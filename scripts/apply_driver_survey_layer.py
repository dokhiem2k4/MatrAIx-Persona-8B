#!/usr/bin/env python3
"""Fill the 2026 assistant dimensions on an existing pool from survey shape.

What this can and cannot claim, stated once so the output is not read as more
than it is:

  The survey export carries no respondent id -- only a timestamp -- so no
  answer can be attached to a particular persona. Nothing here is labelled
  ``observed``; that type means "this person answered this" and would be a lie.

  What does transfer is the population shape, and better than a marginal would:
  every respondent answered the eight original driving questions as well as the
  new ones, so the *conditional* distribution is measurable. A persona's value
  is drawn from the distribution for people who answered the conditioning
  question the way that persona already, measurably, answers it.

  Provenance stays ``generated``. The prior behind it is now measured rather
  than assumed, and ``source_ref`` records which survey and which conditioner.

Allocation uses largest-remainder rather than sampling: on a 42-persona pool a
draw would land a few points off the measured distribution and differ run to
run. This is exact and deterministic.

Usage:
    uv run python scripts/apply_driver_survey_layer.py \
        --responses "~/Downloads/<google forms export>.csv" \
        --pool persona/datasets/vn-drivers \
        --out persona/datasets/vn-drivers
"""

from __future__ import annotations

import argparse
import collections
import csv
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "persona/curation/existing_data/scripts"))

from crosswalks.vn_drivers import CROSSWALK, SCREEN_IN  # noqa: E402

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from validate_persona_rules import repair, violations  # noqa: E402
from persona_tiers import (  # noqa: E402
    OBSERVED_TYPES,
    apply_tiers,
    recompute_grounding_summary,
)

SOURCE_REF = "vn_driver_survey_2026"

#: Each new dimension is conditioned on the measured dimension that predicts it
#: best (Cramér's V over the responses; all of these scored >= 0.44). Choosing
#: the conditioner from the data beats guessing which trait ought to matter.
#: Each generated field draws from the distribution for respondents who match
#: this persona on ALL of these, not just one. Single-parent conditioning is
#: what produced a bicycle commuter who owns no car, drives 150-300km a week,
#: and has a built-in assistant: each value was defensible against its own
#: parent and impossible against the others.
#:
#: Two relations from the first pass are gone rather than widened. trip_mix was
#: conditioned on att_self_driving_cars and cabin_noise on
#: att_electric_vehicles; both scored above the threshold on 81 responses and
#: neither is a cause of anything. A stance on electric cars does not decide how
#: loud a cabin is.
#: ORDER IS LOAD-BEARING. weights_with_backoff keeps ``parents[:depth]``, so
#: parents are dropped from the right. A parent that a hard rule depends on must
#: therefore come FIRST, or thin data will drop exactly the conditioning that
#: keeps the rule satisfiable and leave the validator to repair after the fact.
#: With 24 of 42 personas backing off to a single parent on
#: vn_assistant_task_scope, that is more than half the pool being fixed in post
#: rather than generated right.
CONDITIONED_ON = {
    "vn_locality": ("urbanicity",),
    "veh_class": ("lstyle_commute_mode", "socioeconomic_band"),
    "drv_exposure": ("veh_class", "demo_driver_status", "lstyle_commute_mode"),
    "veh_assistant_builtin": ("veh_class", "tech_savviness"),
    "assistant_usage_freq": ("veh_assistant_builtin", "demo_driver_status"),
    "vn_assistant_task_scope": ("att_self_driving_cars", "cog_patience", "cog_skepticism"),
    "trip_mix": ("urbanicity", "vn_locality"),
    "cabin_noise": ("veh_class", "vn_usual_companion"),
    "cabin_context": ("demo_driver_status", "skill_driving"),
    "vn_usual_companion": ("demo_driver_status", "demo_children_count"),
    "vn_voice_privacy_comfort": ("skill_driving", "vn_usual_companion"),
    "vn_retry_tolerance": ("cog_skepticism", "cog_patience"),
    "need_state": ("topic_cars", "demo_driver_status"),
}

#: Order matters: fields early in this list are assigned before fields that
#: condition on them. vn_usual_companion must exist before cabin_noise can use
#: it, and veh_class before veh_assistant_builtin.
ASSIGNMENT_ORDER = (
    "vn_locality",
    "vn_usual_companion",
    "veh_class",
    "drv_exposure",
    "veh_assistant_builtin",
    "assistant_usage_freq",
    "trip_mix",
    "cabin_noise",
    "cabin_context",
    "vn_voice_privacy_comfort",
    "vn_retry_tolerance",
    "vn_assistant_task_scope",
    "need_state",
)

#: accent_region is deliberately NOT drawn from a distribution. The strongest
#: conditioner the responses offer is att_electric_vehicles at V=0.33, which is
#: a coincidence of a small sample -- a stance on electric cars does not decide
#: where someone learned to speak. Where they live does, and every persona
#: already carries a measured vn_locality, so this one is derived from it.
ACCENT_BY_REGION = {
    "Northern": {
        "Ha Noi", "Bac Ninh", "Hung Yen", "Phu Tho", "Tuyen Quang", "Ninh Binh",
        "Son La", "Dien Bien", "Lai Chau", "Thanh Hoa",
    },
    "Central": {"Da Nang", "Khanh Hoa", "Gia Lai", "Dak Lak", "Lam Dong"},
    "Southern": {
        "Ho Chi Minh City", "Dong Nai", "Tay Ninh", "An Giang", "Dong Thap",
        "Vinh Long", "Ca Mau",
    },
}

#: Follows from task scope by the same rule the crosswalk uses, so a persona
#: never ends up enthusiastic about an assistant it delegates nothing to.
#: att_voice_assistant used to derive from vn_assistant_task_scope, which is
#: itself generated -- a guess resting on a guess, and on vn-drv-001 the error
#: was amplified into "Enthusiast" for someone who opposes self-driving cars.
#: A derived field must rest on a measured one, so this now follows the
#: respondent's own stance on autonomous driving.
SELF_DRIVING_TO_ATTITUDE = {
    "Enthusiast": "Enthusiast",
    "Positive": "Positive",
    "Neutral": "Neutral",
    "Skeptical": "Skeptical",
    "Opposed": "Opposed",
}


def largest_remainder(total: int, weights: dict[str, float]) -> dict[str, int]:
    """Split ``total`` across keys so the result matches ``weights`` exactly."""
    scale = sum(weights.values())
    if scale <= 0:
        return {key: 0 for key in weights}
    raw = {key: total * value / scale for key, value in weights.items()}
    out = {key: int(value) for key, value in raw.items()}
    remainder = total - sum(out.values())
    for key in sorted(raw, key=lambda k: (-(raw[k] - out[k]), k))[:remainder]:
        out[key] += 1
    return out


def read_responses(path: Path) -> list[dict[str, Any]]:
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    eligible = [
        row for row in rows
        if any(term in (list(row.values())[2] or "") for term in SCREEN_IN)
    ]
    return [
        {dim: spec["compute"](row) for dim, spec in CROSSWALK.items()}
        for row in eligible
    ]


def conditional_weights(
    records: list[dict[str, Any]], target: str, parents: tuple[str, ...]
) -> dict[tuple, dict[str, int]]:
    """Counts of ``target`` for every combination of ``parents`` seen."""
    table: dict[tuple, collections.Counter] = collections.defaultdict(collections.Counter)
    for record in records:
        value = record.get(target)
        if value is None:
            continue
        key = tuple(record.get(p) for p in parents)
        if any(k is None for k in key):
            continue
        table[key][value] += 1
    return {k: dict(v) for k, v in table.items()}


def weights_with_backoff(
    records: list[dict[str, Any]],
    target: str,
    parents: tuple[str, ...],
    persona_dims: dict[str, Any],
    *,
    min_support: int = 3,
) -> tuple[dict[str, int], int]:
    """Distribution for this persona, dropping parents until one has support.

    Conditioning on three parents is the point of this change, but 81
    respondents cannot populate every combination of three. Rather than fall
    straight to the marginal -- which throws away the conditioning entirely --
    the least important parent is dropped and the lookup retried, so a persona
    keeps as much conditioning as the data can actually support. The number of
    parents that survived is returned so the run can report how much
    conditioning it really achieved rather than how much it asked for.
    """
    for depth in range(len(parents), 0, -1):
        subset = parents[:depth]
        key = tuple(persona_dims.get(p) for p in subset)
        if any(k is None for k in key):
            continue
        table = conditional_weights(records, target, subset)
        counts = table.get(key)
        if counts and sum(counts.values()) >= min_support:
            return counts, depth
    marginal: collections.Counter = collections.Counter()
    for record in records:
        value = record.get(target)
        if value is not None:
            marginal[value] += 1
    return dict(marginal), 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path, required=True)
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    # Changing the DAG and adding the rules in one run makes any drift in the
    # marginals un-attributable. This runs the generation half alone, so the
    # rules' own effect can be measured against it.
    parser.add_argument("--skip-rules", action="store_true",
                        help="generate without the validator pass")
    args = parser.parse_args()

    records = read_responses(args.responses.expanduser())
    if not records:
        print("no eligible responses in {}".format(args.responses))
        return 1

    paths = persona_paths(args.pool)
    personas = [(p, yaml.safe_load(p.read_text(encoding="utf-8")) or {}) for p in paths]
    print("{} eligible responses shape {} personas\n".format(len(records), len(personas)))

    depth_report: dict[str, collections.Counter] = {}
    for target in ASSIGNMENT_ORDER:
        parents = CONDITIONED_ON[target]
        depths: collections.Counter = collections.Counter()
        assigned: dict[int, str] = {}

        # Personas sharing a parent combination are allocated together, so the
        # pool matches the measured conditional distribution exactly rather
        # than approximately.
        groups: dict[tuple, list[int]] = collections.defaultdict(list)
        for index, (_, persona) in enumerate(personas):
            dims = persona.get("dimensions") or {}
            counts, depth = weights_with_backoff(records, target, parents, dims)
            depths[depth] += 1
            groups[(tuple(dims.get(p) for p in parents[:depth]), depth)].append(index)

        for (key, depth), members in groups.items():
            dims = (personas[members[0]][1].get("dimensions") or {})
            counts, _ = weights_with_backoff(records, target, parents, dims)
            allocation = largest_remainder(len(members), counts)
            slots = [v for value, count in sorted(allocation.items()) for v in [value] * count]
            for member, value in zip(sorted(members, key=lambda i: paths[i].stem), slots):
                assigned[member] = value

        for index, (_, persona) in enumerate(personas):
            value = assigned.get(index)
            if value is None:
                continue
            persona.setdefault("dimensions", {})[target] = value
            persona.setdefault("grounding", {})[target] = {
                "assignment_type": "generated",
                "source_ref": SOURCE_REF,
                "evidence": "{}:conditional_on:{}".format(SOURCE_REF, "+".join(parents)),
                "confidence": 0.5,
            }
        depth_report[target] = depths

    print("conditioning depth actually achieved (parents used / asked for):")
    for target, depths in depth_report.items():
        asked = len(CONDITIONED_ON[target])
        detail = " ".join(
            "{}p:{}".format(d if d else "marginal", n) for d, n in sorted(depths.items(), reverse=True)
        )
        print("  {:26s} asked {}  ->  {}".format(target, asked, detail))
    print()

    # accent_region follows from where the persona lives, not from a draw.
    unplaced = []
    for _, persona in personas:
        locality = (persona.get("dimensions") or {}).get("vn_locality")
        accent = next(
            (name for name, places in ACCENT_BY_REGION.items() if locality in places),
            None,
        )
        if accent is None:
            unplaced.append(locality)
            continue
        persona["dimensions"]["accent_region"] = accent
        persona.setdefault("grounding", {})["accent_region"] = {
            # Not "derived": that type is reserved for a chain resting on a
            # measured value, and vn_locality is itself sampled. The mapping is
            # deterministic, but a deterministic function of a guess is a guess.
            "assignment_type": "generated",
            "source_ref": SOURCE_REF,
            "evidence": "function_of:vn_locality",
            "confidence": 0.6,
        }
    if unplaced:
        print("accent_region: {} persona(s) with an unmapped locality: {}".format(
            len(unplaced), sorted({str(x) for x in unplaced})))
    else:
        print("accent_region: derived from vn_locality for every persona\n")

    # att_voice_assistant now follows a measured field. A derived value resting
    # on a generated one is a guess wearing a second coat of paint, and the
    # build refuses it below.
    for _, persona in personas:
        dims = persona.get("dimensions") or {}
        stance = dims.get("att_self_driving_cars")
        if stance in SELF_DRIVING_TO_ATTITUDE:
            dims["att_voice_assistant"] = SELF_DRIVING_TO_ATTITUDE[stance]
            persona.setdefault("grounding", {})["att_voice_assistant"] = {
                "assignment_type": "derived",
                "source_ref": SOURCE_REF,
                "evidence": "derived_from:att_self_driving_cars",
                "confidence": 0.7,
            }

    # Conditioning narrows the draw; it cannot guarantee a hard constraint,
    # because the respondents themselves contain combinations a rule forbids.
    # So the rules run after generation and before writing, and a violation is
    # resampled rather than accepted. Bounded: a pool that will not converge is
    # a fact about the rules, and looping forever would hide it.
    import random

    rng = random.Random(42)
    pool_values: dict[str, list[str]] = collections.defaultdict(list)
    for _, persona in personas:
        for key, value in (persona.get("dimensions") or {}).items():
            if value is not None:
                pool_values[key].append(str(value))

    MAX_PASSES = 8
    if args.skip_rules:
        print("validator: skipped (--skip-rules)")
    else:
      for attempt in range(1, MAX_PASSES + 1):
          offending = [(pa, pe) for pa, pe in personas if violations(pe)]
          if not offending:
              print("validator: clean after {} pass(es)".format(attempt - 1))
              break
          for _, persona in offending:
              repair(persona, pool_values, rng=rng)
      else:
          if args.skip_rules:
              print("validator: skipped")
              remaining = {}
          else:
              remaining = {
              str(pe.get("persona_id")): [c for c, _ in violations(pe)]
              for _, pe in personas
              if violations(pe)
          }
          raise SystemExit(
              "validator did not converge in {} passes; still failing: {}".format(
                  MAX_PASSES, remaining)
          )

    # Acceptance criterion: a derived field must rest on a measured one. This is
    # a build failure, not a warning -- the whole point of provenance is that a
    # reader can trust what "derived" means without checking the chain by hand.
    for path, persona in personas:
        grounding = persona.get("grounding") or {}
        for field, entry in grounding.items():
            if not isinstance(entry, dict) or entry.get("assignment_type") != "derived":
                continue
            evidence = str(entry.get("evidence") or "")
            if not evidence.startswith("derived_from:"):
                continue
            source = evidence.split("derived_from:", 1)[1].split(":")[0]
            source_type = (grounding.get(source) or {}).get("assignment_type")
            if source_type not in OBSERVED_TYPES:
                raise SystemExit(
                    "{}: {} is derived from {}, which is {!r}, not measured".format(
                        path.name, field, source, source_type)
                )

    for _, persona in personas:
        apply_tiers(persona)
        recompute_grounding_summary(persona)

    args.out.mkdir(parents=True, exist_ok=True)
    # Copying a pool onto itself raises SameFileError, and it raised it before
    # a single persona was written -- an in-place run silently did nothing.
    if args.out.resolve() != args.pool.resolve():
        for extra in args.pool.iterdir():
            if extra.is_file() and not extra.name.startswith("persona_"):
                shutil.copy2(extra, args.out / extra.name)
    for path, persona in personas:
        (args.out / path.name).write_text(
            yaml.safe_dump(persona, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
    print("wrote {} personas to {}".format(len(personas), args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
