#!/usr/bin/env python3
"""Export every stage-1 job to CSV and merge them into one stimulus set.

``export_vita_utterances.py`` turns a single job into the workbook layout; a
multi-intent stage-2 needs all of them in one file, and needs to know which
rows failed to come back so a silent gap never gets mistaken for coverage.

Usage:
    uv run python scripts/merge_vita_datasets.py jobs/vita-s1lite-* -o data/vita-stimuli.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORTER = REPO_ROOT / "scripts" / "export_vita_utterances.py"

COLUMNS = [
    "intent_code",
    "subintent_code",
    "subintent_name",
    "scenario",
    "first_input",
    "vehicle_state",
    "ASSISTANT_MODE",
    "source",
    "note",
    "seed_input",
    "persona_id",
    "persona_name",
    "persona_profile",
    "model",
]


def task_path_for(job_dir: Path) -> Path:
    """The task this job actually ran.

    ``export_vita_utterances.py`` defaults to the navigation task -- it predates
    the other intents. Left to that default it labels every exported row with
    navigation's grid metadata, so a nine-intent merge would come out claiming
    to be nine copies of navigation. Always pass the job's real task.
    """
    config = json.loads((job_dir / "config.json").read_text(encoding="utf-8"))
    tasks = config.get("tasks") or []
    if not tasks or not tasks[0].get("path"):
        raise RuntimeError("job {} has no task path in config.json".format(job_dir))
    return REPO_ROOT / str(tasks[0]["path"])


def export_job(job_dir: Path, out_csv: Path) -> list[dict[str, str]]:
    result = subprocess.run(
        [
            sys.executable,
            str(EXPORTER),
            str(job_dir),
            "--task",
            str(task_path_for(job_dir)),
            "-o",
            str(out_csv),
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(
            "export failed for {}: {}".format(job_dir, (result.stderr or "").strip()[:300])
        )
    # utf-8-sig reads both BOM-prefixed and plain UTF-8; plain utf-8 would turn
    # the first header into "﻿intent_code" and silently blank that column.
    with out_csv.open(encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobs", nargs="+", type=Path, help="stage-1 job directories")
    parser.add_argument("-o", "--out", type=Path, required=True)
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="exit non-zero if any job produced no rows",
    )
    args = parser.parse_args()

    merged: list[dict[str, str]] = []
    empty_jobs: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for job_dir in args.jobs:
            if not job_dir.is_dir():
                continue
            out_csv = Path(tmp) / (job_dir.name + ".csv")
            rows = export_job(job_dir, out_csv)
            # A row with no first_input cannot open a conversation; carrying it
            # would produce a trial that silently falls back to an invented need.
            usable = [r for r in rows if (r.get("first_input") or "").strip()]
            print(
                "{:44s} {:>4} rows  ({} usable)".format(job_dir.name, len(rows), len(usable))
            )
            if not usable:
                empty_jobs.append(job_dir.name)
            merged.extend(usable)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig: this workbook is opened in Excel, which decodes a BOM-less
    # CSV with the machine's ANSI codepage and mangles every Vietnamese row.
    with args.out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(merged)

    intents = Counter(r.get("intent_code") for r in merged)
    personas = Counter(r.get("persona_id") for r in merged)
    print("\nwrote {}".format(args.out))
    print("  rows     : {}".format(len(merged)))
    print("  intents  : {}".format(len(intents)))
    for code, count in sorted(intents.items()):
        print("    {:34s} {:>4}".format(code or "<empty>", count))
    print("  personas : {}".format(len(personas)))
    if empty_jobs:
        print("\nWARNING: no usable rows from: {}".format(", ".join(empty_jobs)))
        if args.require_complete:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
