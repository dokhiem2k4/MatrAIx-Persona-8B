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

    contexts: list[dict[str, Any]] = [
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
