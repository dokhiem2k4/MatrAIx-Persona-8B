#!/usr/bin/env python3
"""Export a grounded persona pool as one machine-readable JSON dataset.

The pool ships as 42 separate YAML files plus a manifest, which is right for
the repo and wrong for handing to someone who wants to load it in pandas or
feed it to a model. This flattens it into a single document that is
self-describing: every dimension carries its value AND its provenance, and the
catalog at the top says what each dimension id means and what values it admits.

The provenance is the point. A persona holds 1,291 values but only ~24 are
answers a person gave; the rest are sampled from the synthesis graph. Anyone
reading this file downstream must be able to tell those apart without knowing
the pipeline, so `assignmentType` travels with every single value and the
caveats that cannot be expressed per-value -- random pairing, generated
locality -- sit in `provenance.caveats` where they cannot be missed.

Usage:
    uv run python scripts/export_persona_dataset_json.py persona/datasets/vn-drivers
    uv run python scripts/export_persona_dataset_json.py persona/datasets/vn-drivers --no-catalog
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from export_vn_driver_profiles import (  # noqa: E402
    SCOREABLE,
    load_labels,
    load_personas,
    overlap_report,
)

SCHEMA = REPO_ROOT / "persona/schema/dimensions.json"


def build_catalog(used: list[str]) -> dict:
    """Describe every dimension present, so the file explains itself."""
    dims = {d["id"]: d for d in json.loads(SCHEMA.read_text(encoding="utf-8"))["dimensions"]}
    dim_label_vi, val_label_vi = load_labels()
    catalog = {}
    for key in used:
        spec = dims.get(key) or {}
        entry = {
            "label": spec.get("label", key),
            "values": spec.get("values", []),
        }
        if spec.get("description"):
            entry["description"] = spec["description"]
        if dim_label_vi.get(key):
            entry["labelVi"] = dim_label_vi[key]
        vi_values = val_label_vi.get(key) or {}
        if vi_values:
            entry["valuesVi"] = {v: vi_values[v] for v in entry["values"] if v in vi_values}
        catalog[key] = entry
    return catalog


def build(pool: Path, *, catalog: bool) -> dict:
    personas = load_personas(pool)
    if not personas:
        raise SystemExit("no persona_*.yaml under {}".format(pool))
    manifest_path = pool / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    rep = overlap_report(personas)

    keys = sorted(set().union(*[set(p["dims"]) for p in personas]))

    doc: dict = {
        "formatVersion": "1.0",
        "datasetId": manifest.get("datasetId") or pool.name,
        "personaCount": len(personas),
        "dimensionCount": len(keys),
        "provenance": {
            "sources": manifest.get("grounding", {}).get("sources", []),
            "primary": manifest.get("primary"),
            "secondary": manifest.get("secondary"),
            "droppedByFilter": manifest.get("droppedByFilter"),
            "pairing": manifest.get("pairing"),
            "byAssignmentType": manifest.get("grounding", {}).get("byAssignmentType"),
            "scoreableMean": manifest.get("grounding", {}).get("scoreableMean"),
            "assignmentTypes": {
                "observed": "answered by a real respondent; the only values that are measurement",
                "generated": "sampled from persona/synthesis/graph/full_dag.json with the observed "
                             "dimensions pinned; never scoreable",
            },
            "scoreableTypes": sorted(SCOREABLE),
            "caveats": [
                "The two source layers describe DIFFERENT PEOPLE and share no dimension, so pairing "
                "is random. Any demographic-to-driving correlation in this dataset is an artefact of "
                "that pairing, not a measurement. Only within-layer relationships are observed.",
                "vn_locality is generated, not observed: WVS Wave 7 recorded pre-merger province "
                "names and mapping them onto the 34 units effective 2025-07-01 needs the official "
                "merger table. Localities are a population-weighted draw -- draw no conclusions by "
                "province.",
                "Names are generated to be consistent with gender_identity. They identify no one.",
            ],
        },
        "overlap": {
            "note": "Share of dimensions holding an identical value, over all persona pairs.",
            "pairCount": rep["pair_count"],
            "allDimensions": rep["all"],
            "observedOnly": rep["observed"],
            "generatedOnly": rep["generated"],
            "exactDuplicatePersonas": rep["exact_dupes"],
            "dimensionsConstantAcrossPool": rep["constant"],
        },
        "observedDimensions": rep["observed_keys"],
    }

    if catalog:
        doc["dimensionCatalog"] = build_catalog(keys)

    doc["personas"] = [
        {
            "personaId": p["id"],
            "displayName": p["name"],
            "source": p["source"],
            "file": p["file"],
            "groundingSummary": p["summary"],
            "observedDimensions": sorted(
                k for k, v in p["grounding"].items()
                if v.get("assignment_type") in SCOREABLE
            ),
            "dimensions": {
                k: {
                    "value": p["dims"][k],
                    "assignmentType": (p["grounding"].get(k) or {}).get("assignment_type"),
                    "sourceRef": (p["grounding"].get(k) or {}).get("source_ref"),
                    "evidence": (p["grounding"].get(k) or {}).get("evidence"),
                }
                for k in sorted(p["dims"])
            },
        }
        for p in personas
    ]
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pool", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--no-catalog", action="store_true", help="omit the dimension catalog")
    ap.add_argument("--indent", type=int, default=2, help="0 for the most compact file")
    args = ap.parse_args()

    pool = args.pool if args.pool.is_absolute() else REPO_ROOT / args.pool
    doc = build(pool, catalog=not args.no_catalog)
    out = args.out or (REPO_ROOT / "reports" / "{}-dataset.json".format(pool.name))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(doc, ensure_ascii=False, indent=args.indent or None) + "\n",
        encoding="utf-8",
    )

    print("personas        {}".format(doc["personaCount"]))
    print("dimensions each {}".format(doc["dimensionCount"]))
    print("observed dims   {}".format(len(doc["observedDimensions"])))
    print("catalog         {}".format("yes" if "dimensionCatalog" in doc else "no"))
    print("WROTE {}  ({:.1f} MB)".format(out, out.stat().st_size / 1e6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
