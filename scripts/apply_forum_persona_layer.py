#!/usr/bin/env python3
"""Fill the two dead dimensions in the VN-Drives pool from forum measurements.

What this can and cannot claim, stated once so the output is not read as more
than it is:

  The 42 personas are survey respondents. The forum members are different
  people. Nothing measured from a member's writing can be attributed to a
  persona, so nothing here is labelled ``forum_measured`` -- that type means
  "measured from the person's own writing" and would be a lie.

  What does transfer is the population shape. Two dimensions are currently
  unusable: vn_address_register is null on all 42, and cog_verbosity comes from
  the synthesis graph. Both are replaced with values drawn so the pool's
  distribution matches what Vietnamese drivers actually do, with the individual
  value following deterministically from that persona's own measured age and
  gender. Provenance stays ``generated``; the prior behind it is now measured
  rather than assumed.

Usage:
    python apply_forum_layer.py --measurements otofun_measurements.json \
        --pool <base pool> --out persona/datasets/vn-drivers

    The base pool this consumed was consolidated into vn-drivers and is no
    longer a directory of its own; recover it with
    ``git show b2ce5d8:persona/datasets/vn-drivers`` if the layer must be rerun.
"""

from __future__ import annotations

import argparse
import collections
import json
import shutil
from pathlib import Path

import yaml

SOURCE_REF = "otofun_2026"

# Vietnamese picks the pronoun pair from the speaker's standing relative to the
# listener. The assistant presents as a young woman, so a speaker who uses
# kinship terms addresses it from their own age and gender.
KINSHIP_BY_AGE = {
    "18-24": {"Man": "anh/em", "Woman": "chi/em"},
    "25-34": {"Man": "anh/em", "Woman": "chi/em"},
    "35-44": {"Man": "anh/em", "Woman": "chi/em"},
    "45-54": {"Man": "co-chu/con", "Woman": "co-chu/con"},
    "55-64": {"Man": "co-chu/con", "Woman": "co-chu/con"},
    "65-74": {"Man": "bac/chau", "Woman": "bac/chau"},
    "75-84": {"Man": "bac/chau", "Woman": "bac/chau"},
    "85+": {"Man": "bac/chau", "Woman": "bac/chau"},
}
KINSHIP_FALLBACK = "toi/ban"


def largest_remainder(total: int, weights: dict[str, float]) -> dict[str, int]:
    """Split ``total`` across keys so the result matches ``weights`` exactly.

    Sampling would leave the pool's distribution a few points off the measured
    one on a pool this small, and would differ run to run. This is exact and
    deterministic.
    """
    scale = sum(weights.values())
    if scale <= 0:
        return {k: 0 for k in weights}
    raw = {k: total * v / scale for k, v in weights.items()}
    out = {k: int(v) for k, v in raw.items()}
    remainder = total - sum(out.values())
    for key in sorted(raw, key=lambda k: (-(raw[k] - out[k]), k))[:remainder]:
        out[key] += 1
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurements", type=Path, required=True)
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    stats = json.loads(args.measurements.read_text(encoding="utf-8"))
    positioning = stats["self_positioning"]
    verbosity_dist = stats["cog_verbosity"]

    paths = sorted(args.pool.glob("persona_*.yaml"))
    personas = [(p, yaml.safe_load(p.read_text(encoding="utf-8"))) for p in paths]
    n = len(personas)

    # --- vn_address_register ------------------------------------------------
    # A member who reaches for kinship terms among peers reaches for them with
    # the assistant too; which pair follows from their own age and gender.
    # The forum measures how a driver stands toward other people, not toward an
    # assistant, so only the kinship-versus-neutral split carries over. Which
    # kinship pair a persona gets is decided by that persona's own measured age
    # and gender, not by anything a forum member wrote.
    register_weights = {
        "kinship": positioning.get("deferential", 0),
        "minh/ban": positioning.get("neutral", 0),
    }
    register_counts = largest_remainder(n, register_weights)

    # --- cog_verbosity ------------------------------------------------------
    verbosity_counts = largest_remainder(n, {k: float(v) for k, v in verbosity_dist.items()})

    # Deterministic order: persona id. No RNG anywhere in this script.
    order = sorted(range(n), key=lambda i: personas[i][1]["persona_id"])

    register_plan: list[str] = []
    for bucket, count in sorted(register_counts.items()):
        register_plan += [bucket] * count
    verbosity_plan: list[str] = []
    for band, count in sorted(verbosity_counts.items()):
        verbosity_plan += [band] * count

    args.out.mkdir(parents=True, exist_ok=True)
    manifest = args.pool / "manifest.json"
    if manifest.is_file():
        shutil.copy2(manifest, args.out / "manifest.json")

    applied = collections.Counter()
    for slot, index in enumerate(order):
        path, persona = personas[index]
        dims = persona.setdefault("dimensions", {})
        grounding = persona.setdefault("grounding", {})

        bucket = register_plan[slot]
        if bucket == "kinship":
            age = str(dims.get("age_bracket") or "")
            gender = str(dims.get("gender_identity") or "")
            register = KINSHIP_BY_AGE.get(age, {}).get(gender, KINSHIP_FALLBACK)
            evidence = "kinship register for age_bracket={} gender_identity={}".format(
                age or "unknown", gender or "unknown"
            )
        else:
            register = bucket
            evidence = "neutral register; pool share calibrated to forum self-positioning"

        dims["vn_address_register"] = register
        grounding["vn_address_register"] = {
            "assignment_type": "generated",
            "source_ref": SOURCE_REF,
            "evidence": evidence,
            "confidence": 0.5,
        }
        applied[register] += 1

        band = verbosity_plan[slot]
        dims["cog_verbosity"] = band
        grounding["cog_verbosity"] = {
            "assignment_type": "generated",
            "source_ref": SOURCE_REF,
            "evidence": "pool share calibrated to median words per post on {}".format(
                stats["source"]
            ),
            "confidence": 0.5,
        }

        (args.out / path.name).write_text(
            yaml.safe_dump(persona, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )

    print("wrote {} personas to {}".format(n, args.out))
    print("\nvn_address_register:")
    for value, count in applied.most_common():
        print("   {:14s} {:>3}".format(value, count))
    print("\ncog_verbosity:")
    for band, count in sorted(verbosity_counts.items()):
        print("   {:10s} {:>3}".format(band, count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
