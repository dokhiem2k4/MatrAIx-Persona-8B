"""Score one assigned case against what the persona and the assistant did."""

from __future__ import annotations

import re
from typing import Any

from tool_mapping import map_expected_tools

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
TOOL_RESULTS_KEY = "toolResults"


def _exposure_value(exposure: Any, key: str) -> Any:
    for field in exposure or ():
        if isinstance(field, dict) and str(field.get("key") or "") == key:
            return field.get("value")
    return None


def observed_decision(exposure: Any) -> tuple[str, str]:
    """Return ``(decision, source)`` when the SUT names the decision itself.

    Kept for deployments that expose a ``decision`` field. The VoiceLab
    deployment does not, so this falls through to ``decision_from_signals``.
    """
    value = _exposure_value(exposure, DECISION_KEY)
    text = str(value or "").strip()
    return (text, "structured") if text else ("", "unavailable")


def observed_tool_names(exposure: Any) -> list[str]:
    """Tool names the vehicle actually ran, from ``vehicle.results``."""
    results = _exposure_value(exposure, TOOL_RESULTS_KEY) or []
    names = {
        str(r.get("tool") or "").strip()
        for r in results
        if isinstance(r, dict) and str(r.get("tool") or "").strip()
    }
    return sorted(names)


def decision_from_signals(exposure: Any) -> tuple[str, str]:
    """Derive the decision class from the deployment's metadata signals.

    Source is ``derived``, never ``structured``: these are typed signals the
    assistant emits about its own turn, but the mapping to the dataset's five
    classes is this file's judgement, not the deployment's.

    Two classes are deliberately NOT derived. A plain conversational answer and
    a refusal both surface as a completed turn with no tool and no flag, so
    picking one would invent data; those stay ``unknown``.
    """
    if not exposure:
        return ("", "unavailable")

    def flag(key: str) -> bool:
        return _exposure_value(exposure, key) is True

    # Order matters: a turn can raise several flags, and a missing precondition
    # is the more specific, more actionable answer than a generic clarification.
    if flag("needsPermission"):
        return ("guide_precondition", "derived")
    if flag("needsFollowUp") or flag("needsConfirmation"):
        return ("clarify_or_offer", "derived")

    results = _exposure_value(exposure, TOOL_RESULTS_KEY) or []
    if results:
        failed = any(isinstance(r, dict) and r.get("success") is False for r in results)
        return ("defer_retry" if failed else "execute", "derived")

    return ("", "unknown")


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


def _feedback_bucket(value: Any) -> str:
    """Normalise a yes/partially/no answer, however the persona spelled it."""
    text = str(value).strip().lower()
    if text in {"true", "1"}:
        return "yes"
    if text in {"false", "0"}:
        return "no"
    return text if text in {"yes", "partially", "no"} else "unknown"


def self_report_facets(feedback: dict[str, Any]) -> list[dict[str, Any]]:
    """Every field the persona wrote, not just the score.

    The score alone says a trial went badly; the persona's own reasons say why,
    and those sentences are the part a human actually reads. Dropping them here
    means they exist only inside one JSON file per trial, where nobody looks.
    """
    rating = feedback.get("overallExperienceRating")
    return [
        _facet(
            "overall_experience_rating",
            "Điểm trải nghiệm",
            "primary",
            "continuous",
            int(rating) if isinstance(rating, int) else None,
        ),
        _facet(
            "need_constraint_satisfaction",
            "Đáp ứng nhu cầu",
            "evidence",
            "categorical",
            _feedback_bucket(feedback.get("needConstraintSatisfaction")),
        ),
        _facet(
            "personal_preference_satisfaction",
            "Hợp sở thích",
            "evidence",
            "categorical",
            _feedback_bucket(feedback.get("personalPreferenceSatisfaction")),
        ),
        _facet(
            "asked_useful_clarification",
            "Có hỏi lại hữu ích",
            "evidence",
            "categorical",
            _feedback_bucket(feedback.get("askedUsefulClarificationQuestions")),
        ),
        _facet(
            "feedback_reason",
            "Lý do chấm điểm",
            "explanation",
            "textual",
            str(feedback.get("reason") or ""),
        ),
        _facet(
            "clarifying_notes",
            "Ghi chú về việc hỏi lại",
            "explanation",
            "textual",
            str(feedback.get("clarifyingNotes") or ""),
        ),
    ]


def build_evaluation_payload(
    case_run: dict[str, Any], feedback: dict[str, Any] | None
) -> dict[str, Any]:
    """Build the ``structured_output.json`` payload for one assigned case."""
    case = dict(case_run.get("case") or {})
    observation = dict(case_run.get("observation") or {})
    exposure = observation.get("structured_exposure") or []
    expected = dict(case.get("expected") or {})

    # Prefer a decision the SUT names itself; fall back to deriving one from its
    # metadata signals. Both paths label their source so a report can say how
    # much of the number is inference.
    decision, decision_source = observed_decision(exposure)
    if decision_source != "structured":
        decision, decision_source = decision_from_signals(exposure)
    if decision_source in ("unavailable", "unknown"):
        decision_match = decision_source
    else:
        decision_match = (
            "match" if decision == str(expected.get("decision") or "") else "mismatch"
        )

    # The deployment reports the tools it ran by name only, under a naming
    # scheme the golden dataset does not share. Cases that expect NO tool are
    # still checkable exactly -- and that is 301 of the 364.
    observed_tools = observed_tool_names(exposure)
    expected_calls = expected.get("tool_calls") or []
    wanted, no_equivalent, unmapped = map_expected_tools(expected_calls)
    if not exposure:
        tool_match = "unavailable"
    elif not expected_calls:
        # 306 of the 364 cases land here, and they are exact: the assistant
        # either touched the vehicle when it should not have, or it did not.
        tool_match = "match" if not observed_tools else "mismatch"
    elif unmapped:
        tool_match = "unmapped"
    elif no_equivalent:
        # The dataset expects a capability this deployment does not ship. No
        # assistant could pass, so this is a product gap, not a wrong answer.
        tool_match = "no_equivalent"
    else:
        tool_match = "match" if wanted == set(observed_tools) else "mismatch"

    integrity = classify_case_integrity(
        case, str(observation.get("first_user_message") or "")
    )

    # The chat debrief view renders three context types by name --
    # task_outcome, conversation_summary and user_feedback -- and ignores any
    # it does not know. Emitting only error_recovery left that panel showing a
    # single raw FAIL string while all fifteen facets sat unread in the file.
    if decision_match == "match" and tool_match == "match":
        outcome_status, outcome_reason = "resolved", "Quyết định và tool call đều khớp kỳ vọng."
    elif decision_match in ("unknown", "unavailable"):
        outcome_status = "partially_resolved"
        outcome_reason = "Không suy được quyết định từ tín hiệu SUT trả về ({}).".format(decision_source)
    else:
        outcome_status = "unresolved"
        outcome_reason = "Kỳ vọng {!r} nhưng quan sát {!r}; tool {}.".format(
            expected.get("decision"), decision or "(không có)", tool_match
        )
    if integrity == "violated":
        outcome_status = "unresolved"
        outcome_reason = (
            "Persona phá ràng buộc đầu vào ({}), nên trial này không đo được SUT. "
        ).format(case.get("input_constraint")) + outcome_reason

    contexts: list[dict[str, Any]] = [
        {
            "key": "task_outcome.primary",
            "label": "Task outcome",
            "contextType": "task_outcome",
            "facets": [
                _facet("outcome_status", "Kết quả", "primary", "categorical", outcome_status),
                _facet("resolution_basis", "Căn cứ", "control", "categorical", "verifier_scoring"),
                _facet("outcome_reason", "Diễn giải", "explanation", "textual", outcome_reason),
            ],
        },
        {
            "key": "conversation_summary.primary",
            "label": "Conversation",
            "contextType": "conversation_summary",
            "facets": [
                _facet("message_count", "Số lượt", "metric", "continuous", int(observation.get("turn_count") or 0)),
                _facet(
                    "conversation_path",
                    "Diễn biến",
                    "explanation",
                    "textual",
                    "Persona: {}\nVita: {}".format(
                        str(observation.get("first_user_message") or "")[:400],
                        str(observation.get("first_assistant_message") or "")[:400],
                    ),
                ),
                _facet(
                    "process_notes",
                    "Ghi chú chấm",
                    "explanation",
                    "textual",
                    "Case {} · {} · ràng buộc {} · toàn vẹn {} · tool đã chạy [{}]".format(
                        case.get("case_id"), case.get("error_type"),
                        case.get("input_constraint"), integrity,
                        ", ".join(observed_tools) or "không có",
                    ),
                ),
            ],
        },
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
                _facet("observed_tools", "Tool đã chạy", "evidence", "textual", ", ".join(observed_tools)),
                _facet("sut_intent", "Intent SUT nhận", "evidence", "categorical", str(_exposure_value(exposure, "intent") or "")),
                _facet("turn_count", "Số lượt", "metric", "continuous", int(observation.get("turn_count") or 0)),
            ],
        }
    ]

    if feedback is not None:
        contexts.append(
            {
                "key": "user_feedback.primary",
                "label": "User feedback",
                "contextType": "user_feedback",
                "facets": self_report_facets(feedback),
            }
        )

    return {
        "schemaVersion": "1.0",
        "artifactType": "matraix.trial_evaluation",
        "contexts": contexts,
    }
