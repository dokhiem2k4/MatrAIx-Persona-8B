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
    """Build ``structured_output.json`` for one conversation seed."""
    case = dict(case_run.get("case") or {})
    observation = dict(case_run.get("observation") or {})
    turns = observation.get("turns") or []
    assistant_replies = sum(
        1 for t in turns if isinstance(t, dict) and str(t.get("assistant_message") or "").strip()
    )

    overlap = lexical_topic_overlap(turns)
    if assistant_replies < 2:
        status, why = "unresolved", "Hội thoại chỉ đạt {} lượt trả lời, chưa đủ để đo giữ ngữ cảnh.".format(assistant_replies)
    elif overlap == "not_carried":
        status, why = "partially_resolved", "Trợ lý trả lời đủ lượt nhưng không lượt nào dùng lại từ khoá persona nêu ở đầu."
    else:
        status, why = "resolved", "Hội thoại {} lượt, bám chủ đề mở đầu ({}).".format(
            int(observation.get("turn_count") or 0), overlap)

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
                       "\n".join("Lượt {}: {} -> {}".format(
                           i + 1,
                           str(x.get("user_message") or "")[:120],
                           str(x.get("assistant_message") or "")[:120],
                       ) for i, x in enumerate(turns[:4]) if isinstance(x, dict))),
                _facet("process_notes", "Ghi chú chấm", "explanation", "textual",
                       "Subintent {} · seed {} · {} lượt trợ lý trả lời · bám chủ đề {}".format(
                           case.get("subintent_code"), case.get("seed_quality"),
                           assistant_replies, overlap)),
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
