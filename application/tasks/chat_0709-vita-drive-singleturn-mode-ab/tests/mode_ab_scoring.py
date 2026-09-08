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


TOOL_RESULTS_KEY = "toolResults"


def _exposure_value(exposure: Any, key: str) -> Any:
    for field in exposure or ():
        if isinstance(field, dict) and str(field.get("key") or "") == key:
            return field.get("value")
    return None


def _short(value: Any) -> str:
    text = "(trống)" if value in (None, "") else str(value)
    return text if len(text) <= 80 else text[:79] + "…"


def tool_call_report(observation: dict[str, Any]) -> str:
    """Every tool the vehicle ran, per turn, with what it changed and how long.

    A list of tool names answers "did it touch the car" and nothing else. The
    arguments a call actually landed live in the property changes the
    deployment reports, and those are what a reviewer needs.
    """
    turns = [turn for turn in (observation.get("turns") or ()) if isinstance(turn, dict)]
    if not turns:
        turns = [{}]
    # Trials recorded before per-turn exposure existed carry it once, at the top
    # of the observation, describing the anchor turn. Falling back to it keeps
    # those runs readable instead of reporting "no tools" for all of them.
    anchor_exposure = observation.get("structured_exposure") or []
    lines: list[str] = []
    for index, turn in enumerate(turns, start=1):
        exposure = turn.get("structured_exposure")
        if not exposure and index == 1:
            exposure = anchor_exposure
        results = _exposure_value(exposure, TOOL_RESULTS_KEY) or []
        seconds = turn.get("duration_seconds")
        timing = " · Vita trả lời sau {:.2f}s".format(seconds) if isinstance(seconds, (int, float)) else ""
        if not results:
            lines.append("Lượt {}: không gọi công cụ nào{}".format(index, timing))
            continue
        lines.append("Lượt {}: gọi {} công cụ{}".format(index, len(results), timing))
        for result in results:
            if not isinstance(result, dict):
                continue
            ok = result.get("success")
            verdict = "chạy được" if ok is True else ("LỖI" if ok is False else "không rõ kết quả")
            lines.append("  • {} — {}".format(str(result.get("tool") or "?"), verdict))
            for change in result.get("changes") or ():
                if not isinstance(change, dict):
                    continue
                old, new = change.get("oldValue"), change.get("newValue")
                # Unchanged properties are noise: the deployment reports every
                # field the tool touched, whether or not it moved.
                if old == new:
                    continue
                lines.append(
                    "      {}: {} → {}".format(
                        change.get("property") or "?", _short(old), _short(new)
                    )
                )
    return "\n".join(lines)


def _turn_seconds(observation: dict[str, Any]) -> list[float]:
    turns = [turn for turn in (observation.get("turns") or ()) if isinstance(turn, dict)]
    return [
        float(turn["duration_seconds"])
        for turn in turns
        if isinstance(turn.get("duration_seconds"), (int, float))
    ]


def total_latency_seconds(observation: dict[str, Any]) -> float | None:
    """Seconds the driver spent waiting on the assistant across the trial."""
    values = _turn_seconds(observation)
    if values:
        return round(sum(values), 3)
    single = observation.get("duration_seconds")
    return round(float(single), 3) if isinstance(single, (int, float)) else None


def slowest_turn_seconds(observation: dict[str, Any]) -> float | None:
    """The worst single wait. An average hides the one turn that took 30s."""
    values = _turn_seconds(observation)
    if values:
        return round(max(values), 3)
    single = observation.get("duration_seconds")
    return round(float(single), 3) if isinstance(single, (int, float)) else None


def conversation_path(observation: dict[str, Any]) -> str:
    """The whole exchange, one line per speaker, nothing truncated.

    The debrief renders this verbatim, so a reviewer can read what was actually
    said instead of scrolling to the transcript and back.
    """
    turns = [turn for turn in (observation.get("turns") or ()) if isinstance(turn, dict)]
    if not turns:
        turns = [
            {
                "user_message": observation.get("first_user_message") or "",
                "assistant_message": observation.get("first_assistant_message") or "",
            }
        ]
    lines: list[str] = []
    for index, turn in enumerate(turns, start=1):
        said = str(turn.get("user_message") or "").strip()
        replied = str(turn.get("assistant_message") or "").strip()
        if said:
            lines.append("Lượt {} · Người lái: {}".format(index, said))
        if replied:
            lines.append("Lượt {} · Vita: {}".format(index, replied))
    return "\n".join(lines)


# Người đọc báo cáo không thuộc các mã này, nên mọi diễn giải nói bằng lời.
PROFILE_MEANING = {
    "vita_default": "tính cách mặc định",
    "vita_proactive": "chủ động gợi ý trước",
    "vita_concise": "trả lời ngắn gọn",
    "vita_friendly": "thân thiện, nhiều lời",
    "vita_professional": "trang trọng, nghiêm túc",
    "vita_humorous": "hài hước",
    "vita_calm": "điềm tĩnh",
}

VEHICLE_STATE_MEANING = {
    "driving": "xe đang chạy",
    "parked": "xe đang đỗ",
    "charging": "xe đang sạc",
    "idle": "xe nổ máy nhưng đứng yên",
}

APPLIED_MEANING = {
    "yes": "đúng profile được yêu cầu",
    "no": "SAI profile — ô lưới này không đo được gì",
    "unknown": "không kiểm được vì SUT không báo profile nào đang chạy",
}


def _describe(table: dict[str, str], code: Any) -> str:
    text = str(code or "").strip()
    return "{} ({})".format(table.get(text, text or "không rõ"), text) if text else "không rõ"


def _process_notes(state: dict[str, Any], reply: str, applied: str) -> str:
    """One sentence a reviewer can act on, not a row of codes."""
    return (
        "Ô lưới này ghép {} với {}. Profile chạy thực tế: {}. "
        "Vita trả lời {} ký tự.".format(
            _describe(PROFILE_MEANING, state.get("assistant_profile_id")),
            _describe(VEHICLE_STATE_MEANING, state.get("vehicle_state")),
            APPLIED_MEANING.get(applied, applied),
            reply_length(reply),
        )
    )


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
        # A bare "partially" says the assistant half worked and nothing about
        # which half. These are the persona's own words on that.
        _facet(
            "need_satisfaction_notes",
            "Đáp ứng nhu cầu — chi tiết",
            "explanation",
            "textual",
            str(feedback.get("needNotes") or ""),
        ),
        _facet(
            "preference_satisfaction_notes",
            "Hợp sở thích — chi tiết",
            "explanation",
            "textual",
            str(feedback.get("preferenceNotes") or ""),
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
        status, why = "resolved", (
            "Đã thu được phản hồi khi Vita chạy {} và {}. Ô lưới này đo được; "
            "nó chỉ ghi lại hành vi, không chấm đúng sai — bộ dữ liệu A/B không "
            "có đáp án đúng.".format(
                _describe(PROFILE_MEANING, state.get("assistant_profile_id")),
                _describe(VEHICLE_STATE_MEANING, state.get("vehicle_state")),
            )
        )

    contexts: list[dict[str, Any]] = [
        {
            "key": "task_outcome.primary",
            "label": "Task outcome",
            "contextType": "task_outcome",
            "facets": [
                _facet("outcome_status", "Kết quả", "primary", "categorical", status),
                _facet("resolution_basis", "Căn cứ", "control", "categorical", "verifier_scoring"),
                # yes/no, because the job report's headline panel only colours
                # words it recognises -- and whether the profile actually
                # switched is the one number that decides if this A/B grid
                # measured anything at all.
                _facet(
                    "profile_switched",
                    "Profile có đổi thật không",
                    "evidence",
                    "categorical",
                    applied,
                ),
                _facet(
                    "assistant_replied",
                    "Trợ lý có trả lời",
                    "evidence",
                    "categorical",
                    "yes" if reply.strip() else "no",
                ),
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
                       conversation_path(observation)),
                _facet("process_notes", "Ghi chú chấm", "explanation", "textual",
                       _process_notes(state, reply, applied)),
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
                _facet(
                    "tool_call_report",
                    "Chi tiết công cụ đã gọi",
                    "evidence",
                    "textual",
                    tool_call_report(observation),
                ),
                _facet(
                    "response_latency_seconds",
                    "Tổng thời gian chờ (giây)",
                    "metric",
                    "continuous",
                    total_latency_seconds(observation),
                ),
                _facet(
                    "slowest_turn_seconds",
                    "Lượt chờ lâu nhất (giây)",
                    "metric",
                    "continuous",
                    slowest_turn_seconds(observation),
                ),
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
