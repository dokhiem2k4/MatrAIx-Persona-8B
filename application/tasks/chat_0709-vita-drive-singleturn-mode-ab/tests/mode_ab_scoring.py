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
    """Build ``structured_output.json`` for one mode x vehicle-state cell."""
    case = dict(case_run.get("case") or {})
    observation = dict(case_run.get("observation") or {})
    state = dict(case.get("state") or {})
    reply = str(observation.get("first_assistant_message") or "")

    applied = profile_applied(case, observation.get("structured_exposure"))
    if applied == "no":
        status, why = "unresolved", (
            "SUT chạy profile {!r} thay vì {!r} được yêu cầu, nên ô lưới này không "
            "đo được yếu tố cần đo.".format(
                str(next((f.get("value") for f in (observation.get("structured_exposure") or [])
                          if isinstance(f, dict) and f.get("key") == "assistantProfileId"), "") or "?"),
                str(state.get("assistant_profile_id") or "?"),
            )
        )
    elif not reply.strip():
        status, why = "unresolved", "Trợ lý không trả lời."
    else:
        status, why = "resolved", "Đã thu được phản hồi dưới profile {!r}, trạng thái xe {!r}.".format(
            str(state.get("assistant_profile_id") or ""), str(state.get("vehicle_state") or "")
        )

    contexts: list[dict[str, Any]] = [
        {
            "key": "task_outcome.primary",
            "label": "Task outcome",
            "contextType": "task_outcome",
            "facets": [
                _facet("outcome_status", "Kết quả", "primary", "categorical", status),
                _facet("resolution_basis", "Căn cứ", "control", "categorical", "verifier_scoring"),
                _facet("outcome_reason", "Diễn giải", "explanation", "textual", why),
            ],
        },
        {
            "key": "conversation_summary.primary",
            "label": "Conversation",
            "contextType": "conversation_summary",
            "facets": [
                _facet("message_count", "Số lượt", "metric", "continuous", int(observation.get("turn_count") or 0)),
                _facet("conversation_path", "Diễn biến", "explanation", "textual",
                       "Persona: {}\nVita: {}".format(
                           str(observation.get("first_user_message") or "")[:400], reply[:400])),
                _facet("process_notes", "Ghi chú chấm", "explanation", "textual",
                       "Profile {} · xe {} · {} ký tự phản hồi · profile có hiệu lực: {}".format(
                           state.get("assistant_profile_id"), state.get("vehicle_state"),
                           reply_length(reply), applied)),
            ],
        },
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
