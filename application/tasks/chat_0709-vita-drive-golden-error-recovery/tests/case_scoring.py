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


# Người đọc báo cáo không thuộc năm mã này, nên mọi diễn giải nói bằng lời.
DECISION_MEANING = {
    "execute": "thực hiện yêu cầu",
    "clarify_or_offer": "hỏi lại cho rõ trước khi làm",
    "defer_retry": "báo chưa làm được và hẹn thử lại",
    "guide_precondition": "hướng dẫn điều kiện cần làm trước",
    "refuse_not_supported": "từ chối vì ngoài khả năng",
}

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


ERROR_TYPE_MEANING = {
    "happy_case": "tình huống thuận lợi, không có lỗi nào",
    "missing_information": "người dùng nói thiếu thông tin",
    "invalid_input": "người dùng đưa giá trị sai",
    "bad_request": "tham số không hợp lệ",
    "no_internet": "xe mất kết nối mạng",
    "external_api_failure": "dịch vụ bên ngoài không phản hồi",
    "resource_not_found": "không tìm thấy thứ người dùng hỏi",
    "vehicle_state_unavailable": "cảm biến trên xe không đọc được",
    "ambiguous_destination": "điểm đến mơ hồ, có nhiều lựa chọn",
    "unsafe_command": "lệnh không an toàn khi đang lái",
}

CONSTRAINT_MEANING = {
    "omit_detail": "người dùng cố tình nói thiếu chi tiết",
    "preserve_invalid_value": "người dùng giữ nguyên một giá trị sai",
}

INTEGRITY_MEANING = {
    "ok": "persona giữ đúng ràng buộc",
    "violated": "persona phá ràng buộc, nên trial này không đo được Vita",
    "not_applicable": "case này không đặt ràng buộc nào",
}


def _process_notes(case: dict[str, Any], integrity: str, observed_tools: list[str]) -> str:
    """One sentence a reviewer can act on, not a row of codes."""
    error_type = str(case.get("error_type") or "")
    constraint = str(case.get("input_constraint") or "none")
    bits = [
        "Tình huống: {}.".format(ERROR_TYPE_MEANING.get(error_type, error_type)),
    ]
    if constraint in CONSTRAINT_MEANING:
        bits.append("Ràng buộc: {}.".format(CONSTRAINT_MEANING[constraint]))
    bits.append("Kiểm tra persona: {}.".format(INTEGRITY_MEANING.get(integrity, integrity)))
    bits.append(
        "Vita gọi công cụ: {}.".format(", ".join(observed_tools) if observed_tools else "không gọi gì")
    )
    bits.append("(mã case {})".format(case.get("case_id")))
    return " ".join(bits)


def tool_call_report(observation: dict[str, Any]) -> str:
    """Every tool the vehicle ran, per turn, with what it changed and how long.

    ``observed_tools`` is a list of names, which answers "did it touch the car"
    and nothing else. A reviewer asking why a route came out 1,500 km long needs
    the arguments the call actually landed -- and those are in the property
    changes the deployment reports, not in the name.
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
            name = str(result.get("tool") or "?")
            ok = result.get("success")
            verdict = "chạy được" if ok is True else ("LỖI" if ok is False else "không rõ kết quả")
            lines.append("  • {} — {}".format(name, verdict))
            for change in result.get("changes") or ():
                if not isinstance(change, dict):
                    continue
                old = change.get("oldValue")
                new = change.get("newValue")
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


def _short(value: Any) -> str:
    text = "(trống)" if value in (None, "") else str(value)
    return text if len(text) <= 80 else text[:79] + "…"


def total_latency_seconds(observation: dict[str, Any]) -> float | None:
    """Seconds the driver spent waiting on the assistant across the trial."""
    turns = [turn for turn in (observation.get("turns") or ()) if isinstance(turn, dict)]
    values = [
        turn.get("duration_seconds")
        for turn in turns
        if isinstance(turn.get("duration_seconds"), (int, float))
    ]
    if not values:
        single = observation.get("duration_seconds")
        return round(float(single), 3) if isinstance(single, (int, float)) else None
    return round(float(sum(values)), 3)


def slowest_turn_seconds(observation: dict[str, Any]) -> float | None:
    """The worst single wait. An average hides the one turn that took 30s."""
    turns = [turn for turn in (observation.get("turns") or ()) if isinstance(turn, dict)]
    values = [
        turn.get("duration_seconds")
        for turn in turns
        if isinstance(turn.get("duration_seconds"), (int, float))
    ]
    if values:
        return round(float(max(values)), 3)
    single = observation.get("duration_seconds")
    return round(float(single), 3) if isinstance(single, (int, float)) else None


def conversation_path(observation: dict[str, Any]) -> str:
    """The whole exchange, one line per speaker, nothing truncated.

    The debrief renders this verbatim, so a reviewer judging whether Vita
    answered the question can read what was actually said instead of scrolling
    to the transcript and back. Only the anchor turn used to be here, which is
    fine for a one-turn case and useless the moment a case runs longer.
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


def expected_behavior(case: dict[str, Any], wanted_tools: set[str]) -> str:
    """What the dataset says a correct assistant would have done, in words.

    Without this the panel shows only what happened, and a reader has to open
    cases.jsonl to learn what was supposed to happen -- which is the one thing
    they need in order to judge the verdict.
    """
    expected = dict(case.get("expected") or {})
    decision = str(expected.get("decision") or "")
    bits = [
        "Bộ dữ liệu kỳ vọng Vita {}.".format(
            DECISION_MEANING.get(decision, decision or "không nêu rõ")
        )
    ]
    if wanted_tools:
        bits.append("Kèm theo là gọi công cụ: {}.".format(", ".join(sorted(wanted_tools))))
    elif expected.get("tool_calls"):
        bits.append(
            "Bộ dữ liệu kỳ vọng một công cụ mà bản triển khai này không có tương đương."
        )
    else:
        bits.append("Và không được đụng vào xe ở lượt này.")
    original = str(case.get("user_input") or "").strip()
    if original:
        bits.append("Câu gốc trong bộ dữ liệu: “{}”.".format(original))
    return " ".join(bits)


def clarification_count(observation: dict[str, Any]) -> int:
    """How many times the assistant asked the driver something back.

    Counted from the text rather than a flag, because the deployment only raises
    ``needsFollowUp`` on some of the turns where it actually asks. The debrief
    header shows this beside the turn count; without it the header read
    "1 messages · - clarifications", which says nothing.
    """
    turns = observation.get("turns") or []
    replies = [str(turn.get("assistant_message") or "") for turn in turns]
    if not replies:
        replies = [str(observation.get("first_assistant_message") or "")]
    return sum(1 for reply in replies if "?" in reply)


def _facet(key: str, label: str, role: str, kind: str, value: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "role": role, "kind": kind, "value": value}


def _as_yes_no(match: str) -> str:
    """Restate a match verdict as yes / no / unknown.

    The job report's headline panel only reads contexts every chatbot task has
    -- task_outcome, conversation_summary, user_feedback -- and only colours a
    categorical facet whose values are words it recognises as good or bad.
    ``match`` / ``mismatch`` are neither, so the two numbers that decide whether
    this whole task passed were being reported nowhere a reader looks first.
    The diagnostic spelling stays in the error_recovery context below.
    """
    if match == "match":
        return "yes"
    if match == "mismatch":
        return "no"
    return "unknown"


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
    want = str(expected.get("decision") or "")
    if decision_match == "match" and tool_match == "match":
        outcome_status = "resolved"
        outcome_reason = "Vita xử lý đúng: {}. Công cụ gọi ra cũng khớp.".format(
            DECISION_MEANING.get(want, want)
        )
    elif decision_match in ("unknown", "unavailable"):
        outcome_status = "partially_resolved"
        outcome_reason = (
            "Chưa kết luận được. Vita có trả lời, nhưng tín hiệu nó gửi kèm không đủ "
            "để biết nó đã quyết định thế nào, nên không so được với kỳ vọng "
            "\u201c{}\u201d.".format(DECISION_MEANING.get(want, want))
        )
    else:
        parts = []
        if decision_match == "mismatch":
            parts.append(
                "Đáng lẽ Vita phải {}, nhưng nó lại {}.".format(
                    DECISION_MEANING.get(want, want),
                    DECISION_MEANING.get(decision, decision or "không làm gì rõ ràng"),
                )
            )
        if tool_match == "mismatch":
            parts.append(
                "Công cụ nó gọi cũng không khớp: {}.".format(
                    ", ".join(observed_tools) if observed_tools else "không gọi công cụ nào"
                )
            )
        elif tool_match == "no_equivalent":
            parts.append(
                "Bộ dữ liệu kỳ vọng một năng lực mà bản triển khai này không có, "
                "nên không trợ lý nào qua được case này."
            )
        elif tool_match == "unmapped":
            parts.append("Tên công cụ trong bộ dữ liệu chưa ánh xạ sang tên thật của xe.")
        outcome_status = "unresolved"
        outcome_reason = " ".join(parts) or "Không khớp kỳ vọng."
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
                _facet(
                    "decision_correct",
                    "Quyết định đúng chưa",
                    "evidence",
                    "categorical",
                    _as_yes_no(decision_match),
                ),
                _facet(
                    "tool_calls_correct",
                    "Gọi đúng công cụ chưa",
                    "evidence",
                    "categorical",
                    _as_yes_no(tool_match),
                ),
                _facet(
                    "case_integrity_ok",
                    "Persona giữ đúng ràng buộc",
                    "evidence",
                    "categorical",
                    {"ok": "yes", "violated": "no"}.get(integrity, "not_applicable"),
                ),
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
                    "clarification_question_count",
                    "Số lần hỏi lại",
                    "metric",
                    "continuous",
                    clarification_count(observation),
                ),
                _facet(
                    "conversation_path",
                    "Diễn biến",
                    "explanation",
                    "textual",
                    conversation_path(observation),
                ),
                _facet(
                    "expected_behavior",
                    "Lẽ ra Vita phải làm gì",
                    "explanation",
                    "textual",
                    expected_behavior(case, wanted),
                ),
                _facet(
                    "process_notes",
                    "Ghi chú chấm",
                    "explanation",
                    "textual",
                    _process_notes(case, integrity, observed_tools),
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
