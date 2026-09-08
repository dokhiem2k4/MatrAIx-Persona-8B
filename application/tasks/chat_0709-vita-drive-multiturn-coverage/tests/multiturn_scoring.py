"""Score one multi-turn coverage trial.

This task has no ground truth. The workbook's assistant turns are one sample
answer, not a specification, so nothing here compares against them.

``lexical_topic_overlap`` is a **lexical proxy**, not a judgment about context
retention: it only asks whether a later assistant reply reuses a content word
the persona introduced in its opening message. A model can carry context
perfectly while paraphrasing every word, and can echo a word while losing the
thread entirely. Read it as a cheap smoke signal, never as a score.
"""

from __future__ import annotations

import re
from typing import Any

_WORD = re.compile(r"[0-9A-Za-zÀ-ỹ]+", re.UNICODE)
MIN_CONTENT_WORD_LEN = 2

# Vietnamese is monosyllabic: filtering by length alone would throw away most
# meaningful words ("xe", "pin", "sạc", "phê"). Filter by function word instead.
STOPWORDS = frozenset(
    """
    a ai anh ах bao bay bằng bị bởi các cách cái cần chỉ cho chị chưa chứ có
    còn cùng của cũng do dạ dùng gì giúp gì gồm hay hãy hơn khi không là lại
    lên luôn là mà mình muốn mới nay nào này nên nhé như nhưng những nó nữa ok
    phải qua ra rồi sao sẽ số thì thế trong tôi từ ta và vào vâng về vì với vẫn
    ừ ạ đang đây được đi đó đã đến để em
    """.split()
)


def content_words(text: str) -> set[str]:
    """Lowercased tokens that plausibly carry topic meaning."""
    return {
        word.lower()
        for word in _WORD.findall(text or "")
        if len(word) >= MIN_CONTENT_WORD_LEN and word.lower() not in STOPWORDS
    }


def lexical_topic_overlap(turns: Any) -> str:
    """Return ``carried`` / ``not_carried`` / ``not_applicable``.

    ``not_applicable`` when the conversation never reached a second turn, so
    there was no opportunity to carry anything.
    """
    ordered = [turn for turn in (turns or ()) if isinstance(turn, dict)]
    if len(ordered) < 2:
        return "not_applicable"
    opening = content_words(str(ordered[0].get("user_message") or ""))
    if not opening:
        return "not_applicable"
    for turn in ordered[1:]:
        if opening & content_words(str(turn.get("assistant_message") or "")):
            return "carried"
    return "not_carried"


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


OVERLAP_MEANING = {
    "carried": (
        "có ít nhất một lượt sau dùng lại từ khoá người lái nêu ở đầu, nên nhiều "
        "khả năng trợ lý vẫn bám chủ đề"
    ),
    "not_carried": (
        "không lượt nào dùng lại từ khoá người lái nêu ở đầu — dấu hiệu có thể đã "
        "lạc chủ đề, nhưng cũng có thể chỉ là diễn đạt lại bằng từ khác"
    ),
    "not_applicable": "hội thoại chưa đủ hai lượt nên không đo được",
}

SEED_QUALITY_MEANING = {
    "ok": "seed đạt",
    "too_short": "seed quá ngắn, cần người rà lại",
    "unknown": "chưa đánh giá chất lượng seed",
}


def _process_notes(case: dict[str, Any], assistant_replies: int, overlap: str) -> str:
    """One sentence a reviewer can act on, not a row of codes."""
    return (
        "Chủ đề: {} (nhóm {}). Trợ lý trả lời {} lượt. Bám chủ đề: {}. "
        "Chất lượng seed: {}. (mã case {})".format(
            case.get("subintent_label_vi") or case.get("subintent_code") or "không rõ",
            case.get("parent_intent_code") or "không rõ",
            assistant_replies,
            OVERLAP_MEANING.get(overlap, overlap),
            SEED_QUALITY_MEANING.get(
                str(case.get("seed_quality") or "unknown"), case.get("seed_quality")
            ),
            case.get("case_id"),
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
    """Build ``structured_output.json`` for one conversation seed."""
    case = dict(case_run.get("case") or {})
    observation = dict(case_run.get("observation") or {})
    turns = observation.get("turns") or []
    assistant_replies = sum(
        1 for t in turns if isinstance(t, dict) and str(t.get("assistant_message") or "").strip()
    )

    overlap = lexical_topic_overlap(turns)
    reference_turns = int(case.get("reference_turn_count") or 0)
    if assistant_replies < 2:
        status = "unresolved"
        why = (
            "Trợ lý chỉ trả lời {} lượt, chưa đủ hai lượt để xét việc giữ ngữ cảnh. "
            "Bộ dữ liệu dựng hội thoại này dài khoảng {} lượt.".format(
                assistant_replies, reference_turns or "vài"
            )
        )
    elif overlap == "not_carried":
        status = "partially_resolved"
        why = (
            "Trợ lý trả lời đủ {} lượt, nhưng {}. Task này không có đáp án đúng, "
            "nên đây là dấu hiệu cần người xem lại hội thoại, chưa phải kết luận "
            "trợ lý sai.".format(assistant_replies, OVERLAP_MEANING["not_carried"])
        )
    else:
        status = "resolved"
        why = (
            "Hội thoại đi hết {} lượt và {}.".format(
                int(observation.get("turn_count") or 0), OVERLAP_MEANING["carried"]
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
                # words it recognises; "carried" / "not_carried" read as neutral
                # labels there and the signal never reached the summary.
                _facet(
                    "context_carried",
                    "Có bám chủ đề mở đầu",
                    "evidence",
                    "categorical",
                    {"carried": "yes", "not_carried": "no"}.get(overlap, "not_applicable"),
                ),
                _facet(
                    "reached_two_replies",
                    "Đủ hai lượt trả lời",
                    "evidence",
                    "categorical",
                    "yes" if assistant_replies >= 2 else "no",
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
                       _process_notes(case, assistant_replies, overlap)),
            ],
        },
        {
            "key": "multiturn_coverage.primary",
            "label": "Multi-turn coverage",
            "contextType": "multiturn_coverage",
            "facets": [
                _facet("subintent_code", "Subintent", "primary", "categorical", str(case.get("subintent_code") or "")),
                _facet("parent_intent_code", "Nhóm intent", "primary", "categorical", str(case.get("parent_intent_code") or "")),
                _facet("lexical_topic_overlap", "Bám chủ đề (proxy từ vựng)", "evidence", "categorical", lexical_topic_overlap(turns)),
                _facet("turn_count", "Số lượt thực tế", "metric", "continuous", int(observation.get("turn_count") or 0)),
                _facet("reference_turn_count", "Số lượt tham chiếu", "control", "continuous", int(case.get("reference_turn_count") or 0)),
                _facet("assistant_reply_count", "Số lượt trợ lý trả lời", "metric", "continuous", assistant_replies),
                # A flagged seed is noisy input, not a model failure: reporting
                # must be able to separate the two.
                _facet("seed_quality", "Chất lượng seed", "control", "categorical", str(case.get("seed_quality") or "unknown")),
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
