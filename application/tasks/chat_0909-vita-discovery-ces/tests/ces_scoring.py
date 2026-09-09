"""Score one discovery scenario: what the assistant did, and how it felt.

Two things are measured here, and they answer different questions.

**CES** is the persona's own verdict, four statements copied word for word from
the research instrument. It is subjective by design -- that is the point of an
effort score -- and it is the number that will line up against real
respondents when the team runs the moderated sessions.

**Conversation behaviour** is the objective half. The guide gives columns 16-19
-- continue, choose/confirm, correct/interrupt/cancel, recognise state -- no
scenarios of their own, because a moderator watches for them across every
scenario. This does the same, reading the transcript and the assistant's own
metadata rather than asking anyone.

The task score 0-3 from the guide is deliberately NOT reproduced. It grades the
respondent -- whether a person could work out how to talk to the assistant
without help -- and a language model always can. Scoring it would produce a
column of threes. What replaces it is `outcome_status`, which grades the
assistant instead.
"""

from __future__ import annotations

import re
from typing import Any

TOOL_RESULTS_KEY = "toolResults"

# CES-4 is the safety indicator. The guide is explicit: "Chấm ≤ 4 ở bất kỳ kịch
# bản nào → đánh dấu rủi ro, ghi rõ nguyên nhân."
SAFETY_FLOOR = 4
CES_MAX = 7


def _exposure_value(exposure: Any, key: str) -> Any:
    for field in exposure or ():
        if isinstance(field, dict) and str(field.get("key") or "") == key:
            return field.get("value")
    return None


def _turns(observation: dict[str, Any]) -> list[dict[str, Any]]:
    return [turn for turn in (observation.get("turns") or ()) if isinstance(turn, dict)]


def _exposure_for(turn: dict[str, Any], observation: dict[str, Any], index: int) -> Any:
    """Per-turn exposure, falling back to the trial-level one on turn 1.

    Trials recorded before per-turn exposure existed carry it once, describing
    the anchor turn.
    """
    exposure = turn.get("structured_exposure")
    if not exposure and index == 0:
        return observation.get("structured_exposure") or []
    return exposure or []


# ---------------------------------------------------------------- behaviours

def ran_any_tool(observation: dict[str, Any]) -> bool:
    for index, turn in enumerate(_turns(observation)):
        if _exposure_value(_exposure_for(turn, observation, index), TOOL_RESULTS_KEY):
            return True
    return False


def continued_conversation(observation: dict[str, Any]) -> str:
    """Column 16: did the exchange go past one exchange at all?"""
    replies = [t for t in _turns(observation) if str(t.get("assistant_message") or "").strip()]
    return "yes" if len(replies) >= 2 else "no"


def asked_to_choose_or_confirm(observation: dict[str, Any]) -> str:
    """Column 17: did the assistant put a choice or a confirmation to the driver?

    Read from the typed flags first. The deployment does not raise them
    reliably, so a trailing question with no tool call counts too -- an
    assistant that ran nothing and ended on a question is waiting for an answer.
    """
    for index, turn in enumerate(_turns(observation)):
        exposure = _exposure_for(turn, observation, index)
        if _exposure_value(exposure, "needsConfirmation") is True:
            return "yes"
        if _exposure_value(exposure, "needsFollowUp") is True:
            return "yes"
        reply = str(turn.get("assistant_message") or "").strip().rstrip("\"')]}")
        if reply.endswith("?") and not _exposure_value(exposure, TOOL_RESULTS_KEY):
            return "yes"
    return "no"


# A driver correcting the assistant says so plainly. These are the openings a
# Vietnamese speaker actually uses; matched on the user's turns only.
_CORRECTION = re.compile(
    r"\b(không phải|nhầm|sai rồi|ý (tôi|mình|em|chị|anh|bác) là|đổi lại|"
    r"thôi(,| )|huỷ|hủy|dừng lại|khoan|ấy chết|không|chưa đúng)\b",
    re.IGNORECASE,
)


def corrected_the_assistant(observation: dict[str, Any]) -> str:
    """Column 18: did the driver have to correct, interrupt or cancel?

    Only turns after the first count: the opening line cannot be a correction.
    """
    turns = _turns(observation)
    for turn in turns[1:]:
        if _CORRECTION.search(str(turn.get("user_message") or "")):
            return "yes"
    return "no" if len(turns) > 1 else "not_applicable"


def state_was_legible(observation: dict[str, Any]) -> str:
    """Column 19: could the driver tell what the assistant was doing?

    "Nhận biết trạng thái ... đủ rõ qua Voice + UI, không cần nhìn màn hình
    liên tục." With voice only, the honest proxy is whether the assistant
    reported a turn status at all and whether it said something on every turn.
    """
    turns = _turns(observation)
    if not turns:
        return "not_applicable"
    silent = [t for t in turns if not str(t.get("assistant_message") or "").strip()]
    if silent:
        return "no"
    reported = any(
        _exposure_value(_exposure_for(turn, observation, index), "turnStatus")
        for index, turn in enumerate(turns)
    )
    return "yes" if reported else "unknown"


# ---------------------------------------------------------------- CES

def _score(feedback: dict[str, Any], key: str) -> int | None:
    value = feedback.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if 1 <= value <= CES_MAX else None


def ces_scores(feedback: dict[str, Any]) -> dict[str, int | None]:
    return {
        "ces1_effort": _score(feedback, "ces1Effort"),
        "ces2_information": _score(feedback, "ces2Information"),
        "ces3_presentation": _score(feedback, "ces3Presentation"),
        "ces4_attention": _score(feedback, "ces4Attention"),
    }


def ces_mean(scores: dict[str, int | None]) -> float | None:
    values = [v for v in scores.values() if isinstance(v, int)]
    return round(sum(values) / len(values), 2) if values else None


def safety_flag(feedback: dict[str, Any]) -> str:
    """The guide's own rule, applied verbatim: CES-4 at or below 4 is a risk."""
    value = _score(feedback, "ces4Attention")
    if value is None:
        return "unknown"
    return "at_risk" if value <= SAFETY_FLOOR else "ok"


def low_scored_statements(scores: dict[str, int | None]) -> list[str]:
    """Which statements earned the follow-up question the guide requires."""
    return sorted(key for key, value in scores.items() if isinstance(value, int) and value <= SAFETY_FLOOR)


# Người đọc báo cáo không thuộc mã, nên mọi diễn giải nói bằng lời.
CAPABILITY_MEANING = {
    1: "cá nhân hoá trợ lý",
    2: "hỏi đáp và tra cứu",
    3: "chủ động theo ngữ cảnh",
    4: "dẫn đường và điều hướng",
    5: "sửa chữa và bảo dưỡng",
    6: "an ninh và an toàn",
    7: "điều khiển chức năng trên xe",
    8: "hệ sinh thái Vingroup và mua sắm",
}

STATE_MEANING = {"parked": "xe đang đỗ", "driving": "xe đang chạy"}

COMPLETION_MEANING = {
    "yes": "người lái làm xong việc",
    "partially": "chỉ xong một phần",
    "no": "không xong",
}


def _completion(feedback: dict[str, Any]) -> str:
    text = str(feedback.get("taskCompleted") or "").strip().lower()
    return text if text in COMPLETION_MEANING else "unknown"


def _facet(key: str, label: str, role: str, kind: str, value: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "role": role, "kind": kind, "value": value}


def conversation_path(observation: dict[str, Any]) -> str:
    """The whole exchange, one line per speaker, nothing truncated."""
    turns = _turns(observation) or [
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


def tool_call_report(observation: dict[str, Any]) -> str:
    """Every tool the vehicle ran, per turn, with what it changed and how long."""
    turns = _turns(observation) or [{}]
    lines: list[str] = []
    for index, turn in enumerate(turns, start=1):
        results = _exposure_value(_exposure_for(turn, observation, index - 1), TOOL_RESULTS_KEY) or []
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
                if old == new:
                    continue
                lines.append(
                    "      {}: {} → {}".format(change.get("property") or "?", _short(old), _short(new))
                )
    return "\n".join(lines)


def _short(value: Any) -> str:
    text = "(trống)" if value in (None, "") else str(value)
    return text if len(text) <= 80 else text[:79] + "…"


def _turn_seconds(observation: dict[str, Any]) -> list[float]:
    return [
        float(turn["duration_seconds"])
        for turn in _turns(observation)
        if isinstance(turn.get("duration_seconds"), (int, float))
    ]


def total_latency_seconds(observation: dict[str, Any]) -> float | None:
    values = _turn_seconds(observation)
    if values:
        return round(sum(values), 3)
    single = observation.get("duration_seconds")
    return round(float(single), 3) if isinstance(single, (int, float)) else None


def slowest_turn_seconds(observation: dict[str, Any]) -> float | None:
    values = _turn_seconds(observation)
    if values:
        return round(max(values), 3)
    single = observation.get("duration_seconds")
    return round(float(single), 3) if isinstance(single, (int, float)) else None


def _process_notes(case: dict[str, Any], observation: dict[str, Any]) -> str:
    """One sentence a reviewer can act on, not a row of codes."""
    number = case.get("capability_number")
    return (
        "Năng lực {}: {}. Bối cảnh: {}. Hội thoại đi {} lượt; "
        "người lái phải sửa lại Vita: {}. (mã case {})".format(
            number,
            CAPABILITY_MEANING.get(number, case.get("capability_label_vi") or "không rõ"),
            STATE_MEANING.get(str(case.get("vehicle_state")), case.get("vehicle_state")),
            len(_turns(observation)),
            {"yes": "có", "no": "không", "not_applicable": "chỉ có một lượt"}[
                corrected_the_assistant(observation)
            ],
            case.get("case_id"),
        )
    )


def build_evaluation_payload(
    case_run: dict[str, Any], feedback: dict[str, Any] | None
) -> dict[str, Any]:
    """Build ``structured_output.json`` for one discovery scenario."""
    case = dict(case_run.get("case") or {})
    observation = dict(case_run.get("observation") or {})
    feedback = feedback or {}

    scores = ces_scores(feedback)
    mean = ces_mean(scores)
    completion = _completion(feedback)
    safety = safety_flag(feedback)
    low = low_scored_statements(scores)

    # The assistant is graded on whether the driver got their task done and
    # whether it was safe to use, not on whether the persona spoke well.
    if completion == "no":
        status = "unresolved"
        why = "Người lái không làm xong việc mình định làm."
    elif safety == "at_risk":
        status = "unresolved"
        why = (
            "Người lái chấm câu an toàn {}/7 — ở mức này tài liệu yêu cầu đánh dấu "
            "rủi ro, dù việc có xong hay không.".format(scores["ces4_attention"])
        )
    elif completion == "partially":
        status = "partially_resolved"
        why = "Việc chỉ xong một phần."
    elif completion == "yes":
        status = "resolved"
        why = "Người lái làm xong việc."
    else:
        status = "partially_resolved"
        why = "Người lái không cho biết việc có xong hay không."
    if mean is not None:
        why += " Điểm CES trung bình {}/7.".format(mean)

    contexts: list[dict[str, Any]] = [
        {
            "key": "task_outcome.primary",
            "label": "Task outcome",
            "contextType": "task_outcome",
            "facets": [
                _facet("outcome_status", "Kết quả", "primary", "categorical", status),
                _facet("resolution_basis", "Căn cứ", "control", "categorical", "user_feedback"),
                _facet(
                    "safety_at_risk",
                    "Có rủi ro an toàn",
                    "evidence",
                    "categorical",
                    {"at_risk": "yes", "ok": "no"}.get(safety, "unknown"),
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
                _facet("conversation_path", "Diễn biến", "explanation", "textual", conversation_path(observation)),
                _facet(
                    "expected_behavior",
                    "Tình huống được giao",
                    "explanation",
                    "textual",
                    "{}\nTiêu chí trong tài liệu: {}".format(
                        case.get("scenario_vi") or "", case.get("success_criteria_vi") or ""
                    ).strip(),
                ),
                _facet("process_notes", "Ghi chú chấm", "explanation", "textual", _process_notes(case, observation)),
            ],
        },
        {
            "key": "ces.primary",
            "label": "CES",
            "contextType": "customer_effort",
            "facets": [
                _facet("ces1_effort", "CES-1 Dễ xử lý", "primary", "continuous", scores["ces1_effort"]),
                _facet("ces2_information", "CES-2 Đủ thông tin để quyết", "primary", "continuous", scores["ces2_information"]),
                # Voice only: no screen was shown, so this is the audio
                # experience. Flagged so a report never compares it straight to
                # a human respondent who could see the display.
                _facet("ces3_presentation", "CES-3 Cách trình bày hợp lúc lái", "primary", "continuous", scores["ces3_presentation"]),
                _facet("ces3_basis", "Cơ sở chấm CES-3", "control", "categorical", "audio_only"),
                _facet("ces4_attention", "CES-4 Vẫn tập trung lái", "primary", "continuous", scores["ces4_attention"]),
                _facet("ces_mean", "CES trung bình", "metric", "continuous", mean),
                _facet("low_scored_statements", "Câu bị chấm thấp", "evidence", "textual", ", ".join(low)),
            ],
        },
        {
            "key": "capability_coverage.primary",
            "label": "Capability coverage",
            "contextType": "capability_coverage",
            "facets": [
                _facet("capability_code", "Nhóm năng lực", "primary", "categorical", str(case.get("capability_code") or "")),
                _facet("capability_number", "Số nhóm năng lực", "control", "continuous", case.get("capability_number")),
                _facet("vehicle_state", "Trạng thái xe", "primary", "categorical", str(case.get("vehicle_state") or "")),
                _facet("task_completed", "Việc có xong không", "evidence", "categorical", completion),
                _facet("continued_conversation", "Hội thoại đi tiếp được", "evidence", "categorical", continued_conversation(observation)),
                _facet("asked_to_choose_or_confirm", "Có bước chọn/xác nhận", "evidence", "categorical", asked_to_choose_or_confirm(observation)),
                _facet("driver_had_to_correct", "Người lái phải sửa lại", "evidence", "categorical", corrected_the_assistant(observation)),
                _facet("state_legible", "Biết Vita đang làm gì", "evidence", "categorical", state_was_legible(observation)),
                _facet("ran_any_tool", "Có đụng vào xe", "evidence", "categorical", "yes" if ran_any_tool(observation) else "no"),
                _facet("tool_call_report", "Chi tiết công cụ đã gọi", "evidence", "textual", tool_call_report(observation)),
                _facet("response_latency_seconds", "Tổng thời gian chờ (giây)", "metric", "continuous", total_latency_seconds(observation)),
                _facet("slowest_turn_seconds", "Lượt chờ lâu nhất (giây)", "metric", "continuous", slowest_turn_seconds(observation)),
                _facet("case_id", "Case", "control", "categorical", str(case.get("case_id") or "")),
            ],
        },
    ]

    if feedback:
        contexts.append(
            {
                "key": "user_feedback.primary",
                "label": "User feedback",
                "contextType": "user_feedback",
                "facets": [
                    _facet("overall_experience_rating", "Điểm trải nghiệm", "primary", "continuous", mean),
                    _facet("need_constraint_satisfaction", "Đáp ứng nhu cầu", "evidence", "categorical", completion),
                    _facet("feedback_reason", "Lý do chấm điểm", "explanation", "textual", str(feedback.get("ces1Reason") or "")),
                    _facet("ces2_notes", "Vì sao chấm CES-2", "explanation", "textual", str(feedback.get("ces2Reason") or "")),
                    _facet("ces3_notes", "Vì sao chấm CES-3", "explanation", "textual", str(feedback.get("ces3Reason") or "")),
                    _facet("clarifying_notes", "Vì sao chấm CES-4 (an toàn)", "explanation", "textual", str(feedback.get("ces4Reason") or "")),
                    _facet("task_completed_notes", "Việc xong tới đâu", "explanation", "textual", str(feedback.get("taskCompletedNotes") or "")),
                ],
            }
        )

    return {"schemaVersion": "1.0", "artifactType": "matraix.trial_evaluation", "contexts": contexts}
