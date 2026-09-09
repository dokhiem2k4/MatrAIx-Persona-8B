"""Score what a first-time driver took away about the assistant itself.

The discussion guide asks three things after showing a respondent the brand
message and the avatar: say what Vita is, say what it promises, describe it in
three words. There is no message and no avatar here, so the basis is swapped:
the persona forms its impression from the conversation it just had. That is a
different measurement and the payload says so -- `impression_basis` is
`conversation_only`.

It is arguably the harder test. A poster can promise anything; the assistant
has to earn the same words by how it actually talks.

The three axes come from the guide's own criteria ("Hiểu ý – Được việc – Đúng
mực") and they line up with what the deployment's own /api/policy declares:
"Hiểu đúng ý định", "Hoàn thành mục tiêu với ít bước nhất", "Giọng điệu tự
nhiên, tôn trọng và tinh tế".

Matching is LEXICAL and nothing more. A driver who says "nó nắm được ý mình"
lands on the first axis; one who says the same thing in words not listed here
does not. Read a miss as "not detected", never as "the assistant failed" -- the
verbatim answer sits next to the score for exactly that reason.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

# Each axis is a set of stems a Vietnamese driver plausibly uses for it. Kept
# small and specific: a broad list would match everything and measure nothing.
BRAND_AXES: dict[str, tuple[str, tuple[str, ...]]] = {
    "hieu_y": (
        "Hiểu ý",
        ("hieu y", "hieu duoc y", "nam duoc y", "hieu minh", "hieu nhanh",
         "doan duoc", "biet minh muon", "hieu dung", "tinh y", "nhay"),
    ),
    "duoc_viec": (
        "Được việc",
        ("duoc viec", "lam duoc", "xong viec", "giai quyet", "huu ich", "tien loi",
         "nhanh gon", "hieu qua", "gon le", "dut khoat", "tien ich"),
    ),
    "dung_muc": (
        "Đúng mực",
        ("dung muc", "lich su", "te nhi", "tinh te", "ton trong", "chung muc",
         "diem dam", "nha nhan", "khong lam dung", "an toan", "than thien vua"),
    ),
}

# What the guide wants a respondent to notice: that this is a daily-life
# assistant, "không chỉ là trợ lý điều khiển xe bằng giọng nói".
BROADER_SCOPE = "broader_daily_assistant"


def _fold(text: str) -> str:
    """Lowercase, strip diacritics, squeeze spaces -- for lexical matching only."""
    stripped = unicodedata.normalize("NFD", (text or "").lower())
    stripped = "".join(ch for ch in stripped if unicodedata.category(ch) != "Mn")
    stripped = stripped.replace("đ", "d")
    return re.sub(r"\s+", " ", stripped).strip()


def axes_detected(*texts: str) -> list[str]:
    """Which of the three brand axes the driver's own words touch."""
    folded = " ".join(_fold(t) for t in texts)
    return [
        axis
        for axis, (_label, stems) in BRAND_AXES.items()
        if any(stem in folded for stem in stems)
    ]


def three_words(raw: str) -> list[str]:
    """The three words the driver chose, however they punctuated them."""
    parts = [p.strip(" .;–-") for p in re.split(r"[,;/]|\bvà\b", raw or "")]
    return [p for p in parts if p][:3]


def _facet(key: str, label: str, role: str, kind: str, value: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "role": role, "kind": kind, "value": value}


def _turns(observation: dict[str, Any]) -> list[dict[str, Any]]:
    return [t for t in (observation.get("turns") or ()) if isinstance(t, dict)]


def conversation_path(observation: dict[str, Any]) -> str:
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


SCOPE_MEANING = {
    "broader_daily_assistant": "trợ lý cho cuộc sống hằng ngày",
    "car_control_only": "chỉ là trợ lý điều khiển xe",
    "unclear": "chưa hình dung được",
}


def _process_notes(case: dict[str, Any], observation: dict[str, Any], axes: list[str], scope: str) -> str:
    """One sentence a reviewer can act on, not a row of codes."""
    named = ", ".join(BRAND_AXES[a][0] for a in axes) if axes else "không trục nào"
    return (
        "Cách tiếp xúc: {}. Hội thoại {} lượt. Người lái chạm được {} trong ba trục "
        "thương hiệu ({}). Sau khi nói chuyện, họ thấy Vita là {}. (mã case {})".format(
            case.get("encounter_label_vi") or case.get("encounter_code"),
            len(_turns(observation)),
            len(axes),
            named,
            SCOPE_MEANING.get(scope, "không rõ"),
            case.get("case_id"),
        )
    )


def build_evaluation_payload(
    case_run: dict[str, Any], feedback: dict[str, Any] | None
) -> dict[str, Any]:
    """Build ``structured_output.json`` for one brand-recognition encounter."""
    case = dict(case_run.get("case") or {})
    observation = dict(case_run.get("observation") or {})
    feedback = feedback or {}

    role = str(feedback.get("assistantRole") or "").strip()
    promises = str(feedback.get("assistantPromises") or "").strip()
    words_raw = str(feedback.get("threeWords") or "").strip()
    words = three_words(words_raw)
    scope = str(feedback.get("moreThanCarControl") or "unclear").strip()
    trust = str(feedback.get("wouldTrust") or "unknown").strip()

    axes = axes_detected(words_raw, role, promises)

    # The guide's bar for this section: the respondent recognises a daily-life
    # assistant, and the words they reach for sit near the brand's own three.
    if not role:
        status, why = "unresolved", "Người lái không mô tả được Vita là gì."
    elif scope == "car_control_only":
        status = "partially_resolved"
        why = (
            "Sau khi nói chuyện, người lái vẫn thấy đây chỉ là trợ lý điều khiển "
            "xe — tiêu chí trong tài liệu là nhận ra một trợ lý cho cuộc sống "
            "hằng ngày."
        )
    elif scope == "unclear":
        status, why = "partially_resolved", "Người lái chưa hình dung được Vita là loại trợ lý nào."
    elif len(axes) >= 2:
        status = "resolved"
        why = "Người lái nhận ra vai trò rộng hơn điều khiển xe, và chạm được {}/3 trục thương hiệu.".format(len(axes))
    else:
        status = "partially_resolved"
        why = (
            "Người lái nhận ra vai trò rộng hơn điều khiển xe, nhưng cách họ mô tả "
            "chỉ chạm {}/3 trục thương hiệu.".format(len(axes))
        )

    contexts: list[dict[str, Any]] = [
        {
            "key": "task_outcome.primary",
            "label": "Task outcome",
            "contextType": "task_outcome",
            "facets": [
                _facet("outcome_status", "Kết quả", "primary", "categorical", status),
                _facet("resolution_basis", "Căn cứ", "control", "categorical", "user_feedback"),
                _facet(
                    "recognised_broader_role",
                    "Nhận ra vai trò rộng hơn",
                    "evidence",
                    "categorical",
                    {"broader_daily_assistant": "yes", "car_control_only": "no"}.get(scope, "unknown"),
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
                    "Cách tiếp xúc được giao",
                    "explanation",
                    "textual",
                    str(case.get("scenario_vi") or ""),
                ),
                _facet("process_notes", "Ghi chú chấm", "explanation", "textual", _process_notes(case, observation, axes, scope)),
            ],
        },
        {
            "key": "brand_recognition.primary",
            "label": "Brand recognition",
            "contextType": "brand_recognition",
            "facets": [
                _facet("encounter_code", "Cách tiếp xúc", "primary", "categorical", str(case.get("encounter_code") or "")),
                _facet("scope_perceived", "Vita là loại trợ lý gì", "primary", "categorical", scope),
                _facet("brand_axes_hit", "Số trục thương hiệu chạm được", "metric", "continuous", len(axes)),
                _facet("brand_axes", "Trục nào chạm được", "evidence", "textual", ", ".join(BRAND_AXES[a][0] for a in axes)),
                # Lexical match only. The verbatim answer sits right here so a
                # reader can overrule the count in one glance.
                _facet("brand_axis_basis", "Cách đối chiếu trục", "control", "categorical", "lexical_proxy"),
                # No brand message and no avatar were shown; the impression came
                # from the conversation. Never compare this straight to a
                # respondent who saw the poster.
                _facet("impression_basis", "Cơ sở ấn tượng", "control", "categorical", "conversation_only"),
                _facet("three_words", "Ba từ mô tả Vita", "evidence", "textual", ", ".join(words)),
                _facet("three_words_count", "Số từ đưa ra", "control", "continuous", len(words)),
                _facet("would_trust", "Có tin tưởng giao việc", "evidence", "categorical", trust),
                _facet("role_stated", "Vita là gì (nguyên văn)", "explanation", "textual", role),
                _facet("promises_stated", "Lời hứa cảm nhận được (nguyên văn)", "explanation", "textual", promises),
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
                    _facet("need_constraint_satisfaction", "Tin tưởng giao việc", "evidence", "categorical", trust),
                    _facet("feedback_reason", "Vì sao ba từ đó", "explanation", "textual", str(feedback.get("threeWordsReason") or "")),
                    _facet("clarifying_notes", "Vì sao thấy vậy về vai trò", "explanation", "textual", str(feedback.get("moreThanCarControlReason") or "")),
                    _facet("trust_notes", "Vì sao tin / chưa tin", "explanation", "textual", str(feedback.get("wouldTrustReason") or "")),
                ],
            }
        )

    return {"schemaVersion": "1.0", "artifactType": "matraix.trial_evaluation", "contexts": contexts}
