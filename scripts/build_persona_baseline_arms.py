#!/usr/bin/env python3
"""Build the arms that separate "the persona moved" from "the product moved".

Two changes landed on the persona pool at once. Values changed on 14 dimensions
-- five of them tier A, two on more than half the pool -- and the prompt tier is
about to shrink from 48 fields to 18. Either one alone breaks comparison with
every earlier run: a later score would mix product movement with a shifted
definition of who is doing the scoring, and nothing separates them after the
fact.

So run the old and new definitions side by side, on the same day, against the
same endpoint. The difference between arms is the persona shift; whatever is
left over is the product.

    old48   pool before the change, all 48 fields   <- reproduces earlier runs
    new48   pool after the change, all 48 fields    <- isolates the value change
    old18   pool before, prompt tier only           <- isolates the field cut
    new18   pool after, prompt tier only            <- the proposed future state

A fifth arm exists because vn_voice_privacy_comfort carries two changes at once:
it entered the prompt tier in this commit AND its value moved on 30 of 42
personas. Summed with everything else those two are not separable, so new18-vpc
is new18 with that one field held at its old value. new18 minus new18-vpc is
that field's contribution, alone.

    uv run python scripts/build_persona_baseline_arms.py --dry-run
    uv run python scripts/build_persona_baseline_arms.py --intent cabin-vehicle-control
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from persona_tiers import PROMPT_FIELDS, persona_paths  # noqa: E402

#: The pool as it stood before the tiering and rule work. Anything measured
#: before 2026-09-09 was measured against this.
OLD_REV = "110fd46"

#: Entered the prompt tier and changed value in the same commit.
DOUBLE_CHANGED = "vn_voice_privacy_comfort"

STAGE1_USD, STAGE1_SEC = 0.008, 12.2
STAGE2_USD, STAGE2_SEC = 0.0101, 75.0


def read_old_pool(pool_rel: str) -> dict[str, dict[str, Any]]:
    """The pre-change pool, read from git rather than from a directory."""
    listing = subprocess.run(
        ["git", "ls-tree", "--name-only", OLD_REV, pool_rel + "/"],
        capture_output=True, text=True, check=True, cwd=REPO_ROOT).stdout.split()
    out = {}
    for name in listing:
        if not name.endswith(".yaml") or "/persona_" not in name:
            continue
        if name.endswith(".prompt.yaml"):
            continue
        raw = subprocess.run(["git", "show", f"{OLD_REV}:{name}"],
                             capture_output=True, text=True, check=True,
                             cwd=REPO_ROOT).stdout
        doc = yaml.safe_load(raw) or {}
        out[Path(name).name] = doc
    return out


def restrict(doc: dict[str, Any], keep: tuple[str, ...] | None) -> dict[str, Any]:
    if keep is None:
        return doc
    allow = set(keep)
    out = dict(doc)
    out["dimensions"] = {k: v for k, v in (doc.get("dimensions") or {}).items()
                         if k in allow}
    out["grounding"] = {k: v for k, v in (doc.get("grounding") or {}).items()
                        if k in allow}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pool", default="persona/datasets/vn-drivers")
    ap.add_argument("--personas", type=int, default=0, help="0 = the whole pool")
    ap.add_argument("--intent", action="append", default=[], dest="intents")
    ap.add_argument("--out-root", type=Path,
                    default=Path("persona/datasets/vn-drivers-baseline"))
    ap.add_argument("--stage2", action="store_true",
                    help="price the multiturn stage as well as stimulus generation")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    new_paths = persona_paths(REPO_ROOT / args.pool)
    new_pool = {p.name: yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                for p in new_paths}
    old_pool = read_old_pool(args.pool)

    shared = sorted(set(new_pool) & set(old_pool))
    if args.personas:
        shared = shared[: args.personas]
    if not shared:
        print("no personas common to {} and {}".format(OLD_REV, args.pool))
        return 1

    moved = sum(
        1 for n in shared
        if (old_pool[n].get("dimensions") or {}).get(DOUBLE_CHANGED)
        != (new_pool[n].get("dimensions") or {}).get(DOUBLE_CHANGED)
    )

    arms = {
        "old48": (old_pool, None, None),
        "new48": (new_pool, None, None),
        "old18": (old_pool, PROMPT_FIELDS, None),
        "new18": (new_pool, PROMPT_FIELDS, None),
        "new18-vpc": (new_pool, PROMPT_FIELDS, DOUBLE_CHANGED),
    }

    all_intents = sorted(
        p.name.replace("survey_vita-utterance-", "")
        for p in (REPO_ROOT / "application" / "tasks").glob("survey_vita-utterance-*")
    )
    intents = args.intents or all_intents

    print("{} personas common to both pools, {} intent(s)".format(len(shared), len(intents)))
    print("{} of {} differ on {}\n".format(moved, len(shared), DOUBLE_CHANGED))
    print("{:<12}{:>8}  {}".format("arm", "fields", "what it isolates"))
    notes = {
        "old48": "the definition every earlier run used",
        "new48": "value changes only",
        "old18": "field cut only",
        "new18": "both, as proposed",
        "new18-vpc": "new18 with {} held old".format(DOUBLE_CHANGED),
    }
    for tag, (pool, keep, _) in arms.items():
        n = len(PROMPT_FIELDS) if keep else len(
            (pool[shared[0]].get("dimensions") or {}))
        print("{:<12}{:>8}  {}".format(tag, n, notes[tag]))

    trials = len(arms) * len(shared) * len(intents)
    cost = trials * STAGE1_USD
    hours = trials * STAGE1_SEC / 3600
    print("\nstage 1: {} trials  ${:.2f}  ~{:.1f}h serial".format(trials, cost, hours))
    if args.stage2:
        c2, h2 = trials * STAGE2_USD, trials * STAGE2_SEC / 3600
        print("stage 2: {} conversations  ${:.2f}  ~{:.1f}h serial".format(trials, c2, h2))
        print("total  : ${:.2f}".format(cost + c2))

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0

    if args.out_root.exists():
        shutil.rmtree(args.out_root)
    for tag, (pool, keep, hold) in arms.items():
        target = args.out_root / tag
        target.mkdir(parents=True, exist_ok=True)
        for extra in (REPO_ROOT / args.pool).iterdir():
            if extra.is_file() and not extra.name.startswith("persona_"):
                shutil.copy2(extra, target / extra.name)
        for name in shared:
            doc = restrict(pool[name], keep)
            if hold:
                doc = dict(doc)
                dims = dict(doc.get("dimensions") or {})
                dims[hold] = (old_pool[name].get("dimensions") or {}).get(hold)
                doc["dimensions"] = dims
            (target / name).write_text(
                yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
                encoding="utf-8")

    manifest = {
        "old_rev": OLD_REV,
        "pool": args.pool,
        "personas": shared,
        "intents": intents,
        "arms": {t: notes[t] for t in arms},
        "double_changed_field": DOUBLE_CHANGED,
        "double_changed_personas": moved,
        "stage1_trials": trials,
        "stage1_usd": round(cost, 2),
    }
    (args.out_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\nwrote {} arms to {}".format(len(arms), args.out_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
