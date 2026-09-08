#!/usr/bin/env python3
"""Compare two runs of the same persona x case pairs: before a fix, and after.

Two runs are only comparable if they faced the same stimulus, which is what a
run manifest guarantees -- see application/scripts/vita_run_manifest.py. This
joins them on (persona, case) and reports what actually moved.

The headline is not the average. Averages hide the case that regressed behind
the four that improved, and a regression is the thing worth knowing about
before shipping. So every pair that changed verdict is listed by name.

Usage:
    uv run python scripts/compare_vita_runs.py data/golden-2p-128 data/golden-2p-128-after
    uv run python scripts/compare_vita_runs.py <before> <after> --csv data/compare.csv
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

# Ordered worst to best, so a move down the list is a regression and a move up
# is a fix. "partially_resolved" sits between them: the assistant answered, but
# not in a way the dataset can grade.
OUTCOME_RANK = {"unresolved": 0, "partially_resolved": 1, "resolved": 2}

VERDICT_LABEL = {
    "fixed": "đã sửa được",
    "regressed": "hỏng đi",
    "still_failing": "vẫn sai như cũ",
    "still_passing": "vẫn đúng như cũ",
    "unchanged": "không đổi",
}


def results_csv(run_dir: Path) -> Path:
    """The one results CSV in a run folder, whatever the run was named."""
    matches = sorted(run_dir.glob("*-results.csv"))
    if not matches:
        raise SystemExit("no *-results.csv in {}".format(run_dir))
    if len(matches) > 1:
        raise SystemExit(
            "several results files in {}: {}".format(
                run_dir, ", ".join(path.name for path in matches)
            )
        )
    return matches[0]


def load_rows(run_dir: Path) -> dict[tuple[str, str], dict[str, Any]]:
    """Rows keyed by (persona_id, case_id) -- the pair a manifest pins down."""
    path = results_csv(run_dir)
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    with io.open(path, encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row.get("persona_id", ""), row.get("case_id", ""))
            rows[key] = row
    return rows


def load_manifest(run_dir: Path) -> dict[str, Any] | None:
    matches = sorted(run_dir.glob("*-manifest.json"))
    if not matches:
        return None
    return json.loads(matches[0].read_text(encoding="utf-8"))


def verdict(before: str, after: str) -> str:
    """How one pair moved between the two runs."""
    was = OUTCOME_RANK.get(before, -1)
    now = OUTCOME_RANK.get(after, -1)
    if now > was:
        return "fixed"
    if now < was:
        return "regressed"
    return "still_passing" if before == "resolved" else "still_failing"


def pass_rate(rows: list[dict[str, Any]]) -> tuple[int, int]:
    """Pairs that resolved, out of pairs scored at all."""
    scored = [r for r in rows if r.get("outcome_status") in OUTCOME_RANK]
    return sum(1 for r in scored if r["outcome_status"] == "resolved"), len(scored)


def _rate(passed: int, total: int) -> str:
    return "{}/{} ({:.0f}%)".format(passed, total, 100.0 * passed / total) if total else "-"


def compare(before_dir: Path, after_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """One record per pair present in both runs, plus notes on what did not join."""
    before = load_rows(before_dir)
    after = load_rows(after_dir)
    notes: list[str] = []

    before_manifest = load_manifest(before_dir)
    after_manifest = load_manifest(after_dir)
    if before_manifest and after_manifest:
        # A replay copies the pair list verbatim, so an unequal list means the
        # second run was not a replay of the first and the comparison is
        # measuring a different sample as well as a different assistant.
        if before_manifest.get("pairs") != after_manifest.get("pairs"):
            notes.append(
                "hai lượt chạy KHÔNG cùng danh sách persona x case -- chênh lệch "
                "dưới đây có phần do đổi mẫu, không chỉ do sửa trợ lý"
            )
        if before_manifest.get("task_path") != after_manifest.get("task_path"):
            notes.append("hai lượt chạy khác task, không so được")
    else:
        notes.append(
            "thiếu manifest ở ít nhất một lượt, không kiểm được là cùng bộ stimulus"
        )

    only_before = sorted(set(before) - set(after))
    only_after = sorted(set(after) - set(before))
    if only_before:
        notes.append("{} cặp chỉ có ở lượt trước".format(len(only_before)))
    if only_after:
        notes.append("{} cặp chỉ có ở lượt sau".format(len(only_after)))

    records = []
    for key in sorted(set(before) & set(after)):
        was, now = before[key], after[key]
        before_status = was.get("outcome_status", "")
        after_status = now.get("outcome_status", "")
        records.append(
            {
                "persona_id": key[0],
                "persona_name": was.get("persona_name", ""),
                "case_id": key[1],
                "intent_code": was.get("intent_code", ""),
                "subintent_name": was.get("subintent_name", ""),
                "error_type": was.get("scenario", "") or was.get("error_type", ""),
                "expected_decision": was.get("expected_decision", ""),
                "verdict": verdict(before_status, after_status),
                "outcome_before": before_status,
                "outcome_after": after_status,
                "decision_before": was.get("observed_decision", ""),
                "decision_after": now.get("observed_decision", ""),
                "tools_before": was.get("observed_tools", ""),
                "tools_after": now.get("observed_tools", ""),
                "rating_before": was.get("overall_rating", ""),
                "rating_after": now.get("overall_rating", ""),
                "reason_after": now.get("outcome_reason", ""),
            }
        )
    return records, notes


def report(records: list[dict[str, Any]], notes: list[str], before_dir: Path, after_dir: Path) -> None:
    for note in notes:
        print("! {}".format(note))
    if notes:
        print()

    if not records:
        print("không có cặp persona x case nào chung giữa hai lượt")
        return

    before_pass = sum(1 for r in records if r["outcome_before"] == "resolved")
    after_pass = sum(1 for r in records if r["outcome_after"] == "resolved")
    total = len(records)
    print("{} cặp persona x case chung giữa hai lượt".format(total))
    print("  trước ({}): {}".format(before_dir.name, _rate(before_pass, total)))
    print("  sau   ({}): {}".format(after_dir.name, _rate(after_pass, total)))
    delta = after_pass - before_pass
    print("  chênh lệch: {:+d} case đạt ({:+.1f} điểm phần trăm)".format(
        delta, 100.0 * delta / total
    ))

    tally = Counter(r["verdict"] for r in records)
    print()
    for name in ("fixed", "regressed", "still_failing", "still_passing"):
        if tally[name]:
            print("  {:16s} {:>4}".format(VERDICT_LABEL[name], tally[name]))

    # Per intent, because a fix usually lands in one area of the product and
    # the total hides which one.
    by_intent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_intent[record["intent_code"] or "(không rõ)"].append(record)
    print("\n{:34s} {:>4} {:>8} {:>8} {:>7}".format("intent", "n", "trước", "sau", "±"))
    for intent, group in sorted(
        by_intent.items(),
        key=lambda kv: sum(1 for r in kv[1] if r["outcome_after"] == "resolved")
        - sum(1 for r in kv[1] if r["outcome_before"] == "resolved"),
    ):
        was = sum(1 for r in group if r["outcome_before"] == "resolved")
        now = sum(1 for r in group if r["outcome_after"] == "resolved")
        print("{:34s} {:>4} {:>8} {:>8} {:>+7d}".format(
            intent[:34], len(group), was, now, now - was
        ))

    # Named, not counted. A regression is the reason to read this report at all.
    for name in ("regressed", "fixed"):
        group = [r for r in records if r["verdict"] == name]
        if not group:
            continue
        print("\n{} ({}):".format(VERDICT_LABEL[name].upper(), len(group)))
        for record in group:
            print("  {} · {} · {} · {} -> {}".format(
                record["case_id"],
                record["persona_name"] or record["persona_id"],
                record["subintent_name"] or record["intent_code"],
                record["outcome_before"],
                record["outcome_after"],
            ))
            if name == "regressed" and record["reason_after"]:
                print("      {}".format(record["reason_after"][:150]))


CSV_COLUMNS = [
    "case_id", "persona_id", "persona_name", "intent_code", "subintent_name",
    "error_type", "expected_decision", "verdict", "outcome_before", "outcome_after",
    "decision_before", "decision_after", "tools_before", "tools_after",
    "rating_before", "rating_after", "reason_after",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, help="run folder under data/")
    parser.add_argument("after", type=Path, help="run folder under data/")
    parser.add_argument("--csv", type=Path, help="also write the joined rows here")
    args = parser.parse_args()

    records, notes = compare(args.before, args.after)
    report(records, notes, args.before, args.after)

    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        # utf-8-sig so Excel reads the Vietnamese columns as UTF-8.
        with args.csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=CSV_COLUMNS, extrasaction="ignore", restval=""
            )
            writer.writeheader()
            writer.writerows(records)
        print("\nwrote {} ({} rows)".format(args.csv, len(records)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
