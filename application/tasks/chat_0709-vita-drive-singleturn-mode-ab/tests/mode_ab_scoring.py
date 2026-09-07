"""Score one assistant-mode A/B trial.

This task has no ground truth: the dataset carries prompts and two experiment
factors, not expected answers. So nothing here judges correctness. It records
the factors, a few deterministic response measures, and the persona's own
verdict, and lets ``reporting.json`` cross-tabulate them.

The one deterministic measure that speaks to the research question is response
length: the question "does proactive mode bother a driver" is partly answerable
from how much the assistant says while ``vehicle_state`` is ``driving``.
"""

from __future__ import annotations

from typing import Any


def profile_applied(case: dict[str, Any], exposure: Any) -> str:
    """Did the deployment actually run the profile this case asked for?

    The whole experiment is worthless if it did not: every cell would hold the
    same default profile and the grid would report that seven personalities are
    indistinguishable, when in truth none of them was ever switched on. So this
    is checked per trial and reported, never assumed.
    """
    wanted = str((case.get("state") or {}).get("assistant_profile_id") or "").strip()
    served = ""
    for field in exposure or ():
        if isinstance(field, dict) and str(field.get("key") or "") == "assistantProfileId":
            served = str(field.get("value") or "").strip()
    if not wanted or not served:
        return "unknown"
    return "yes" if wanted == served else "no"


def reply_length(first_assistant_message: str) -> int:
    """Character count of the assistant's first reply."""
    return len((first_assistant_message or "").strip())


def _facet(key: str, label: str, role: str, kind: str, value: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "role": role, "kind": kind, "value": value}


def _feedback_bucket(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"true", "1"}:
        return "yes"
    if text in {"false", "0"}:
        return "no"
    return text if text in {"yes", "partially", "no"} else "unknown"


def build_evaluation_payload(
    case_run: dict[str, Any], feedback: dict[str, Any] | None
) -> dict[str, Any]:
    """Build ``structured_output.json`` for one mode x vehicle-state cell."""
    case = dict(case_run.get("case") or {})
    observation = dict(case_run.get("observation") or {})
    state = dict(case.get("state") or {})
    reply = str(observation.get("first_assistant_message") or "")

    contexts: list[dict[str, Any]] = [
        {
            "key": "assistant_mode.primary",
            "label": "Assistant mode",
            "contextType": "assistant_mode",
            "facets": [
                _facet("assistant_profile_id", "Profile trợ lý", "primary", "categorical", str(state.get("assistant_profile_id") or "")),
                _facet("vehicle_state", "Trạng thái xe", "primary", "categorical", str(state.get("vehicle_state") or "")),
                _facet("reply_char_count", "Độ dài phản hồi", "metric", "continuous", reply_length(reply)),
                _facet("replied", "Có phản hồi", "control", "categorical", "yes" if reply.strip() else "no"),
                _facet("profile_applied", "Profile có hiệu lực", "control", "categorical", profile_applied(case, observation.get("structured_exposure"))),
                _facet("served_profile", "Profile SUT chạy", "evidence", "categorical", str(next((f.get("value") for f in (observation.get("structured_exposure") or []) if isinstance(f, dict) and f.get("key") == "assistantProfileId"), "") or "")),
                _facet("turn_count", "Số lượt", "metric", "continuous", int(observation.get("turn_count") or 0)),
                _facet("case_id", "Case", "control", "categorical", str(case.get("case_id") or "")),
                _facet("subintent_code", "Subintent", "control", "categorical", str(case.get("subintent_code") or "")),
                _facet("parent_intent_code", "Nhóm intent", "control", "categorical", str(case.get("parent_intent_code") or "")),
                # Every prompt in this dataset is machine-generated and was never
                # human-reviewed; the report must be able to say so.
                _facet("prompt_source", "Nguồn prompt", "control", "categorical", str(case.get("source") or "unknown")),
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
                    ),
                    _facet(
                        "need_constraint_satisfaction",
                        "Need satisfaction",
                        "evidence",
                        "categorical",
                        _feedback_bucket(feedback.get("needConstraintSatisfaction")),
                    ),
                    _facet(
                        "personal_preference_satisfaction",
                        "Preference satisfaction",
                        "evidence",
                        "categorical",
                        _feedback_bucket(feedback.get("personalPreferenceSatisfaction")),
                    ),
                ],
            }
        )

    return {
        "schemaVersion": "1.0",
        "artifactType": "matraix.trial_evaluation",
        "contexts": contexts,
    }
