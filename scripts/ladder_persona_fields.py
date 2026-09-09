#!/usr/bin/env python3
"""Ask what a persona loses when you take fields away, one rung at a time.

The per-field ablation answers "does flipping X change the output". That is not
the question a reviewer asks. Theirs is simpler and harder: if a persona
carried six fields instead of forty-eight, would the driver say anything
different? A field can be individually live and still redundant, because three
neighbours already say the same thing about the same person.

So this builds a ladder rather than a set of flips. Each rung is the same pool
with a smaller field set, and the rungs nest: everything in rung 6 is in rung
12. Compare each rung against the full profile and the answer is a curve, not a
verdict -- the rung where the curve meets the noise floor is the smallest
profile that still writes the same utterances.

Fields are ordered by entropy over the pool, which is the only ranking
available before spending anything: a field with one value across every persona
cannot change an utterance no matter how important it sounds. Axes named in
KEEP_FIRST are pinned to the front regardless, because a rung that drops the
accent or who is in the car stops being a driver profile at all.

The full profile is emitted twice (base-a, base-b). Rerunning one prompt already
changes the text, and a rung that differs from the base by less than that has
not been shown to differ at all.

    uv run python scripts/ladder_persona_fields.py --dry-run
    uv run python scripts/ladder_persona_fields.py --rungs 6,12,24 --personas 3 \
        --intent cabin-vehicle-control --out-dir data/ladder
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from persona_tiers import persona_paths  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

#: Pinned to the front of the ranking. Losing any of these stops the profile
#: describing a driver: who they are, how they sound, and who is listening.
KEEP_FIRST = (
    "age_bracket",
    "gender_identity",
    "accent_region",
    "vn_address_register",
    "demo_driver_status",
    "vn_usual_companion",
)


def entropy(counter: collections.Counter) -> float:
    total = sum(counter.values())
    if total <= 0:
        return 0.0
    return -sum(
        (n / total) * math.log2(n / total) for n in counter.values() if n
    )


def rank_fields(pool: list[dict[str, Any]]) -> list[str]:
    """Pinned axes first, then everything else by entropy, high to low."""
    keys = sorted({k for p in pool for k in p})
    scored = {
        key: entropy(collections.Counter(str(p.get(key)) for p in pool))
        for key in keys
    }
    pinned = [k for k in KEEP_FIRST if k in scored]
    rest = sorted(
        (k for k in scored if k not in pinned),
        key=lambda k: (-scored[k], k),
    )
    return pinned + rest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pool", default="vn-drivers")
    ap.add_argument("--rungs", default="6,12,24",
                    help="field counts to test, comma separated")
    ap.add_argument("--personas", type=int, default=3)
    ap.add_argument("--intent", action="append", default=[], dest="intents")
    ap.add_argument("--out-dir", type=Path, default=Path("data/ladder"))
    ap.add_argument("--job-prefix", default="lad")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pool_dir = REPO_ROOT / "persona" / "datasets" / args.pool
    paths = persona_paths(pool_dir)[: args.personas]
    docs = [(p, yaml.safe_load(p.read_text(encoding="utf-8")) or {}) for p in paths]
    dims = [d.get("dimensions") or {} for _, d in docs]
    order = rank_fields(dims)
    rungs = sorted({int(x) for x in args.rungs.split(",") if x.strip()})

    print("{} personas, {} fields, ranking by entropy with {} pinned\n".format(
        len(docs), len(order), len(KEEP_FIRST)))
    print("{:>4}  {}".format("rung", "fields kept (first few)"))
    for n in rungs:
        kept = order[:n]
        print("{:>4}  {}{}".format(
            n, ", ".join(kept[:6]), " ..." if len(kept) > 6 else ""))
    print("\nfull profile = {} fields, emitted twice as the noise floor".format(len(order)))

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0

    abl_root = REPO_ROOT / "persona" / "datasets" / "{}-lad".format(args.pool)
    if abl_root.exists():
        shutil.rmtree(abl_root)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    def write_arm(tag: str, keep: list[str] | None) -> None:
        target = abl_root / tag
        target.mkdir(parents=True, exist_ok=True)
        for extra in pool_dir.iterdir():
            if extra.is_file() and not extra.name.startswith("persona_"):
                shutil.copy2(extra, target / extra.name)
        for path, data in docs:
            out = dict(data)
            if keep is not None:
                allow = set(keep)
                out["dimensions"] = {
                    k: v for k, v in (data.get("dimensions") or {}).items() if k in allow
                }
                out["grounding"] = {
                    k: v for k, v in (data.get("grounding") or {}).items() if k in allow
                }
            (target / path.name).write_text(
                yaml.safe_dump(out, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )

    arms = []
    write_arm("base-a", None)
    write_arm("base-b", None)
    for n in rungs:
        tag = "rung-{:02d}".format(n)
        write_arm(tag, order[:n])
        # score_persona_ablation.py keys on tag + mutated_dimension, so a rung
        # borrows that shape: the "dimension" it reports is the rung itself.
        arms.append({
            "tag": tag,
            "mutated_dimension": "{} fields".format(n),
            "fields": n,
            "kept": order[:n],
        })

    manifest = {
        "pool": args.pool,
        "personas": [d.get("persona_id") for _, d in docs],
        "intents": args.intents,
        "noise_floor_arms": ["base-a", "base-b"],
        "full_field_count": len(order),
        "arms": arms,
    }
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    all_intents = sorted(
        p.name.replace("survey_vita-utterance-", "")
        for p in (REPO_ROOT / "application" / "tasks").glob("survey_vita-utterance-*")
    )
    skips = [i for i in all_intents if args.intents and i not in args.intents]

    lines = ["#!/usr/bin/env bash", "set -eu", 'cd "$(dirname "$0")/../.."', ""]
    for tag in ["base-a", "base-b"] + [a["tag"] for a in arms]:
        job = "{}-{}".format(args.job_prefix, tag)
        lines += [
            "echo '### arm {}'".format(tag),
            "uv run python scripts/generate_vita_stage1_jobs.py \\",
            "  " + " ".join("--persona={}".format(d.get("persona_id")) for _, d in docs) + " \\",
            "  --persona-pool {}-lad/{} \\".format(args.pool, tag),
            "  --out-dir configs/jobs/{} \\".format(job),
            "  --job-prefix {}{}".format(job, " \\" if skips else ""),
            *(["  " + " ".join("--skip-intent={}".format(s) for s in skips)] if skips else []),
            "for cfg in configs/jobs/{}/*.yaml; do".format(job),
            '  intent=$(basename "$cfg" .yaml | sed "s/^{}-//")'.format(job),
            '  export MATRIX_SURVEY_TASK_PATH="application/tasks/survey_vita-utterance-${intent}"',
            '  uv run matraix run -c "$cfg" 2>&1 | tail -2',
            "done",
            "uv run python scripts/merge_vita_datasets.py jobs/{}-* -o {}/{}.csv".format(
                job, args.out_dir, tag),
            "",
        ]
    runner = args.out_dir / "run_arms.sh"
    runner.write_text("\n".join(lines), encoding="utf-8")
    runner.chmod(0o755)

    total = (2 + len(rungs)) * max(len(args.intents) or len(all_intents), 1) * len(docs)
    print("\nbuilt {} arms (2 noise + {} rungs) for {} personas".format(
        2 + len(rungs), len(rungs), len(docs)))
    print("  pools    : {}".format(abl_root))
    print("  run      : bash {}".format(runner))
    print("  score    : uv run python scripts/score_persona_ablation.py {}".format(args.out_dir))
    print("  ~{} stage-1 trials at $0.008 = ${:.2f}".format(total, total * 0.008))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
