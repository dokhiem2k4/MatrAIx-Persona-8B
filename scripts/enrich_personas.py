#!/usr/bin/env python3
"""Fill a grounded persona's remaining dimensions from the synthesis DAG.

A persona built from a survey carries ~25 measured dimensions. The personas
shipped with the repo carry ~294, and the UI is built for that shape: a card
reads ``domain`` and ``life_stage``, and the profile drawer groups attributes
into Background / Psychology / Capability / Behavior / Lifestyle. With 25
dimensions most of that reads as empty.

This samples the missing dimensions from ``full_dag.json`` with the measured
ones pinned, so what is generated stays consistent with what was observed --
a retired respondent does not get an "early career" attribute.

The distinction is preserved rather than blurred. Sampled values are written as
``assignment_type: generated`` and never enter the scoreable set, so a later
reader can still separate the 25 answers a person actually gave from the
hundreds the graph invented around them. That matters more here than usual:
only 107 of the DAG's 6,999 edges are calibrated on real microdata, and none
of them touch the driving or cog_* dimensions, so the generated layer is
mostly prior rather than measurement.

Usage:
    uv run python scripts/enrich_personas.py persona/datasets/vn-drivers
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from persona_tiers import persona_paths  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from persona.human_extraction.grounding import (  # noqa: E402
    GENERATED,
    GroundedPersona,
    Grounding,
    summarise,
)

DEFAULT_GRAPH = REPO_ROOT / "persona/synthesis/graph/full_dag.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="directory of persona_*.yaml")
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--dry-run", action="store_true", help="report coverage without writing"
    )
    args = parser.parse_args()

    from persona.synthesis.sampler.sampler import PersonaForwardSampler, SamplingConfig

    print("loading graph {} ...".format(args.graph), flush=True)
    sampler = PersonaForwardSampler(
        args.graph, SamplingConfig(seed=args.seed)
    )
    print("  {} nodes".format(len(sampler.nodes)), flush=True)

    files = persona_paths(args.dataset)
    if not files:
        raise SystemExit("no persona_*.yaml under {}".format(args.dataset))

    personas: list[GroundedPersona] = []
    relaxed: dict[str, list[str]] = {}
    added_total = 0

    for path in files:
        persona = GroundedPersona.from_yaml_dict(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
        observed = {
            d: str(v)
            for d, v in persona.dimensions.items()
            # Pin only what the graph knows and accepts as a value; an unknown
            # node or a value outside its enum would abort the whole sample.
            if d in sampler.values and str(v) in sampler.values[d]
        }
        # The graph rejects some real combinations. One Vietnamese respondent
        # reported no denomination while rating religion as important -- common
        # where practice is ancestral rather than congregational -- and the DAG
        # gives that zero probability. The measured answer stays; only the
        # conditioning is relaxed, by dropping the fewest pins that restore a
        # supported assignment. Leaving these personas unenriched instead would
        # split the set into 1,291-dimension and 25-dimension halves and
        # reintroduce exactly the coverage confound the standard exists to stop.
        dropped_pins: list[str] = []
        while observed and not sampler.assignment_supported(observed):
            culprit = next(
                (
                    dim
                    for dim in sorted(observed)
                    if sampler.assignment_supported(
                        {k: v for k, v in observed.items() if k != dim}
                    )
                ),
                None,
            )
            if culprit is None:
                # No single pin explains it; give up on conditioning entirely
                # rather than peeling the set down one arbitrary dimension at a
                # time.
                dropped_pins.extend(sorted(observed))
                observed = {}
                break
            dropped_pins.append(culprit)
            observed.pop(culprit)
        if dropped_pins:
            relaxed[persona.persona_id] = dropped_pins

        sample = sampler.sample(1, fixed=observed)[0]
        added = 0
        for dimension, value in sample.items():
            if dimension in persona.dimensions:
                continue
            if value is None or not str(value).strip():
                continue
            persona.dimensions[dimension] = value
            persona.grounding[dimension] = Grounding(
                assignment_type=GENERATED,
                source_ref="full_dag",
                evidence="sampled conditioned on {} observed dimensions".format(
                    len(observed)
                ),
            )
            added += 1
        added_total += added
        personas.append(persona)

        if not args.dry_run:
            path.write_text(
                yaml.safe_dump(
                    persona.to_yaml_dict(), sort_keys=False, allow_unicode=True
                ),
                encoding="utf-8",
            )

    sizes = [len(p.dimensions) for p in personas]
    print("\n{} persona(s) in {}".format(len(personas), args.dataset))
    print("  dimensions : mean {:.0f}  min {}  max {}".format(
        sum(sizes) / len(sizes), min(sizes), max(sizes)
    ))
    print("  generated  : {} value(s) added".format(added_total))
    for key, value in summarise(personas).items():
        print("  {:12s} {}".format(key, value))
    if relaxed:
        print(
            "\n  {} persona(s) needed a relaxed pin set -- the graph gives their "
            "measured combination zero probability. The measured values are "
            "unchanged; they just did not constrain the sampling:".format(len(relaxed))
        )
        for pid, dims in list(relaxed.items())[:6]:
            print("      {:14s} unpinned {}".format(pid, ", ".join(dims)))

    manifest_path = args.dataset / "manifest.json"
    if manifest_path.is_file() and not args.dry_run:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["enrichment"] = {
            "graph": str(args.graph),
            "seed": args.seed,
            "generatedValues": added_total,
            "relaxedPins": relaxed,
            "caveat": (
                "Generated dimensions are sampled from the synthesis DAG "
                "conditioned on the measured ones. Only 107 of its 6,999 edges "
                "are calibrated on real microdata and none touch driving or "
                "cog_* dimensions, so treat the generated layer as plausible "
                "context, not evidence."
            ),
        }
        manifest["grounding"] = summarise(personas)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
