#!/usr/bin/env python3
"""Turn a stage-1 utterance dataset into a stage-2 multi-turn job recipe.

Stage 1 runs a survey that produces ``scenario`` + ``first_input`` rows (see
``scripts/export_vita_utterances.py``). This script binds one row to one
multi-turn trial: each row becomes an agent entry carrying both the persona
that produced it and the row itself, so the conversation opens on a fixed
stimulus instead of a need the persona invents on the spot.

Usage:
    uv run python scripts/generate_vita_multiturn_job.py jobs/vita-nav-vi50/dataset.csv \\
        --job-name vita-multiturn-n10 --limit 10 -o configs/jobs/application-task-job-recipe/vita-multiturn-n10.yaml

Then:
    export OPENROUTER_API_KEY=...
    uv run matraix run -c configs/jobs/application-task-job-recipe/vita-multiturn-n10.yaml
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from persona_tiers import persona_paths  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from matraix.persona_agent_context import (  # noqa: E402
    apply_persona_context_to_agent_spec,
)

DEFAULT_TASK = "application/tasks/chat_vita-drive-assistant"
DEFAULT_AGENT = "persona-user-sim"
# The model id belongs to whichever endpoint OPENROUTER_API_BASE points at --
# OpenRouter wants "google/gemini-...", Google's own OpenAI-compatible endpoint
# 404s on that and wants the bare id. Reading the env keeps one repo working
# against both, the way the locale-pack scripts already do.
DEFAULT_MODEL = os.environ.get(
    "MATRIX_PERSONA_MODEL", "openrouter/google/gemini-3.5-flash-lite"
)
PERSONA_ROOT = "persona/datasets"

# Columns copied onto the seed. Everything else in the workbook is provenance
# that the trial does not need in order to open the conversation.
SEED_COLUMNS = (
    "scenario",
    "first_input",
    "intent_code",
    "subintent_code",
    "subintent_name",
    "vehicle_state",
    "ASSISTANT_MODE",
    "persona_id",
)


class PersonaLookupError(RuntimeError):
    """Raised when a dataset row names a persona with no file on disk."""


def build_persona_index(repo_root: Path, pool: str | None = None) -> dict[str, str]:
    """Map ``persona_id`` -> repo-relative yaml path.

    The same persona can appear in several cohorts; take the lexicographically
    first path so a given dataset always generates the same job.

    That tie-break is silent, though, and once two pools hold the same
    persona_ids -- an original and a revised copy -- it always resolves to
    whichever sorts first, with no way to ask for the other. ``pool`` names the
    directory under ``persona/datasets`` to search instead.
    """
    root = repo_root / PERSONA_ROOT / pool if pool else repo_root / PERSONA_ROOT
    if not root.is_dir():
        raise PersonaLookupError("persona pool not found: {}".format(root))
    index: dict[str, str] = {}
    for path in persona_paths(root, recursive=True):
        persona_id = path.stem[len("persona_") :]
        index.setdefault(persona_id, str(path.relative_to(repo_root)))
    return index


def seed_from_row(row: dict[str, str], *, row_id: str) -> dict[str, str]:
    seed: dict[str, str] = {"row_id": row_id}
    for column in SEED_COLUMNS:
        value = (row.get(column) or "").strip()
        if value:
            seed[column] = value
    return seed


def round_robin_by_persona(
    selected: list[tuple[int, dict[str, str]]],
) -> list[tuple[int, dict[str, str]]]:
    """Interleave rows across personas, preserving each persona's own order.

    The workbook groups all of one persona's rows together, so any prefix-based
    cap lands entirely inside the first persona -- a 10-trial sample would test
    one person instead of eight. Interleaving first makes small samples cover
    the population. Deterministic: no shuffling, no RNG.
    """
    buckets: dict[str, list[tuple[int, dict[str, str]]]] = {}
    for item in selected:
        key = (item[1].get("persona_id") or "").strip()
        buckets.setdefault(key, []).append(item)
    order = sorted(buckets)
    out: list[tuple[int, dict[str, str]]] = []
    for position in range(max((len(b) for b in buckets.values()), default=0)):
        for key in order:
            bucket = buckets[key]
            if position < len(bucket):
                out.append(bucket[position])
    return out


def select_rows(
    rows: list[dict[str, str]],
    *,
    subintents: list[str] | None,
    intents: list[str] | None,
    limit: int | None,
    per_subintent: int | None,
    spread_personas: bool = True,
    n_personas: int | None = None,
) -> list[tuple[int, dict[str, str]]]:
    """Filter and cap rows. Deterministic: same dataset + flags -> same job."""
    keep_personas: set[str] | None = None
    if n_personas is not None:
        # First N in dataset order, so the same dataset always yields the same
        # subset -- a sampled pilot has to be repeatable to be worth anything.
        ordered: list[str] = []
        for row in rows:
            persona_id = (row.get("persona_id") or "").strip()
            if persona_id and persona_id not in ordered:
                ordered.append(persona_id)
        keep_personas = set(ordered[:n_personas])

    selected: list[tuple[int, dict[str, str]]] = []
    for index, row in enumerate(rows):
        if subintents and (row.get("subintent_code") or "").strip() not in subintents:
            continue
        if intents and (row.get("intent_code") or "").strip() not in intents:
            continue
        if keep_personas is not None:
            if (row.get("persona_id") or "").strip() not in keep_personas:
                continue
        selected.append((index, row))

    if spread_personas:
        selected = round_robin_by_persona(selected)

    if per_subintent is not None:
        # Spread coverage across subintents rather than taking a prefix that
        # may land entirely inside one of them.
        counts: dict[str, int] = {}
        capped: list[tuple[int, dict[str, str]]] = []
        for index, row in selected:
            key = (row.get("subintent_code") or "").strip()
            if counts.get(key, 0) >= per_subintent:
                continue
            counts[key] = counts.get(key, 0) + 1
            capped.append((index, row))
        selected = capped

    if limit is not None:
        selected = selected[:limit]
    return selected


def build_agents(
    selected: list[tuple[int, dict[str, str]]],
    *,
    persona_index: dict[str, str],
    agent_name: str,
    model_name: str,
) -> list[dict[str, Any]]:
    agents: list[dict[str, Any]] = []
    missing: set[str] = set()
    for index, row in selected:
        persona_id = (row.get("persona_id") or "").strip()
        persona_path = persona_index.get(persona_id)
        if persona_path is None:
            missing.add(persona_id or "<empty>")
            continue
        agents.append(
            apply_persona_context_to_agent_spec(
                {
                    "name": agent_name,
                    "model_name": model_name,
                    "kwargs": {
                        "persona_path": persona_path,
                        "seed": seed_from_row(row, row_id="row-{:04d}".format(index)),
                    },
                },
                model_name=model_name,
            )
        )
    if missing:
        raise PersonaLookupError(
            "no persona yaml under {} for id(s): {}".format(
                PERSONA_ROOT, ", ".join(sorted(missing))
            )
        )
    return agents


def header_comment(
    *,
    dataset: Path,
    task: str,
    agent_name: str,
    model_name: str,
    total_rows: int,
    n_agents: int,
    dropped: int,
    out_path: Path,
) -> str:
    lines = [
        "# Generated by scripts/generate_vita_multiturn_job.py",
        "# Dataset: {} ({} rows)".format(dataset, total_rows),
        "# Task: {}".format(task),
        "# Agent: {} | model: {}".format(agent_name, model_name),
        "# Trials: {} (1 multi-turn conversation per dataset row)".format(n_agents),
    ]
    if dropped:
        lines.append(
            "# Rows not selected: {} (filtered or capped -- see --limit/--subintent)".format(
                dropped
            )
        )
    lines += [
        "#",
        "# Each agent entry carries kwargs.seed = the row it replays. The persona",
        "# rephrases first_input in its own voice, then continues the conversation",
        "# on its own. Unseeded runs let the persona invent a need instead.",
        "#",
        "# Run:",
        "#   set -a; source application/playground/.env.local; set +a",
        "#   export MATRIX_CHATBOT_TASK_PATH={}".format(task),
        "#   export VITA_ASSISTANT_API_URL=http://127.0.0.1:3001   # the app under test",
        "#   uv run matraix run -c {}".format(out_path),
        "#",
        "# MATRIX_CHATBOT_TASK_PATH is required: the chat adapter reads the task",
        "# from the environment, not from the tasks: entry below.",
        "#",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="stage-1 dataset.csv")
    parser.add_argument("-o", "--out", type=Path, required=True, help="job recipe yaml")
    parser.add_argument("--job-name", default="vita-multiturn")
    parser.add_argument("--task", default=DEFAULT_TASK)
    parser.add_argument("--agent", default=DEFAULT_AGENT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--limit", type=int, help="cap total trials")
    parser.add_argument(
        "--per-subintent",
        type=int,
        help="cap trials per subintent_code before --limit applies",
    )
    parser.add_argument(
        "--subintent",
        action="append",
        dest="subintents",
        help="keep only these subintent_code values (repeatable)",
    )
    parser.add_argument(
        "--intent",
        action="append",
        dest="intents",
        help="keep only these intent_code values (repeatable)",
    )
    parser.add_argument(
        "--no-spread-personas",
        dest="spread_personas",
        action="store_false",
        help=(
            "take rows in raw dataset order instead of interleaving personas; "
            "a small --limit then covers only the first persona"
        ),
    )
    parser.add_argument(
        "--n-personas",
        type=int,
        help="keep only the first N personas in dataset order (all their rows)",
    )
    parser.add_argument("--n-concurrent", type=int, default=1)
    parser.add_argument(
        "--persona-pool",
        help=(
            "directory under persona/datasets to resolve personas from; "
            "without it the first pool in sort order silently wins"
        ),
    )
    parser.add_argument("--jobs-dir", default="jobs")
    args = parser.parse_args()

    # utf-8-sig reads both BOM-prefixed and plain UTF-8; plain utf-8 would turn
    # the first header into "﻿intent_code" and silently blank that column.
    with args.dataset.open(encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        parser.error("dataset {} has no rows".format(args.dataset))

    selected = select_rows(
        rows,
        subintents=args.subintents,
        intents=args.intents,
        limit=args.limit,
        per_subintent=args.per_subintent,
        spread_personas=args.spread_personas,
        n_personas=args.n_personas,
    )
    if not selected:
        parser.error("no rows left after filtering")

    try:
        agents = build_agents(
            selected,
            persona_index=build_persona_index(REPO_ROOT, args.persona_pool),
            agent_name=args.agent,
            model_name=args.model,
        )
    except PersonaLookupError as exc:
        parser.error(str(exc))

    job = {
        "job_name": args.job_name,
        "jobs_dir": args.jobs_dir,
        "n_attempts": 1,
        "timeout_multiplier": 1.0,
        "n_concurrent_trials": args.n_concurrent,
        "quiet": False,
        "environment": {"type": "host", "delete": True},
        "agents": agents,
        "tasks": [{"path": args.task}],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    body = yaml.safe_dump(job, sort_keys=False, allow_unicode=True, width=100)
    args.out.write_text(
        header_comment(
            dataset=args.dataset,
            task=args.task,
            agent_name=args.agent,
            model_name=args.model,
            total_rows=len(rows),
            n_agents=len(agents),
            dropped=len(rows) - len(selected),
            out_path=args.out,
        )
        + body,
        encoding="utf-8",
    )

    subintents = sorted({(r.get("subintent_code") or "").strip() for _, r in selected})
    personas = sorted({(r.get("persona_id") or "").strip() for _, r in selected})
    print("wrote {}".format(args.out))
    print("  trials    : {} (from {} dataset rows)".format(len(agents), len(rows)))
    print("  personas  : {}".format(len(personas)))
    print("  subintents: {}".format(", ".join(subintents)))
    print("  model     : {}".format(args.model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
