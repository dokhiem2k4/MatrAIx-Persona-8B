"""Convert the Vita Demo workbook into ``cases.jsonl`` for the A/B mode task.

The workbook is a balanced factorial grid: 46 subintents x vehicle_state
(driving/parking) x ASSISTANT_MODE (quiet/balance/proactive). It carries no
expected output, so the task it feeds is judged on persona experience rather
than on matching a golden answer.

    uv run --with openpyxl python application/scripts/convert_vita_demo_dataset.py \
        --source "/path/to/Dataset - Vita Demo - 27Aug26 (1).xlsx" \
        --out-dir application/tasks/chat_0709-vita-drive-singleturn-mode-ab/input
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from application.scripts.vita_intent_taxonomy import (
    UnknownSubintentError,
    subintent_entry,
)


class DemoConversionError(ValueError):
    """Raised when a demo row cannot be converted safely."""


VEHICLE_STATES = frozenset({"driving", "parking"})
ASSISTANT_MODES = frozenset({"quiet", "balance", "proactive"})


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def build_demo_case_record(row: dict[str, Any], index: int) -> dict[str, Any]:
    """Turn one demo workbook row into a ``cases.jsonl`` record."""
    label = _text(row.get("subintent_name"))
    try:
        subintent_code, parent_intent_code = subintent_entry(label)
    except UnknownSubintentError as exc:
        raise DemoConversionError(str(exc)) from None

    # Cross-check the workbook's own identifiers against the taxonomy rather
    # than trusting either side: a silent disagreement would split one subintent
    # into two buckets in the report.
    if _text(row.get("subintent_code")) != subintent_code:
        raise DemoConversionError(
            "subintent_code {!r} disagrees with taxonomy {!r} for label {!r}".format(
                _text(row.get("subintent_code")), subintent_code, label
            )
        )
    if _text(row.get("intent_code")) != parent_intent_code:
        raise DemoConversionError(
            "intent_code {!r} disagrees with taxonomy {!r} for label {!r}".format(
                _text(row.get("intent_code")), parent_intent_code, label
            )
        )

    vehicle_state = _text(row.get("vehicle_state"))
    if vehicle_state not in VEHICLE_STATES:
        raise DemoConversionError("unknown vehicle_state {!r}".format(vehicle_state))

    assistant_mode = _text(row.get("ASSISTANT_MODE"))
    if assistant_mode not in ASSISTANT_MODES:
        raise DemoConversionError("unknown ASSISTANT_MODE {!r}".format(assistant_mode))

    user_input = _text(row.get("input"))
    if not user_input:
        raise DemoConversionError("input must not be empty")

    return {
        "case_id": "vd_{:04d}".format(index + 1),
        "subintent_code": subintent_code,
        "parent_intent_code": parent_intent_code,
        "subintent_label_vi": label,
        "user_input": user_input,
        # No ground truth exists, so the persona is free to rephrase.
        "input_constraint": "none",
        "state": {"vehicle_state": vehicle_state, "assistant_mode": assistant_mode},
        "source": _text(row.get("source")) or "unknown",
        "note": _text(row.get("note")),
    }


def _read_rows(source: Path) -> list[dict[str, Any]]:
    import openpyxl

    workbook = openpyxl.load_workbook(source, data_only=True, read_only=True)
    sheet = workbook.worksheets[0]
    rows = list(sheet.iter_rows(values_only=True))
    workbook.close()
    if not rows:
        raise DemoConversionError("workbook has no rows")
    header = [_text(cell) for cell in rows[0]]
    return [dict(zip(header, row)) for row in rows[1:] if any(c is not None for c in row)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    records = [build_demo_case_record(row, i) for i, row in enumerate(_read_rows(args.source))]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    path = args.out_dir / "cases.jsonl"
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8"
    )
    print("wrote {} cases to {}".format(len(records), path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
