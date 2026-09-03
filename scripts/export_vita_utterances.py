#!/usr/bin/env python3
"""Export a step-1 job into the original Vita workbook column layout.

Each trial answers one free_text question per seed, so ``questionId`` is the
join key back to ``input/seed_index.json`` -- that sidecar restores the grid
cell (intent / subintent / vehicle_state / assistant_mode) the seed came from.

Usage:
    uv run python scripts/export_vita_utterances.py jobs/<job> -o out.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

# Multi-turn seed layout: scenario + first_input open a conversation the
# simulation continues on its own. Grid columns from the original workbook are
# kept so rows stay joinable to the source stimulus set.
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
    "model",
]


def load_seed_index(task_path: Path) -> dict[str, dict[str, Any]]:
    path = task_path / "input" / "seed_index.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {row["questionId"]: row for row in rows}


def trial_answers(trial: Path) -> list[tuple[str, str]]:
    """Return (questionId, utterance) pairs from the verifier artifact."""
    structured = trial / "verifier" / "structured_output.json"
    if not structured.is_file():
        return []
    payload = json.loads(structured.read_text(encoding="utf-8"))
    out: list[tuple[str, str]] = []
    for context in payload.get("contexts", []):
        if context.get("contextType") != "question_response":
            continue
        # context key is "question.<questionId>"
        question_id = str(context.get("key", "")).split(".", 1)[-1]
        for facet in context.get("facets", []):
            if facet.get("key") == "response":
                out.append((question_id, str(facet.get("value", "")).strip()))
    return out


def trial_meta(trial: Path) -> dict[str, str]:
    config = json.loads((trial / "config.json").read_text(encoding="utf-8"))
    agent = config.get("agent", config)
    kwargs = agent.get("kwargs") or config.get("kwargs") or {}
    persona_path = Path(str(kwargs.get("persona_path", "")))
    meta_path = trial / "persona_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    return {
        "model": str(agent.get("model_name") or config.get("model_name") or ""),
        "persona_id": persona_path.stem.replace("persona_", ""),
        "persona_name": str(meta.get("display_name") or ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", type=Path, help="job directory under jobs/")
    parser.add_argument("--task", type=Path, default=None, help="task dir (for seed_index)")
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()

    task_path = args.task or (
        REPO_ROOT
        / "application"
        / "tasks"
        / "survey_vita-utterance-journey-navigation-places"
    )
    seeds = load_seed_index(task_path)

    rows: list[dict[str, Any]] = []
    for trial in sorted(p for p in args.job.iterdir() if p.is_dir() and not p.name.startswith("_")):
        meta = trial_meta(trial)
        # Pivot the scenario/first_input question pair back onto one grid cell.
        pending: dict[tuple[str, str], dict[str, Any]] = {}
        for question_id, answer in trial_answers(trial):
            seed = seeds.get(question_id)
            if seed is None:
                continue
            key = (seed["subintent_code"], seed["seed_input"])
            row = pending.setdefault(
                key,
                {
                    "intent_code": seed["intent_code"],
                    "subintent_code": seed["subintent_code"],
                    "subintent_name": seed["subintent_name"],
                    "scenario": "",
                    "first_input": "",
                    "vehicle_state": seed["vehicle_state"],
                    "ASSISTANT_MODE": seed["assistant_mode"],
                    "source": f"persona:{meta['persona_id']}",
                    "note": "",
                    "seed_input": seed["seed_input"],
                    **meta,
                },
            )
            row[seed.get("field", "first_input")] = answer
        rows.extend(pending.values())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} dòng → {args.output}")
    by_model: dict[str, int] = {}
    for row in rows:
        by_model[row["model"]] = by_model.get(row["model"], 0) + 1
    for model, count in sorted(by_model.items()):
        print(f"  {count:4d}  {model}")


if __name__ == "__main__":
    main()
