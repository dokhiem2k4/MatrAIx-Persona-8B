"""Generate a job recipe whose trials are persona x case pairs.

    uv run python application/scripts/generate_vita_case_job.py \
        --job-name appSim-0709-vita-golden-error-recovery-smoke-baseline \
        --model-name openrouter/anthropic/claude-haiku-4.5 \
        --personas persona/datasets/matraix-persona-dev-sample/persona_0042.yaml \
        --smoke-per-error-type 2

Pass ``--all-cases`` instead of ``--smoke-per-error-type`` for the full sweep.
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from application.scripts.vita_case_jobs import pairs_from_agents  # noqa: E402
from application.scripts.vita_run_manifest import (  # noqa: E402
    build_manifest,
    check_drift,
    load_manifest,
    manifest_path_for,
    replay_pairs,
    write_manifest,
)


def _int_or_none(value: str | None) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None

# Which credential each provider prefix needs. Checked before a run, never
# during one: a job that dies on a missing key still burns wall clock and,
# depending on the provider, tokens for the trials that did start.
CREDENTIAL_ENV_BY_PREFIX = {
    "openrouter/": "OPENROUTER_API_KEY",
    "anthropic/": "ANTHROPIC_API_KEY",
    "openai/": "OPENAI_API_KEY",
    "dashscope/": "DASHSCOPE_API_KEY",
}


def credential_env_for_model(model_name: str) -> str | None:
    """Return the env var this model needs, or ``None`` when unknown."""
    value = (model_name or "").strip()
    for prefix, env_name in CREDENTIAL_ENV_BY_PREFIX.items():
        if value.startswith(prefix):
            return env_name
    return None


def resolve_model_name(explicit: str | None, env: Mapping[str, str]) -> str:
    """Explicit flag wins, else fall back to the configured persona model."""
    value = (explicit or "").strip() or str(env.get("MATRIX_PERSONA_MODEL") or "").strip()
    if not value:
        raise SystemExit(
            "no model: pass --model-name or set MATRIX_PERSONA_MODEL "
            "(application/playground/.env.local)"
        )
    return value
DEFAULT_TASK_PATH = "application/tasks/chat_0709-vita-drive-golden-error-recovery"

# Which field to spread a capped sample across, per task. The golden set is
# organised by failure mode; the multi-turn set has one case per subintent and
# no error_type at all, so spreading it by parent intent is the only way a
# half-size run still touches every area of the product.
STRATA_FIELD_BY_TASK = {
    "chat_0709-vita-drive-golden-error-recovery": "error_type",
    "chat_0709-vita-drive-multiturn-coverage": "parent_intent_code",
    "chat_0709-vita-drive-singleturn-mode-ab": "assistant_profile_id",
    # The discovery guide's own axis: eight capability groups, and a capped run
    # that missed one of them would leave a whole area of the product untested.
    "chat_0909-vita-discovery-ces": "capability_number",
    # Four ways of meeting the assistant for the first time. A capped run that
    # dropped one would measure the brand through fewer kinds of encounter.
    "chat_0909-vita-brand-recognition": "encounter_code",
}


def strata_field(task_path: str) -> str:
    """Field a capped sample is dealt across for this task."""
    return STRATA_FIELD_BY_TASK.get(task_path.rstrip("/").rsplit("/", 1)[-1], "error_type")


def case_stratum(case: dict[str, Any], field: str) -> str:
    """Read the stratum value, looking inside ``state`` when it lives there."""
    if field in case:
        return str(case[field])
    return str((case.get("state") or {}).get(field, ""))
RECIPE_DIR = REPO_ROOT / "configs/jobs/application-task-job-recipe"


def load_case_ids(
    *,
    task_path: str = DEFAULT_TASK_PATH,
    per_error_type: int | None = None,
    max_cases: int | None = None,
) -> list[str]:
    """Return case ids, sampled so every error type stays represented.

    ``max_cases`` deals the cases round-robin across error types rather than
    taking the first N: the dataset is ordered, so a plain head would return
    only two or three of the ten error types and the run would answer nothing
    about the rest.
    """
    path = REPO_ROOT / task_path / "input" / "cases.jsonl"
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if per_error_type is None and max_cases is None:
        return [case["case_id"] for case in cases]

    field = strata_field(task_path)
    by_stratum: dict[str, list[str]] = collections.defaultdict(list)
    for case in cases:
        by_stratum[case_stratum(case, field)].append(case["case_id"])
    buckets = [sorted(ids) for _, ids in sorted(by_stratum.items())]

    if per_error_type is not None:
        return list(itertools.chain.from_iterable(b[:per_error_type] for b in buckets))

    picked: list[str] = []
    for index in range(max(len(b) for b in buckets)):
        for bucket in buckets:
            if index < len(bucket):
                picked.append(bucket[index])
                if len(picked) == max_cases:
                    return picked
    return picked


def build_recipe(
    *,
    job_name: str,
    model_name: str,
    persona_paths: list[str],
    case_ids: list[str],
    task_path: str = DEFAULT_TASK_PATH,
    concurrency: int = 6,
    pairs: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    from application.scripts.vita_case_jobs import build_case_agent_entries, build_pair_agent_entries

    agents = (
        build_pair_agent_entries(pairs, model_name)
        if pairs is not None
        else build_case_agent_entries(persona_paths, case_ids, model_name)
    )
    return {
        "job_name": job_name,
        "jobs_dir": "jobs",
        "n_attempts": 1,
        "timeout_multiplier": 1.0,
        "n_concurrent_trials": concurrency,
        "quiet": False,
        # host, not docker. A chat trial drives an external HTTP SUT and needs
        # no sandbox of its own; inside the docker environment the trial
        # container cannot resolve DNS, so every SUT call dies with
        # "Temporary failure in name resolution". This mirrors what the
        # Playground backend emits for the user_sim_chat trial profile.
        "environment": {"type": "host", "delete": True},
        "agents": agents,
        "tasks": [{"path": task_path}],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--task", default=DEFAULT_TASK_PATH, help="task path to run")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=6,
        help=(
            "trials in flight at once. Costs the same either way; it only trades "
            "wall time for load on the system under test."
        ),
    )
    parser.add_argument("--model-name", default=None)
    parser.add_argument("--personas", nargs="+", help="required unless --replay is given")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--smoke-per-error-type", type=int)
    group.add_argument("--all-cases", action="store_true")
    group.add_argument(
        "--max-cases", type=int, help="cap the case count, dealt across error types"
    )
    group.add_argument(
        "--replay",
        type=Path,
        help=(
            "manifest from an earlier run: re-run that run's exact persona x case "
            "pairs, so the two runs can be compared. Takes the task and the "
            "personas from the manifest, so --task and --personas are not needed."
        ),
    )
    parser.add_argument(
        "--allow-drift",
        action="store_true",
        help=(
            "replay even though personas or cases changed since the run being "
            "replayed. The comparison is then between two different experiments."
        ),
    )
    args = parser.parse_args()

    model_name = resolve_model_name(args.model_name, os.environ)

    if args.replay:
        manifest = load_manifest(args.replay)
        # Replaying under a different task path would rebind every case id to a
        # different dataset, silently.
        args.task = str(manifest.get("task_path") or args.task)
        pairs = replay_pairs(manifest)
        case_ids = list(dict.fromkeys(case_id for _, case_id in pairs))
        persona_paths = list(
            dict.fromkeys(persona_path for persona_path, _ in pairs)
        )
        drift = check_drift(manifest)
        if drift:
            print("drift since {}:".format(manifest.get("run_name") or args.replay))
            for problem in drift:
                print("  - {}".format(problem))
            if not args.allow_drift:
                raise SystemExit(
                    "refusing to replay: the stimulus is no longer the one that run "
                    "faced, so a before/after difference would not be the "
                    "assistant's. Pass --allow-drift to run anyway."
                )
        print(
            "replaying {}: {} trials, {} personas, {} cases".format(
                manifest.get("run_name") or args.replay.name,
                len(pairs),
                len(persona_paths),
                len(case_ids),
            )
        )
    else:
        pairs = None
        if not args.personas:
            raise SystemExit("--personas is required unless --replay is given")
        persona_paths = list(args.personas)
        case_ids = load_case_ids(
            task_path=args.task,
            per_error_type=(
                None if (args.all_cases or args.max_cases) else args.smoke_per_error_type
            ),
            max_cases=args.max_cases,
        )

    for persona in persona_paths:
        if not (REPO_ROOT / persona).is_file():
            raise SystemExit("persona file not found: {}".format(persona))

    recipe = build_recipe(
        job_name=args.job_name,
        model_name=model_name,
        persona_paths=persona_paths,
        case_ids=case_ids,
        task_path=args.task,
        concurrency=args.concurrency,
        pairs=pairs,
    )
    RECIPE_DIR.mkdir(parents=True, exist_ok=True)
    path = RECIPE_DIR / "{}.yaml".format(args.job_name)
    header = (
        "# Generated by application/scripts/generate_vita_case_job.py\n"
        "# Task: {}\n"
        "# Trial = 1 persona x 1 case | personas={} cases={} trials={}\n"
        "# Persona model: {}\n\n".format(
            args.task,
            len(persona_paths),
            len(case_ids),
            len(recipe["agents"]),
            model_name,
        )
    )
    path.write_text(header + yaml.safe_dump(recipe, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print("wrote {} ({} trials)".format(path, len(recipe["agents"])))

    # Written now, not after the run: a run that dies halfway still needs a
    # record of what it was asked to do, and this is also what a later replay
    # reads. It costs nothing and is the only artifact that makes a
    # before/after comparison possible.
    manifest = build_manifest(
        run_name=args.job_name,
        task_path=args.task,
        model_name=model_name,
        persona_paths=persona_paths,
        case_ids=case_ids,
        pairs=pairs_from_agents(recipe["agents"]),
        max_turns=_int_or_none(os.environ.get("MATRIX_CHATBOT_MAX_TURNS")),
        sut_base_url=os.environ.get("VITA_ASSISTANT_API_URL", ""),
    )
    manifest_file = write_manifest(manifest, manifest_path_for(args.job_name))
    print(
        "wrote {} ({} personas x {} cases)".format(
            manifest_file, len(manifest["personas"]), len(manifest["cases"])
        )
    )

    needed = credential_env_for_model(model_name)
    if needed is None:
        print("model {}: unknown provider, cannot check credentials".format(model_name))
    elif os.environ.get(needed, "").strip():
        print("model {}: {} is set".format(model_name, needed))
    else:
        print(
            "model {}: {} is NOT set -- this job would fail. "
            "Fix it before running, not after.".format(model_name, needed)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
