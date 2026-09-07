#!/usr/bin/env python3
"""Price a set of jobs from the tokens they actually consumed.

``result.json`` carries ``cost_usd``, but it is a floor and sometimes absent:
a trial that dies mid-flight records no cost even though the provider billed
every call it made before dying, and providers that do not return a cost field
leave the number to be derived. So this reads token counts and applies a rate
table, then reports the recorded figure beside the derived one -- a gap between
them is the unbilled remainder, which is information rather than noise.

Rates are per token and must be stated by the caller in a JSON file so the
invoice never depends on a price this script happens to remember:

    {"models/gemini-3.1-flash-lite": {"input": 2.5e-07,
                                      "cache": 2.5e-08,
                                      "output": 1.5e-06}}

Usage:
    uv run python scripts/build_run_invoice.py --rates rates.json \
        --job jobs/vita-drive-agent-v2-s1-'*' --job jobs/vita-drive-agent-v2-3p9i \
        -o reports/invoice.md
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any

MODEL_KEY_HINT = "model_name"


def job_model(job_dir: Path, stats: dict[str, Any]) -> str:
    for name in stats.get("evals") or {}:
        if "__" in name:
            return name.split("__")[1]
    try:
        config = json.loads((job_dir / "config.json").read_text(encoding="utf-8"))
    except OSError:
        return "?"
    agents = config.get("agents") or []
    return (agents[0].get(MODEL_KEY_HINT) if agents else "?") or "?"


def normalise(model: str) -> str:
    """Strip the harness prefix so a rate table keys on the provider's own id."""
    value = model.strip()
    if value.startswith("openrouter/"):
        value = value[len("openrouter/") :]
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rates", type=Path, required=True)
    parser.add_argument("--job", action="append", required=True, dest="jobs")
    parser.add_argument("--label", action="append", default=[], dest="labels")
    parser.add_argument("-o", "--out", type=Path)
    args = parser.parse_args()

    rates = json.loads(args.rates.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    unpriced: set[str] = set()

    for position, pattern in enumerate(args.jobs):
        label = args.labels[position] if position < len(args.labels) else pattern
        group = {
            "label": label,
            "jobs": 0,
            "trials": 0,
            "completed": 0,
            "errored": 0,
            "input": 0,
            "cache": 0,
            "output": 0,
            "recorded": 0.0,
            "models": set(),
        }
        for result_path in sorted(glob.glob(pattern.rstrip("/") + "/result.json")):
            job_dir = Path(result_path).parent
            data = json.loads(Path(result_path).read_text(encoding="utf-8"))
            stats = data.get("stats") or {}
            group["jobs"] += 1
            group["trials"] += data.get("n_total_trials", 0)
            group["completed"] += stats.get("n_completed_trials", 0)
            group["errored"] += stats.get("n_errored_trials", 0)
            group["input"] += stats.get("n_input_tokens") or 0
            group["cache"] += stats.get("n_cache_tokens") or 0
            group["output"] += stats.get("n_output_tokens") or 0
            group["recorded"] += stats.get("cost_usd") or 0.0
            group["models"].add(normalise(job_model(job_dir, stats)))
        if group["jobs"]:
            rows.append(group)

    lines: list[str] = ["| Hạng mục | Job | Trial | Input | Cache | Output | Ghi nhận | Tính lại |",
                        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    total_recorded = total_derived = 0.0
    for group in rows:
        model = sorted(group["models"])[0] if group["models"] else "?"
        rate = rates.get(model)
        if rate is None:
            unpriced.add(model)
            derived = 0.0
        else:
            # Harbor counts cache inside n_input, so bill the remainder at the
            # full input rate and the cached part at the cache rate.
            billable = max(0, group["input"] - group["cache"])
            derived = (
                billable * rate["input"]
                + group["cache"] * rate["cache"]
                + group["output"] * rate["output"]
            )
        total_recorded += group["recorded"]
        total_derived += derived
        lines.append(
            "| {} | {} | {} | {:,} | {:,} | {:,} | ${:.4f} | ${:.4f} |".format(
                group["label"], group["jobs"], group["trials"],
                group["input"], group["cache"], group["output"],
                group["recorded"], derived,
            )
        )
    lines.append(
        "| **Tổng** | | | | | | **${:.4f}** | **${:.4f}** |".format(
            total_recorded, total_derived
        )
    )

    report = "\n".join(lines)
    if unpriced:
        report += "\n\nKhông có đơn giá cho: {}".format(", ".join(sorted(unpriced)))
    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report + "\n", encoding="utf-8")
        print("\nwrote {}".format(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
