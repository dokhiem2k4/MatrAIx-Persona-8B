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

from crosswalks.vn_drivers import CROSSWALK  # noqa: E402

SOURCE_REF = "vn_driver_survey_2026"

#: Only respondents who actually drive may shape a driver pool.
SCREEN_IN = ("Lái hằng ngày", "Thỉnh thoảng lái")

#: Each new dimension is conditioned on the measured dimension that predicts it
#: best (Cramér's V over the responses; all of these scored >= 0.44). Choosing
#: the conditioner from the data beats guessing which trait ought to matter.
CONDITIONED_ON = {
    "vn_usual_companion": "demo_driver_status",
    "vn_voice_privacy_comfort": "skill_driving",
    "vn_assistant_task_scope": "cog_patience",
    "vn_retry_tolerance": "cog_skepticism",
    # Second round. Same rule: the conditioner is whichever measured dimension
    # predicts this one best over the responses, not whichever seems apt.
    "veh_class": "lstyle_commute_mode",
    "veh_assistant_builtin": "cog_patience",
    "drv_exposure": "demo_driver_status",
    "trip_mix": "att_self_driving_cars",
    "assistant_usage_freq": "demo_driver_status",
    "need_state": "topic_cars",
    "cabin_context": "topic_cars",
    "cabin_noise": "att_electric_vehicles",
}

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
SCOPE_TO_ATTITUDE = {
    "None": "Opposed",
    "Navigation only": "Skeptical",
    "Navigation and media": "Neutral",
    "Most non-driving tasks": "Positive",
    "Everything including vehicle control": "Enthusiast",
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
    records: list[dict[str, Any]], target: str, conditioner: str
) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    """P(target | conditioner) plus the marginal, both as raw counts."""
    per_group: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    marginal: collections.Counter = collections.Counter()
    for record in records:
        value, group = record.get(target), record.get(conditioner)
        if value is None:
            continue
        marginal[value] += 1
        if group is not None:
            per_group[group][value] += 1
    return ({g: dict(c) for g, c in per_group.items()}, dict(marginal))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path, required=True)
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    records = read_responses(args.responses.expanduser())
    if not records:
        print("no eligible responses in {}".format(args.responses))
        return 1

    paths = sorted(args.pool.glob("persona_*.yaml"))
    personas = [(p, yaml.safe_load(p.read_text(encoding="utf-8")) or {}) for p in paths]
    print("{} eligible responses shape {} personas\n".format(len(records), len(personas)))

    for target, conditioner in CONDITIONED_ON.items():
        groups, marginal = conditional_weights(records, target, conditioner)

        # Bucket personas by their own measured value of the conditioner.
        buckets: dict[Any, list[int]] = collections.defaultdict(list)
        for index, (_, persona) in enumerate(personas):
            buckets[(persona.get("dimensions") or {}).get(conditioner)].append(index)

        assigned: dict[int, str] = {}
        fell_back = 0
        for group, members in buckets.items():
            # A persona whose conditioner value no respondent shares has no
            # conditional distribution to draw from; the marginal is the honest
            # fallback, and the count of those is reported rather than hidden.
            weights = groups.get(group) or marginal
            if group not in groups:
                fell_back += len(members)
            allocation = largest_remainder(len(members), weights)
            slots = [v for value, count in sorted(allocation.items()) for v in [value] * count]
            # Sorted by persona id, so the same pool always yields the same map.
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
                "evidence": "{}:conditional_on:{}".format(SOURCE_REF, conditioner),
                "confidence": 0.5,
            }

        spread = collections.Counter(assigned.values())
        print("{}  (conditioned on {})".format(target, conditioner))
        for value, count in spread.most_common():
            print("   {:3d}  {}".format(count, value))
        if fell_back:
            print("   {} persona(s) used the marginal: conditioner value unseen in responses".format(fell_back))
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
            "assignment_type": "derived",
            "source_ref": SOURCE_REF,
            "evidence": "derived_from:vn_locality",
            "confidence": 0.9,
        }
    if unplaced:
        print("accent_region: {} persona(s) with an unmapped locality: {}".format(
            len(unplaced), sorted({str(x) for x in unplaced})))
    else:
        print("accent_region: derived from vn_locality for every persona\n")

    # att_voice_assistant follows from the scope just assigned.
    for _, persona in personas:
        scope = (persona.get("dimensions") or {}).get("vn_assistant_task_scope")
        if scope in SCOPE_TO_ATTITUDE:
            persona["dimensions"]["att_voice_assistant"] = SCOPE_TO_ATTITUDE[scope]
            persona.setdefault("grounding", {})["att_voice_assistant"] = {
                "assignment_type": "derived",
                "source_ref": SOURCE_REF,
                "evidence": "derived_from:vn_assistant_task_scope",
                "confidence": 0.5,
            }

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
