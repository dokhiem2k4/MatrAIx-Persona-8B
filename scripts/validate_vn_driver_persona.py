#!/usr/bin/env python3
"""Check Vietnamese driver personas against the vn_driver_persona standard.

Standard: persona/human_extraction/standards/vn_driver_persona_v1.json

Complements validate_extraction.py rather than replacing it. That one checks
schema validity; this checks the three things a persona set used to score an
in-car assistant cannot do without:

  1. Tier A complete  -- a missing dimension means that persona cannot be
                         compared with any other on it.
  2. Eligibility      -- someone who does not drive cannot rate a car assistant.
  3. Coverage parity  -- across the 541 personas on hand, coverage ranges from
                         7 to 1,290 dimensions. That gap becomes a confound
                         when the scores are read.

Usage:
    uv run python scripts/validate_vn_driver_persona.py --input drivers.jsonl
    uv run python scripts/validate_vn_driver_persona.py --input 'persona/datasets/**/persona_*.yaml'
"""

from __future__ import annotations

import argparse
import glob
import gzip
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent
STANDARD = REPO_ROOT / "persona/human_extraction/standards/vn_driver_persona_v1.json"
SCHEMA = REPO_ROOT / "persona/schema/dimensions.json"


def load_records(pattern: str) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield (label, dimensions) from .jsonl(.gz) or persona YAML."""
    paths = sorted(glob.glob(pattern, recursive=True))
    if not paths:
        raise SystemExit("no files matched: {}".format(pattern))
    for path in paths:
        p = Path(path)
        if p.suffix in {".jsonl", ".gz"} or p.name.endswith(".jsonl.gz"):
            opener = gzip.open if p.name.endswith(".gz") else open
            with opener(p, "rt", encoding="utf-8") as handle:
                for i, line in enumerate(handle):
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    dims = rec.get("fields") or rec.get("dimensions") or rec.get("observed") or {}
                    if isinstance(dims, dict) and dims and isinstance(next(iter(dims.values())), dict):
                        # {dim: {"value": x, "provenance": y}}
                        dims = {k: v.get("value") for k, v in dims.items()}
                    yield "{}#{}".format(p.name, rec.get("user_id") or i), dims
        else:
            import yaml

            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            yield data.get("display_name") or p.stem, data.get("dimensions") or {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="glob for jsonl(.gz) or persona yaml")
    parser.add_argument("--standard", type=Path, default=STANDARD)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--max-report", type=int, default=12)
    parser.add_argument(
        "--skip-eligibility",
        action="store_true",
        help="skip the drives-a-car check (for auditing older persona pools)",
    )
    args = parser.parse_args()

    std = json.loads(args.standard.read_text(encoding="utf-8"))
    schema = {d["id"]: d for d in json.loads(args.schema.read_text(encoding="utf-8"))["dimensions"]}

    tier_a = [d["id"] for d in std["tierA"]["dimensions"]]
    forbidden = set(std["forbiddenValues"]["literalStrings"])
    elig = std["eligibility"]["rules"][0]

    missing_counts: dict[str, int] = {d: 0 for d in tier_a}
    bad_values: list[str] = []
    ineligible: list[str] = []
    grounded: list[int] = []
    n = 0

    for label, dims in load_records(args.input):
        n += 1
        filled = 0
        for dim_id, value in dims.items():
            spec = schema.get(dim_id)
            if spec is None:
                bad_values.append("{}: {} = key not in schema".format(label, dim_id))
                continue
            if value is None:
                continue
            text = str(value)
            # "None" is only junk when the dimension's enum does not admit it.
            if text in forbidden and text not in map(str, spec["values"]):
                bad_values.append("{}: {} = {!r} (junk string, should be null)".format(label, dim_id, text))
                continue
            if text not in map(str, spec["values"]):
                bad_values.append("{}: {} = {!r} (outside enum)".format(label, dim_id, text))
                continue
            filled += 1
        grounded.append(filled)

        for dim_id in tier_a:
            v = dims.get(dim_id)
            if v is None or str(v) in forbidden and str(v) not in map(str, schema[dim_id]["values"]):
                missing_counts[dim_id] += 1

        if not args.skip_eligibility:
            status = str(dims.get(elig["dimension"]) or "")
            if status not in elig["mustBeOneOf"]:
                ineligible.append("{}: {} = {!r}".format(label, elig["dimension"], status or None))

    print("standard   : {} v{}".format(std["standardId"], std["version"]))
    print("personas   : {}".format(n))
    if grounded:
        stdev = statistics.pstdev(grounded) if len(grounded) > 1 else 0.0
        print(
            "coverage   : mean {:.1f} | min {} | max {} | stdev {:.1f}".format(
                statistics.mean(grounded), min(grounded), max(grounded), stdev
            )
        )

    errors = 0

    incomplete = {d: c for d, c in missing_counts.items() if c}
    print("\n-- Tier A ({} required dimensions) --".format(len(tier_a)))
    if incomplete:
        errors += sum(incomplete.values())
        for dim_id, c in sorted(incomplete.items(), key=lambda kv: -kv[1])[: args.max_report]:
            print("   MISSING  {:28s} {}/{} personas".format(dim_id, c, n))
        if len(incomplete) > args.max_report:
            print("   ... and {} more dimensions".format(len(incomplete) - args.max_report))
    else:
        print("   OK -- complete on every persona")

    print("\n-- Value validity --")
    if bad_values:
        errors += len(bad_values)
        print("   {} invalid values".format(len(bad_values)))
        for line in bad_values[: args.max_report]:
            print("   {}".format(line))
        if len(bad_values) > args.max_report:
            print("   ... and {} more".format(len(bad_values) - args.max_report))
    else:
        print("   OK -- every value is inside its enum")

    if not args.skip_eligibility:
        print("\n-- Driving eligibility --")
        if ineligible:
            errors += len(ineligible)
            print("   {}/{} personas do not drive".format(len(ineligible), n))
            for line in ineligible[: args.max_report]:
                print("   {}".format(line))
        else:
            print("   OK -- every persona drives")

    print("\n-- Coverage parity --")
    limit = std["coverageParity"]["maxGroundedStdevInBatch"]
    if len(grounded) > 1:
        stdev = statistics.pstdev(grounded)
        if stdev > limit:
            errors += 1
            print(
                "   SKEWED  stdev {:.1f} > limit {} -- uneven coverage will leak into the scores".format(
                    stdev, limit
                )
            )
        else:
            print("   OK -- stdev {:.1f} <= {}".format(stdev, limit))
    else:
        print("   (skipped, only one persona)")

    print("\n{}".format("PASS" if errors == 0 else "FAIL -- {} problem(s)".format(errors)))
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
