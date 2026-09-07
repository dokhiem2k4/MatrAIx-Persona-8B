"""Score one assigned case against what the persona and the assistant did."""

from __future__ import annotations

import re
from typing import Any

_NUMBER = re.compile(r"\d+")
# A capitalised word that is not the first word of a sentence reads as a proper
# noun in Vietnamese, which is how a persona usually leaks a withheld place name.
_PROPER_NOUN = re.compile(r"(?<!^)(?<![.!?]\s)\b[A-ZÀ-Ỹ][a-zà-ỹ]{2,}")


def classify_case_integrity(case: dict[str, Any], first_user_message: str) -> str:
    """Return ``ok`` / ``violated`` / ``not_applicable`` for the input constraint.

    ``not_applicable`` means the case placed no constraint on the persona, so the
    trial can never be invalidated on these grounds.
    """
    constraint = str(case.get("input_constraint") or "none")
    if constraint == "none":
        return "not_applicable"

    said = (first_user_message or "").strip()
    if not said:
        return "violated"

    original = str(case.get("user_input") or "")

    if constraint == "omit_detail":
        added_numbers = set(_NUMBER.findall(said)) - set(_NUMBER.findall(original))
        added_nouns = set(_PROPER_NOUN.findall(said)) - set(_PROPER_NOUN.findall(original))
        return "violated" if (added_numbers or added_nouns) else "ok"

    if constraint == "preserve_invalid_value":
        required = set(_NUMBER.findall(original))
        return "ok" if required <= set(_NUMBER.findall(said)) else "violated"

    return "not_applicable"


DECISION_KEY = "decision"
TOOL_CALLS_KEY = "toolCalls"


def _exposure_value(exposure: Any, key: str) -> Any:
    for field in exposure or ():
        if isinstance(field, dict) and str(field.get("key") or "") == key:
            return field.get("value")
    return None


def observed_decision(exposure: Any) -> tuple[str, str]:
    """Return ``(decision, source)``; source is ``structured`` or ``unavailable``.

    There is deliberately no guessing branch: an assistant reply that carries no
    structured decision is reported as unknown rather than classified by keyword,
    which would silently invent data.
    """
    value = _exposure_value(exposure, DECISION_KEY)
    text = str(value or "").strip()
    return (text, "structured") if text else ("", "unavailable")


def _call_signature(call: Any) -> tuple[str, str]:
    """Identify a tool call by module + key, accepting the ``action`` spelling.

    The golden dataset itself spells two calls with ``action``/``parameters``, so
    the SUT may do the same.
    """
    if not isinstance(call, dict):
        return ("", "")
    module = str(call.get("module") or "").strip()
    key = str(call.get("key") or "").strip() or str(call.get("action") or "").strip()
    return (module, key)


def tool_calls_match(expected: Any, observed: Any) -> bool:
    """Compare tool calls on ``module`` + ``key`` only, ignoring params and order."""
    return {_call_signature(call) for call in expected or ()} == {
        _call_signature(call) for call in observed or ()
    }


def _facet(key: str, label: str, role: str, kind: str, value: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "role": role, "kind": kind, "value": value}


def build_evaluation_payload(
    case_run: dict[str, Any], feedback: dict[str, Any] | None
) -> dict[str, Any]:
    """Build the ``structured_output.json`` payload for one assigned case."""
    case = dict(case_run.get("case") or {})
    observation = dict(case_run.get("observation") or {})
    exposure = observation.get("structured_exposure") or []
    expected = dict(case.get("expected") or {})

    decision, decision_source = observed_decision(exposure)
    if decision_source == "unavailable":
        decision_match = "unknown"
    else:
        decision_match = (
            "match" if decision == str(expected.get("decision") or "") else "mismatch"
        )

    observed_calls = _exposure_value(exposure, TOOL_CALLS_KEY) or []
    if decision_source == "unavailable" and not observed_calls:
        tool_match = "unknown"
    elif tool_calls_match(expected.get("tool_calls"), observed_calls):
        tool_match = "match"
    else:
        tool_match = "mismatch"

    integrity = classify_case_integrity(
        case, str(observation.get("first_user_message") or "")
    )

    contexts: list[dict[str, Any]] = [
        {
            "key": "error_recovery.primary",
            "label": "Error recovery",
            "contextType": "error_recovery",
            "facets": [
                _facet("decision_match", "Khớp quyết định", "primary", "categorical", decision_match),
                _facet("tool_call_match", "Khớp tool call", "primary", "categorical", tool_match),
                _facet("case_integrity", "Toàn vẹn case", "control", "categorical", integrity),
                _facet("decision_source", "Nguồn quyết định", "control", "categorical", decision_source),
                _facet("case_id", "Case", "control", "categorical", str(case.get("case_id") or "")),
                _facet("case_type", "Loại case", "control", "categorical", str(case.get("case_type") or "")),
                _facet("group", "Nhóm", "control", "categorical", str(case.get("group") or "")),
                _facet("error_type", "Nhóm lỗi", "control", "categorical", str(case.get("error_type") or "")),
                _facet("subintent_code", "Subintent", "control", "categorical", str(case.get("subintent_code") or "")),
                _facet("input_constraint", "Ràng buộc đầu vào", "control", "categorical", str(case.get("input_constraint") or "")),
                _facet("expected_decision", "Quyết định kỳ vọng", "evidence", "categorical", str(expected.get("decision") or "")),
                _facet("observed_decision", "Quyết định quan sát", "evidence", "categorical", decision),
                _facet("turn_count", "Số lượt", "metric", "continuous", int(observation.get("turn_count") or 0)),
            ],
        }
    ]

    if feedback is not None:
        rating = feedback.get("overallExperienceRating")
        contexts.append(
            {
                "key": "user_feedback.primary",
                "label": "User feedback",
                "contextType": "user_feedback",
                "facets": [
                    _facet(
                        "overall_experience_rating",
                        "Overall experience rating",
                        "primary",
                        "continuous",
                        int(rating) if isinstance(rating, int) else None,
                    )
                ],
            }
        )

    return {
        "schemaVersion": "1.0",
        "artifactType": "matraix.trial_evaluation",
        "contexts": contexts,
    }
