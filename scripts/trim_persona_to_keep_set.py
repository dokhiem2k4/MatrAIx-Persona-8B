#!/usr/bin/env python3
"""Cut every persona in a pool down to the fields something still reads.

48 fields per persona is 32,000 lines across a pool, and the reason to shorten
it is that nobody reviews 32,000 lines. The reason to be careful is that the
prompt is unaffected either way -- guard and archive never render -- so the
thing a careless cut breaks is not the model's behaviour but the checks, which
fail by going quiet.

``matraix.persona_minimal`` defines the keep set by consumer rather than by
tier, and its tests inject a known violation per rule into a trimmed persona to
prove each one still fires. This script applies it.

What leaves is provenance and only provenance: seventeen fields no rule, no
derivation and no renderer reads. Most of them are answers a person gave. Run
``--dry-run`` first and read the list, because that is the trade.

    uv run python scripts/trim_persona_to_keep_set.py <pool> --dry-run
    uv run python scripts/trim_persona_to_keep_set.py <pool>
    uv run python scripts/trim_persona_to_keep_set.py <pool> --out <other-pool>
"""

from __future__ import annotations

import argparse
import collections
import shutil
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from matraix.persona_minimal import (  # noqa: E402
    dropped_fields,
    keep_set,
    trim_to_keep_set,
)
from matraix.persona_pool import persona_paths  # noqa: E402
from matraix.persona_sources import MEASURED_TYPES  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pool", type=Path)
    ap.add_argument("--out", type=Path, help="defaults to trimming in place")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    paths = persona_paths(args.pool)
    if not paths:
        print(f"no persona_*.yaml under {args.pool}")
        return 1

    out = args.out or args.pool
    if args.out and not args.dry_run:
        shutil.copytree(args.pool, args.out, dirs_exist_ok=True)

    losing: collections.Counter = collections.Counter()
    evidence: collections.Counter = collections.Counter()
    before = after = 0

    for path in paths:
        persona = yaml.safe_load(path.read_text(encoding="utf-8"))
        grounding = persona.get("grounding") or {}
        before = len(persona.get("dimensions") or {})
        for field in dropped_fields(persona):
            losing[field] += 1
            if (grounding.get(field) or {}).get("assignment_type") in MEASURED_TYPES:
                evidence[field] += 1
        trim_to_keep_set(persona)
        after = len(persona["dimensions"])
        if not args.dry_run:
            (out / path.name).write_text(
                yaml.safe_dump(
                    persona, allow_unicode=True, sort_keys=False, width=1000
                ),
                encoding="utf-8",
            )

    print(f"{len(paths)} personas: {before} -> {after} fields ({len(keep_set())} kept)")
    print(f"\ndropping {len(losing)} fields, and with them the evidence behind them:")
    for field, count in sorted(losing.items(), key=lambda kv: -evidence[kv[0]]):
        measured = evidence[field]
        mark = f"{measured}/{count} answered" if measured else "no evidence lost"
        print(f"  {field:28s} {mark}")
    total = sum(evidence.values())
    print(
        f"\n{total} measured values leave the pool "
        f"({total / len(paths):.1f} per persona). They are recoverable only from "
        "git history and the source export."
    )
    if args.dry_run:
        print("\n(dry run -- nothing written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
