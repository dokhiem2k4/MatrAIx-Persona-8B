"""Turn the RISE discovery Task List into runnable cases.

The source is a moderator's discussion guide: a wide matrix where each column
is a task group and two rows hold the scenarios to read aloud, one for a parked
car and one for a moving one. Fifteen of those cells carry a scenario.

The scenario text is copied verbatim. It is what the persona is asked to act
on, and a paraphrase would quietly change the measurement -- these sentences
were written to be read to a person without improvisation.

Usage:
    uv run python application/scripts/convert_vita_discovery_tasklist.py \
        --source "~/Downloads/...(Task List) (1).csv" \
        --out application/tasks/chat_0909-vita-tasklist/input/cases.jsonl
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

# Row indices in the guide. The sheet is hand-maintained, so these are checked
# against the row labels at load time rather than trusted blindly.
ROW_GROUP = 4
ROW_TASK = 5
ROW_PARKED = 6
ROW_DRIVING = 7
ROW_CRITERIA = 8

# The eight capability columns. Columns 1-6 are the settings walkthrough (a
# screen exercise, no scenario) and 16-22 are behaviours the moderator watches
# across all of them, so neither yields a case.
CAPABILITY_COLUMNS = range(8, 16)

CONTEXT_LABELS = {"parked": "Đang đỗ xe", "driving": "Đang lái xe"}


def _clean(text: str) -> str:
    """Collapse the newlines Excel leaves inside a cell, keep the wording."""
    return re.sub(r"\s+", " ", (text or "").replace(" ", " ")).strip()


def _slug(text: str) -> str:
    """ASCII slug from Vietnamese text, for ids that stay keyboard-typable."""
    stripped = unicodedata.normalize("NFD", text)
    stripped = "".join(ch for ch in stripped if unicodedata.category(ch) != "Mn")
    stripped = stripped.replace("đ", "d").replace("Đ", "D")
    return re.sub(r"[^a-z0-9]+", "_", stripped.lower()).strip("_")


def capability_number(group_text: str) -> int | None:
    match = re.search(r"Nhóm năng lực\s*(\d+)", group_text)
    return int(match.group(1)) if match else None


def capability_title(group_text: str) -> str:
    """The part after "Nhóm năng lực N - " and before the colon."""
    body = re.sub(r"^Nhóm năng lực\s*\d+\s*-\s*", "", group_text).strip()
    return body.split(":", 1)[0].strip()


def strip_context_prefix(scenario: str) -> str:
    """Drop the "[Đang đỗ xe]" marker; it becomes a field, not prose.

    The guide spells it two ways -- "đỗ" and "đổ" -- so both are matched.
    """
    return re.sub(r"^\[\s*Đang\s+đ[ỗổ]\s+xe\s*\]|^\[\s*Đang\s+lái\s+xe\s*\]", "", scenario).strip()


def split_probe(scenario: str) -> tuple[str, str]:
    """Separate the moderator's fallback prompt from the scenario itself.

    "Probe thêm nếu người dùng không rõ: ..." is an instruction to the human
    running the session, not something to read out, so it is kept as its own
    field instead of being spoken by the persona.
    """
    parts = re.split(r"\bProbe thêm[^:]*:", scenario, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return scenario.strip(), ""


def build_cases(rows: list[list[str]]) -> list[dict[str, Any]]:
    label = _clean(rows[ROW_GROUP][0]) if rows[ROW_GROUP] else ""
    if "Nhóm task" not in label:
        raise SystemExit(
            "row {} should be the task-group header, found {!r}".format(ROW_GROUP, label)
        )

    cases: list[dict[str, Any]] = []
    for column in CAPABILITY_COLUMNS:
        group = _clean(rows[ROW_TASK][column]) if column < len(rows[ROW_TASK]) else ""
        if not group:
            continue
        number = capability_number(group)
        if number is None:
            raise SystemExit("column {} is not a capability group: {!r}".format(column, group))
        title = capability_title(group)
        criteria = _clean(rows[ROW_CRITERIA][column]) if column < len(rows[ROW_CRITERIA]) else ""

        for row_index, context in ((ROW_PARKED, "parked"), (ROW_DRIVING, "driving")):
            raw = _clean(rows[row_index][column]) if column < len(rows[row_index]) else ""
            if not raw:
                continue
            scenario, probe = split_probe(strip_context_prefix(raw))
            cases.append(
                {
                    "case_id": "vd_{:02d}_{}".format(number, context),
                    "capability_number": number,
                    "capability_code": _slug(title),
                    "capability_label_vi": title,
                    "capability_brief_vi": group,
                    "vehicle_state": context,
                    "vehicle_state_label_vi": CONTEXT_LABELS[context],
                    "scenario_vi": scenario,
                    "moderator_probe_vi": probe,
                    "success_criteria_vi": criteria,
                }
            )
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    text = args.source.expanduser().read_text(encoding="utf-8-sig")
    if "?i?m" in text or text.count("?") > len(text) // 40:
        raise SystemExit(
            "source looks mojibaked (Vietnamese diacritics lost). Re-export it "
            "from Excel as 'CSV UTF-8'."
        )
    rows = list(csv.reader(io.StringIO(text)))
    cases = build_cases(rows)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(case, ensure_ascii=False) + "\n")

    by_state: dict[str, int] = {}
    for case in cases:
        by_state[case["vehicle_state"]] = by_state.get(case["vehicle_state"], 0) + 1
    print("wrote {} ({} cases)".format(args.out, len(cases)))
    print("  capabilities: {}".format(sorted({c["capability_number"] for c in cases})))
    print("  by vehicle state: {}".format(by_state))
    print("  with moderator probe: {}".format(sum(1 for c in cases if c["moderator_probe_vi"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
