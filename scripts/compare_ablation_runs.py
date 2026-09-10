#!/usr/bin/env python3
"""Did rewriting the prompt make the fields visible? Two runs, same arms.

The control run rendered every field as ``- Label: Value``, all 48 of them,
tier ignored. The treatment run renders the 18 prompt-tier fields as
second-person directives and drops the rest. Same personas, same stimuli, same
arms -- only the renderer differs, so a difference between the two runs is the
renderer's.

Read the probe columns, not the distance columns. The distance scorer's noise
floor is 0.408 and it could not separate any field from it; that is the finding
this run exists to route around, not a baseline to beat.

    uv run python scripts/compare_ablation_runs.py \\
        --control data/ablation --treatment data/ablation-directives
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def score(directory: Path) -> dict:
    """Run the probe scorer over one directory and return its JSON."""
    out = directory / "probes.json"
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/score_persona_probes.py"),
            str(directory),
            "--json-out",
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    return json.loads(out.read_text())


def word_counts(directory: Path, arm: str) -> list[float]:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from score_persona_probes import load_arm, probe_word_count

    return [probe_word_count(t) for t in load_arm(directory, arm).values()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--control", type=Path, default=REPO_ROOT / "data/ablation")
    ap.add_argument(
        "--treatment", type=Path, default=REPO_ROOT / "data/ablation-directives"
    )
    args = ap.parse_args()

    if not (args.treatment / "base-a.csv").is_file():
        print(f"no treatment run at {args.treatment} -- run the arms first:")
        print(f"  OUT_DIR={args.treatment} bash data/ablation/run_arms.sh")
        return 1

    control, treatment = score(args.control), score(args.treatment)
    by_field = {
        "control": {p["field"]: p for p in control["probes"]},
        "treatment": {p["field"]: p for p in treatment["probes"]},
    }

    print("PROBES -- does flipping the field move its own measure?")
    print(f"{'field':24s} {'control':>18s} {'treatment':>18s}")
    for field in sorted(set(by_field["control"]) | set(by_field["treatment"])):
        c = by_field["control"].get(field)
        t = by_field["treatment"].get(field)
        fmt = lambda p: (
            f"{p['delta']:+.2f} {p['verdict']:8s}" if p else " " * 17
        )  # noqa: E731
        print(f"{field:24s} {fmt(c):>18s} {fmt(t):>18s}")

    print("\nCOMPLIANCE -- did the persona use the value it was told to?")
    ctrl = {c["field"]: c for c in control.get("compliance", [])}
    treat = {c["field"]: c for c in treatment.get("compliance", [])}
    for field in sorted(set(ctrl) | set(treat)):
        c, t = ctrl.get(field), treat.get(field)
        print(
            f"  {field}: control {c['arm_followed_its_own_value']:.0%}"
            if c
            else f"  {field}: control  --",
            end="",
        )
        print(f"  ->  treatment {t['arm_followed_its_own_value']:.0%}" if t else "")

    print("\nUTTERANCE LENGTH -- the directives name a word budget in a way")
    print("labels never did, so the spread across personas should widen.")
    for name, directory in (("control", args.control), ("treatment", args.treatment)):
        counts = word_counts(directory, "base-a")
        print(
            f"  {name:9s} median {statistics.median(counts):5.1f} words, "
            f"sd {statistics.pstdev(counts):4.1f}, "
            f"range {min(counts):.0f}-{max(counts):.0f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
