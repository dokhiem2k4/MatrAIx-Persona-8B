#!/usr/bin/env python3
"""Write the tier-A view of every persona in a pool, as a file on disk.

These views existed before this script did -- generated once by hand, then
committed. That is the wrong way round: the view is what the model is actually
shown, so a view nobody can regenerate is a prompt nobody can audit. Whenever
the tier list or the pool changes, run this.

    uv run python scripts/write_prompt_views.py persona/datasets/vn-drivers
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from persona_tiers import PROMPT_FIELDS, prompt_view  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pool", type=Path)
    ap.add_argument("--check", action="store_true",
                    help="fail if any view on disk differs from what this would write")
    args = ap.parse_args()

    paths = sorted(p for p in args.pool.glob("persona_*.yaml")
                   if not p.name.endswith(".prompt.yaml"))
    if not paths:
        print("no persona_*.yaml under {}".format(args.pool))
        return 1

    stale = []
    for path in paths:
        persona = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        text = yaml.safe_dump(prompt_view(persona), allow_unicode=True, sort_keys=False)
        target = path.with_suffix(".prompt.yaml")
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != text:
                stale.append(target.name)
            continue
        target.write_text(text, encoding="utf-8")

    if args.check:
        if stale:
            print("{} view(s) out of date; run without --check:".format(len(stale)))
            for name in stale:
                print("  {}".format(name))
            return 1
        print("{} views up to date".format(len(paths)))
        return 0

    missing = [
        f for f in PROMPT_FIELDS
        if not any(f in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get(
            "dimensions", {}) for p in paths)
    ]
    print("wrote {} prompt views ({} tier-A fields)".format(len(paths), len(PROMPT_FIELDS)))
    if missing:
        print("absent from every persona in this pool: {}".format(", ".join(missing)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
