#!/usr/bin/env python3
"""Cut a persona pool down to the fields that actually do work.

A persona carries 1,297 dimensions of which 24 are answers a person gave. The
remaining 1,272 are sampled *conditioned on those 24*, so they add no
information about a real person -- the variance they do add is sampling noise,
which is worse than adding nothing when it reaches a prompt.

The kept set comes from asking what each field is for. A field earns its place
by doing one of three jobs:

  sample       decides who belongs in the pool (age, locality, income band)
  condition    steers the model's output (patience, register, task scope)
  present      lets a reader understand the persona (name, employment)

Everything else -- 145 developer-tooling fields inherited from a DAG built for
programmers, 143 professional-familiarity scores, 109 psychometric items, and
the genre and cuisine blocks -- serves none of the three for a driver talking
to a car.

Two deliberate departures from a strict "cut what carries no bits" rule:

  Five observed fields are constant across the pool (region, primary_language,
  lang_vietnamese, cult_vietnam, demo_citizenship_status). They condition
  nothing, but they are evidence a person supplied, and discarding measured
  data to save five slots out of forty is the wrong trade.

  Conversation-layer fields (intent, emotional_state, query_complexity,
  time_pressure) are cut despite having the highest variance in the catalog.
  They change per turn; freezing them into a persona means one who is
  permanently anxious, which is a bug wearing the costume of a trait.

Usage:
    uv run python scripts/trim_persona_fields.py persona/datasets/vn-drivers
    uv run python scripts/trim_persona_fields.py <pool> --out <other-pool>
    uv run python scripts/trim_persona_fields.py <pool> --dry-run
"""

from __future__ import annotations

import argparse
import collections
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from persona_tiers import persona_paths  # noqa: E402

#: Who belongs in the pool. These pick the 42; they barely steer an answer.
SAMPLING = (
    "age_bracket",
    "gender_identity",
    "vn_locality",
    "urbanicity",
    "socioeconomic_band",
    "highest_education",
    "demo_employment_status",
    "demo_marital_status",
    "demo_children_count",
    "life_stage",
)

#: What steers the answer: content, form, and the thresholds for giving up.
CONDITIONING = (
    "demo_driver_status",
    "skill_driving",
    "lstyle_commute_mode",
    "topic_cars",
    "att_electric_vehicles",
    "att_self_driving_cars",
    "att_voice_assistant",
    "vn_usual_companion",
    "vn_assistant_task_scope",
    "vn_voice_privacy_comfort",
    "vn_retry_tolerance",
    "vn_address_register",
    "cog_patience",
    "cog_skepticism",
    "cog_verbosity",
    "cog_formality",
    "tone_expected",
    "english_proficiency",
    "trust_level",
    "safety_sensitivity",
    "tech_savviness",
    # Second 2026 round: the car, the trip, and the conditions in the cabin.
    # The audit called these the emptiest part of the persona -- a driver whose
    # record says nothing about what they drive or where.
    "accent_region",
    "veh_class",
    "veh_assistant_builtin",
    "drv_exposure",
    "trip_mix",
    "assistant_usage_freq",
    "need_state",
    "cabin_context",
    "cabin_noise",
)

#: Neither samples nor conditions: these let a reader tell one persona from
#: another at a glance, which is the third job a field can do. The playground
#: card is built from them, so cutting them empties the browse grid.
PRESENTATION = (
    "domain",
)

#: Carries no variance, but a person answered it. Kept as evidence, not signal.
MEASURED_CONSTANT = (
    "region",
    "primary_language",
    "lang_vietnamese",
    "cult_vietnam",
    "demo_citizenship_status",
    "demo_religion_affiliation",
    "religiosity",
)

KEEP = tuple(dict.fromkeys(SAMPLING + CONDITIONING + PRESENTATION + MEASURED_CONSTANT))

OBSERVED = {"observed", "direct", "forum_measured"}


def trim(persona: dict[str, Any]) -> tuple[int, int, list[str]]:
    """Drop unkept dimensions. Returns (before, after, measured_dropped)."""
    dims = persona.get("dimensions") or {}
    grounding = persona.get("grounding") or {}
    before = len(dims)
    dropped_measured = [
        key
        for key in dims
        if key not in KEEP
        and (grounding.get(key) or {}).get("assignment_type") in OBSERVED
    ]
    persona["dimensions"] = {k: v for k, v in dims.items() if k in KEEP}
    # Grounding for a dropped dimension would describe a value no longer there.
    # removed_incoherent entries stay: they record a repair, not a value.
    persona["grounding"] = {
        k: v
        for k, v in grounding.items()
        if k in KEEP or (isinstance(v, dict) and v.get("assignment_type") == "removed_incoherent")
    }
    return before, len(persona["dimensions"]), dropped_measured


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pool", type=Path)
    parser.add_argument("--out", type=Path, help="defaults to trimming in place")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    paths = persona_paths(args.pool)
    if not paths:
        print("no persona_*.yaml under {}".format(args.pool))
        return 1

    out_dir = args.out or args.pool
    totals: collections.Counter = collections.Counter()
    lost_measured: collections.Counter = collections.Counter()
    docs = []

    for path in paths:
        persona = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        before, after, dropped = trim(persona)
        totals["before"] += before
        totals["after"] += after
        for key in dropped:
            lost_measured[key] += 1
        docs.append((path, persona))

    n = len(paths)
    print("{} personas: {:.0f} -> {:.0f} dimensions each".format(
        n, totals["before"] / n, totals["after"] / n))
    kept_measured = sum(
        1
        for key, value in (docs[0][1].get("grounding") or {}).items()
        if isinstance(value, dict) and value.get("assignment_type") in OBSERVED
    )
    print("measured dimensions kept: {}".format(kept_measured))
    if lost_measured:
        print("\nWARNING: measured dimensions dropped, which discards evidence:")
        for key, count in lost_measured.most_common():
            print("   {:30s} {}/{} personas".format(key, count, n))

    if args.dry_run:
        print("\ndry run, nothing written")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    if out_dir != args.pool:
        for extra in args.pool.iterdir():
            if extra.is_file() and not extra.name.startswith("persona_"):
                shutil.copy2(extra, out_dir / extra.name)
    for path, persona in docs:
        (out_dir / path.name).write_text(
            yaml.safe_dump(persona, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
    print("\nwrote {} personas to {}".format(len(docs), out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
