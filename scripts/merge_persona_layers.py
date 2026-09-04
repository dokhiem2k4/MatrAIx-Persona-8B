#!/usr/bin/env python3
"""Combine extraction shards from different sources into one persona set.

The demographic layer (WVS) and the driving layer (questionnaire) describe
different people, so they cannot be joined on an identifier. They are joined by
*sampling*: each driver keeps their own answers and is paired with a WVS
respondent, giving a persona whose demographics and driving behaviour are each
grounded in a real person, with provenance recording which is which.

That pairing is a real limitation and the manifest says so. It is still a large
improvement on the alternative -- a persona whose driving traits were invented
by a prior -- but the demographic-driving correlations it produces are an
artefact of the pairing, not measurement, and must not be read as findings.

Pairing is stratified where the two sources share a dimension, so a retired
respondent is not handed a "new driver" profile at random.

Usage:
    uv run python scripts/merge_persona_layers.py \\
        --primary   persona/curation/.../vn_drivers/extraction_v1/shard_00.jsonl.gz \\
        --primary-ref vn_driver_survey_2026 \\
        --secondary persona/curation/.../wvs_vn/extraction_v1/shard_00.jsonl.gz \\
        --secondary-ref wvs_wave7_vnm_2020 \\
        --out persona/datasets/vn-drivers
"""

from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from persona.human_extraction.grounding import (  # noqa: E402
    GroundedPersona,
    Grounding,
    summarise,
)
from persona.human_extraction.vn_names import vietnamese_name  # noqa: E402
from persona.human_extraction.vn_localities import weighted_locality  # noqa: E402

#: Dimensions that would let the pairing be stratified rather than random.
#: Whether they help depends on the sources: a driver questionnaire and a
#: population survey may share nothing at all, in which case stratifying on an
#: absent key matches empty-against-empty and reports a perfect score while
#: doing nothing. ``describe_pairing`` checks for that instead of assuming.
STRATIFY_ON = ("life_stage", "urbanicity", "age_bracket", "gender_identity")


def read_shard(path: Path) -> Iterator[dict[str, Any]]:
    opener = gzip.open if path.name.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def observed(record: dict[str, Any]) -> dict[str, Any]:
    values = record.get("observed") or {}
    return {k: v for k, v in values.items() if v is not None and str(v).strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--primary-ref", required=True)
    parser.add_argument("--secondary", type=Path, required=True)
    parser.add_argument("--secondary-ref", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--name-prefix", default="VN")
    parser.add_argument(
        "--source-label",
        default="vn-driver",
        help="short pool label shown on the persona card chip",
    )
    parser.add_argument(
        "--vietnamese-localities",
        action="store_true",
        help=(
            "assign a province weighted by population, recorded as generated. "
            "The survey province cannot be reused: Vietnam merged 63 provinces "
            "into 34 units in July 2025 and several the respondents named no "
            "longer exist"
        ),
    )
    parser.add_argument(
        "--vietnamese-names",
        action="store_true",
        help=(
            "give each persona a Vietnamese display name, recorded as generated "
            "rather than observed -- no respondent supplied one"
        ),
    )
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="DIM=V1|V2",
        help="keep only primary records whose DIM is one of the listed values",
    )
    args = parser.parse_args()

    filters: dict[str, set[str]] = {}
    for spec in args.require:
        dim, _, values = spec.partition("=")
        filters[dim.strip()] = {v.strip() for v in values.split("|") if v.strip()}

    primary = [(r, observed(r)) for r in read_shard(args.primary)]
    dropped = 0
    if filters:
        kept = []
        for record, values in primary:
            if all(str(values.get(d) or "") in allowed for d, allowed in filters.items()):
                kept.append((record, values))
            else:
                dropped += 1
        primary = kept

    secondary = [(r, observed(r)) for r in read_shard(args.secondary)]

    # Stratify only on dimensions BOTH layers actually populate. Without this
    # check a missing key on one side makes every stratum ("", "") and the run
    # reports 100% same-stratum matches while pairing at random.
    primary_keys = set().union(*[set(v) for _, v in primary]) if primary else set()
    secondary_keys = set().union(*[set(v) for _, v in secondary]) if secondary else set()
    shared = {d for d in STRATIFY_ON if d in primary_keys and d in secondary_keys}

    def stratum(values: dict[str, Any]) -> tuple:
        return tuple(str(values.get(d) or "") for d in sorted(shared))

    by_stratum: dict[tuple, list] = defaultdict(list)
    for record, values in secondary:
        by_stratum[stratum(values)].append((record, values))

    rng = random.Random(args.seed)
    for bucket in by_stratum.values():
        rng.shuffle(bucket)
    pool = list(secondary)
    rng.shuffle(pool)

    args.out.mkdir(parents=True, exist_ok=True)
    personas: list[GroundedPersona] = []
    exact_stratum = 0

    for index, (record, values) in enumerate(primary):
        key = stratum(values)
        bucket = by_stratum.get(key) or []
        if bucket:
            match_record, match_values = bucket.pop()
            exact_stratum += 1
        else:
            # No same-stratum partner left; fall back rather than drop the
            # driver, whose answers are the scarce half.
            match_record, match_values = pool[index % len(pool)]

        uid = str(record.get("user_id") or "row-{:03d}".format(index))
        bits = [
            b
            for b in (match_values.get("gender_identity"), match_values.get("age_bracket"))
            if b
        ]
        if args.vietnamese_names:
            display = vietnamese_name(uid, match_values.get("gender_identity"))
        else:
            display = "{} {}{}".format(
                args.name_prefix,
                uid.rsplit("-", 1)[-1],
                " ({})".format(", ".join(map(str, bits))) if bits else "",
            )
        persona = GroundedPersona(
            persona_id=uid,
            display_name=display,
            # Short, like the pools already shipped ("wiki", "gss", "amazon").
            # The full provenance lives per dimension in `grounding` and in
            # `grounding_summary.sources`; a long value here only crowds the
            # card, where the source chip sits beside the persona name.
            source=args.source_label,
        )
        # Demographics first so a driving answer wins any overlap: the driver
        # answered about themselves, the paired respondent did not.
        for dimension, value in sorted(match_values.items()):
            persona.set(
                dimension,
                value,
                assignment_type="observed",
                source_ref=args.secondary_ref,
                evidence="{}:{}".format(
                    args.secondary_ref, match_record.get("user_id")
                ),
                confidence=1.0,
            )
        for dimension, value in sorted(values.items()):
            persona.set(
                dimension,
                value,
                assignment_type="observed",
                source_ref=args.primary_ref,
                evidence="{}:{}".format(args.primary_ref, uid),
                confidence=1.0,
            )
        if args.vietnamese_localities:
            persona.set(
                "vn_locality",
                weighted_locality(uid),
                assignment_type="generated",
                source_ref="vn_localities",
                evidence="population-weighted draw over the 34 units effective 2025-07-01",
            )
        if args.vietnamese_names:
            # A name nobody supplied. Recorded so a reader can tell it apart
            # from the surveyed values sitting beside it.
            persona.grounding["display_name"] = Grounding(
                assignment_type="generated",
                source_ref="vn_names",
                evidence="derived from gender_identity + persona_id",
            )
        personas.append(persona)
        (args.out / "persona_{}.yaml".format(uid)).write_text(
            yaml.safe_dump(persona.to_yaml_dict(), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    manifest = {
        # ``count`` is the key PersonaPoolService reads; a manifest without it
        # reports a pool of 0 and never falls through to counting the files.
        "count": len(personas),
        "kind": "dataset",
        "datasetId": args.out.name,
        "personaCount": len(personas),
        # ``personas`` is what load_manifest reads; without it the loader
        # returns an empty list and never falls through to globbing, so the
        # pool counts but cannot be opened. Filenames rather than dicts: given
        # a dict, load_manifest takes it verbatim and never opens the YAML, so
        # display_name and dimensions go missing and the card falls back to a
        # synthesised name.
        "personas": [
            "persona_{}.yaml".format(p.persona_id) for p in personas
        ],
        "primary": {"shard": str(args.primary), "ref": args.primary_ref},
        "secondary": {"shard": str(args.secondary), "ref": args.secondary_ref},
        "droppedByFilter": dropped,
        "pairing": {
            "method": (
                "stratified sampling on {}".format(", ".join(sorted(shared)))
                if shared
                else "random sampling -- the two layers share no dimension to "
                "stratify on, so nothing constrains which respondent is paired "
                "with which driver"
            ),
            "sharedDimensions": sorted(shared),
            "sameStratumMatches": exact_stratum,
            "fallbackMatches": len(personas) - exact_stratum,
            "seed": args.seed,
            "caveat": (
                "The two layers describe different people. Demographic-driving "
                "correlations in this set are an artefact of pairing, not "
                "measurement; only within-layer relationships are observed."
            ),
        },
        "grounding": summarise(personas),
    }
    (args.out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("wrote {} personas -> {}".format(len(personas), args.out))
    if dropped:
        print("  dropped {} by --require".format(dropped))
    if shared:
        print("  stratified on   : {}".format(", ".join(sorted(shared))))
        print("  same-stratum    : {}/{}".format(exact_stratum, len(personas)))
    else:
        print("  pairing         : RANDOM -- layers share no common dimension")
    for key, value in manifest["grounding"].items():
        print("  {:18s} {}".format(key, value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
