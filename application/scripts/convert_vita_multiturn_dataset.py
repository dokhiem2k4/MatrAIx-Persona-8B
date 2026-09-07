"""Convert the 46-intent multi-turn workbook into conversation seeds.

Only the FIRST user turn of each conversation becomes a seed. The reference
assistant turns are deliberately dropped: if the persona could read them it
would steer the conversation onto the transcript and the measurement would mean
nothing.

The workbook is noisy. Several seeds are speech-recognition fragments or sit
under a sub_intent they do not match. Label mismatch cannot be detected
reliably by rule, so this converter flags only what it can defend --
``seed_quality = too_short`` -- and writes ``seed_review.md`` listing every seed
so a person can judge the rest.

    uv run --with openpyxl python application/scripts/convert_vita_multiturn_dataset.py \
        --source "/path/to/Dataset - 46 Intent - Multiturn - 27Aug26.xlsx" \
        --out-dir application/tasks/chat_0709-vita-drive-multiturn-coverage/input \
        --review-out application/tasks/chat_0709-vita-drive-multiturn-coverage/seed_review.md
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any

from application.scripts.vita_intent_taxonomy import SUBINTENT_BY_LABEL_VI


class MultiturnConversionError(ValueError):
    """Raised when a conversation cannot be converted safely."""


MIN_SEED_WORDS = 4

PARENT_BY_SUBINTENT_CODE: dict[str, str] = {
    code: parent for code, parent in SUBINTENT_BY_LABEL_VI.values()
}
LABEL_BY_SUBINTENT_CODE: dict[str, str] = {
    code: label for label, (code, _) in SUBINTENT_BY_LABEL_VI.items()
}


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def group_conversations(rows: list[dict[str, Any]]) -> "collections.OrderedDict":
    """Group flat turn rows into ``{(parent, subintent): [rows]}`` in file order."""
    grouped: collections.OrderedDict = collections.OrderedDict()
    for row in rows:
        key = (_text(row.get("Parent_intent")), _text(row.get("sub_intent")))
        grouped.setdefault(key, []).append(row)
    return grouped


def build_conversation_record(
    key: tuple[str, str], rows: list[dict[str, Any]], index: int
) -> dict[str, Any]:
    """Turn one grouped conversation into a ``cases.jsonl`` seed record."""
    parent_intent_code, subintent_code = key

    expected_parent = PARENT_BY_SUBINTENT_CODE.get(subintent_code)
    if expected_parent is None:
        raise MultiturnConversionError(
            "sub_intent {!r} is not in the taxonomy".format(subintent_code)
        )
    if expected_parent != parent_intent_code:
        raise MultiturnConversionError(
            "Parent_intent {!r} disagrees with taxonomy {!r} for sub_intent {!r}".format(
                parent_intent_code, expected_parent, subintent_code
            )
        )

    user_turns = [row for row in rows if _text(row.get("role")) == "user"]
    seeds = [row for row in user_turns if int(row.get("turn_index") or 0) == 1]
    if not seeds:
        raise MultiturnConversionError(
            "conversation {!r} has no first user turn".format(subintent_code)
        )
    seed = _text(seeds[0].get("content"))
    if not seed:
        raise MultiturnConversionError(
            "conversation {!r} has an empty first user turn".format(subintent_code)
        )

    word_count = len(seed.split())
    return {
        "case_id": "vm_{:04d}".format(index + 1),
        "subintent_code": subintent_code,
        "parent_intent_code": parent_intent_code,
        "subintent_label_vi": LABEL_BY_SUBINTENT_CODE.get(subintent_code, ""),
        "user_input": seed,
        "seed_user_turn": seed,
        "seed_word_count": word_count,
        "seed_quality": "ok" if word_count >= MIN_SEED_WORDS else "too_short",
        "reference_turn_count": len(user_turns),
        "input_constraint": "none",
        "state": {},
    }


def _read_rows(source: Path) -> list[dict[str, Any]]:
    import openpyxl

    workbook = openpyxl.load_workbook(source, data_only=True, read_only=True)
    sheet = workbook.worksheets[0]
    rows = list(sheet.iter_rows(values_only=True))
    workbook.close()
    if not rows:
        raise MultiturnConversionError("workbook has no rows")
    header = [_text(cell) for cell in rows[0]]
    return [dict(zip(header, row)) for row in rows[1:] if any(c is not None for c in row)]


def render_review(records: list[dict[str, Any]]) -> str:
    """Render every seed for human review; rules cannot catch label mismatch."""
    flagged = sum(1 for r in records if r["seed_quality"] != "ok")
    lines = [
        "# Seed review — chat_0709-vita-drive-multiturn-coverage",
        "",
        "Mỗi dòng là lượt user đầu tiên của một hội thoại, dùng làm mục tiêu giao cho persona.",
        "",
        "`seed_quality = too_short` là thứ luật bắt được ({} / {} seed). ".format(flagged, len(records)),
        "Thứ luật **không** bắt được là seed gán sai nhãn hoặc là nhiễu nhận dạng giọng nói —",
        "phải người đọc. Cột **Duyệt** để trống, người review điền `ok` hoặc `loại`.",
        "",
        "| case_id | subintent_code | từ | quality | seed | Duyệt |",
        "|---|---|---|---|---|---|",
    ]
    for record in records:
        lines.append(
            "| {} | `{}` | {} | {} | {} | |".format(
                record["case_id"],
                record["subintent_code"],
                record["seed_word_count"],
                record["seed_quality"],
                record["seed_user_turn"].replace("|", "\\|"),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--review-out", required=True, type=Path)
    args = parser.parse_args()

    grouped = group_conversations(_read_rows(args.source))
    records = [
        build_conversation_record(key, rows, index)
        for index, (key, rows) in enumerate(grouped.items())
    ]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    path = args.out_dir / "cases.jsonl"
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8"
    )
    args.review_out.parent.mkdir(parents=True, exist_ok=True)
    args.review_out.write_text(render_review(records), encoding="utf-8")

    flagged = [r["case_id"] for r in records if r["seed_quality"] != "ok"]
    print("wrote {} conversation seeds to {}".format(len(records), path))
    print("flagged too_short: {} -> {}".format(len(flagged), flagged))
    print("review sheet: {}".format(args.review_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
