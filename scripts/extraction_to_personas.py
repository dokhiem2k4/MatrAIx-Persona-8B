#!/usr/bin/env python3
"""Turn an extraction shard into persona YAML files the agent can load.

``run_pipeline.py`` emits ``{user_id, fields[N], observed}`` -- the archival
format. The persona agent loads ``persona/datasets/<set>/persona_<id>.yaml``
with a flat ``dimensions`` mapping. Nothing bridged the two for a locally
produced shard: ``extract_subset.py`` writes persona YAML but pulls rows from
HuggingFace, so a crosswalk you just ran had nowhere to go.

Every dimension carries its provenance (see ``persona/human_extraction/grounding.py``),
so a later reader can tell a surveyed answer from a generated one -- the persona
files in the repo today record only a single file-level ``source``.

Usage:
    uv run python scripts/extraction_to_personas.py \\
        persona/curation/existing_data/raw/wvs_vn/extraction_v1/shard_00.jsonl.gz \\
        --out persona/datasets/vn-wvs7 \\
        --source-ref wvs_wave7_vnm_2020 \\
        --assignment-type observed \\
        --name-prefix VN
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path
from typing import Any, Iterator

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from persona.human_extraction.grounding import (  # noqa: E402
    GroundedPersona,
    summarise,
)


def read_shard(path: Path) -> Iterator[dict[str, Any]]:
    opener = gzip.open if path.name.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def observed_values(record: dict[str, Any]) -> dict[str, Any]:
    """Non-null dimensions from the record.

    Prefer the top-level ``observed`` map the crosswalk wrote; fall back to
    scanning ``fields`` so a shard produced by another writer still converts.
    """
    observed = record.get("observed")
    if isinstance(observed, dict) and observed:
        return {k: v for k, v in observed.items() if v is not None and str(v).strip()}
    out: dict[str, Any] = {}
    for field in record.get("fields") or []:
        if not isinstance(field, dict):
            continue
        value = field.get("value")
        field_id = field.get("field_id") or field.get("id")
        if field_id and value is not None and str(value).strip():
            out[str(field_id)] = value
    return out


def display_name(record: dict[str, Any], values: dict[str, Any], prefix: str) -> str:
    """A stable label, not a fabricated Vietnamese name.

    Inventing "Nguyen Van A" would put a gender and a region into the prompt
    that no respondent supplied, and the corpus already shows what that costs:
    personas named as women carrying ``gender_identity: Man``.
    """
    uid = str(record.get("user_id") or "").strip() or "unknown"
    tail = uid.rsplit("-", 1)[-1]
    bits = [b for b in (values.get("gender_identity"), values.get("age_bracket")) if b]
    suffix = " ({})".format(", ".join(map(str, bits))) if bits else ""
    return "{} {}{}".format(prefix, tail, suffix)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("shard", type=Path, help="extraction shard (.jsonl/.jsonl.gz)")
    parser.add_argument("--out", type=Path, required=True, help="dataset directory")
    parser.add_argument("--source-ref", required=True, help="e.g. wvs_wave7_vnm_2020")
    parser.add_argument("--assignment-type", default="observed")
    parser.add_argument("--name-prefix", default="Persona")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--min-dims",
        type=int,
        default=1,
        help="skip records grounding fewer than this many dimensions",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    personas: list[GroundedPersona] = []
    skipped = 0

    for index, record in enumerate(read_shard(args.shard)):
        if args.limit is not None and len(personas) >= args.limit:
            break
        values = observed_values(record)
        if len(values) < args.min_dims:
            skipped += 1
            continue
        uid = str(record.get("user_id") or "row-{:06d}".format(index))
        persona = GroundedPersona(
            persona_id=uid,
            display_name=display_name(record, values, args.name_prefix),
            source=args.source_ref,
        )
        for dimension, value in sorted(values.items()):
            persona.set(
                dimension,
                value,
                assignment_type=args.assignment_type,
                source_ref=args.source_ref,
                # The respondent id is the whole audit trail: it points at one
                # row of the official microdata.
                evidence="{}:{}".format(args.source_ref, uid),
                confidence=1.0,
            )
        personas.append(persona)
        (args.out / "persona_{}.yaml".format(uid)).write_text(
            yaml.safe_dump(
                persona.to_yaml_dict(), sort_keys=False, allow_unicode=True
            ),
            encoding="utf-8",
        )

    manifest = {
        # ``count`` is the key PersonaPoolService reads; a manifest without it
        # reports a pool of 0 and never falls through to counting the files.
        "count": len(personas),
        "kind": "dataset",
        "datasetId": args.out.name,
        # ``personas`` is what load_manifest reads; without it the loader
        # returns an empty list and never falls through to globbing, so the
        # pool counts but cannot be opened. Filenames rather than dicts: given
        # a dict, load_manifest takes it verbatim and never opens the YAML, so
        # display_name and dimensions go missing and the card falls back to a
        # synthesised name.
        "personas": [
            "persona_{}.yaml".format(p.persona_id) for p in personas
        ],
        "sourceShard": str(args.shard),
        "sourceRef": args.source_ref,
        "assignmentType": args.assignment_type,
        "personaCount": len(personas),
        "skippedBelowMinDims": skipped,
        "grounding": summarise(personas),
    }
    (args.out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("wrote {} persona files -> {}".format(len(personas), args.out))
    if skipped:
        print("  skipped {} record(s) under --min-dims={}".format(skipped, args.min_dims))
    for key, value in manifest["grounding"].items():
        print("  {:18s} {}".format(key, value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
