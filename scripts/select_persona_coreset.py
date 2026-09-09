#!/usr/bin/env python3
"""Reduce a pool to the fewest personas that still cover what matters.

Forty-two personas of a country do not describe forty-two kinds of person. On
this pool any two personas already agree on half their measured dimensions, and
the closest pair agrees on three quarters. A reviewer cannot hold forty-two
profiles in their head, and most of the reading is repetition.

Cutting by similarity alone is the obvious move and the wrong one: a set chosen
purely for spread can quietly drop the only Central-accent speaker, and an
assistant evaluated on that set will look better at speech recognition than it
is. So coverage comes first and spread second.

  step 1  keep adding the persona that covers the most missing values on the
          axes named below, until every value on every axis is represented
  step 2  break ties by distance from the personas already chosen

The axes are the ones an in-car assistant is actually judged on -- who the
driver is, how they speak, what they hand over, and when they give up. A value
absent from the coreset is a case the evaluation can no longer see, which is
why the default is full coverage rather than a target size.

    uv run python scripts/select_persona_coreset.py persona/datasets/vn-drivers --dry-run
    uv run python scripts/select_persona_coreset.py persona/datasets/vn-drivers --apply
    uv run python scripts/select_persona_coreset.py <pool> --apply --out <other-pool>
"""

from __future__ import annotations

import argparse
import itertools
import shutil
import statistics
from pathlib import Path
from typing import Any

import yaml

#: Every value of every axis here survives into the coreset. Chosen because
#: losing one removes a case the evaluation can no longer test: drop the only
#: Central accent and an ASR score stops meaning anything; drop the only
#: "Tried it and stopped" and churn becomes invisible.
COVER_AXES = (
    "accent_region",
    "demo_driver_status",
    "vn_address_register",
    "need_state",
    "cog_patience",
    "cog_skepticism",
    "vn_voice_privacy_comfort",
    "veh_assistant_builtin",
    "vn_assistant_task_scope",
    "vn_retry_tolerance",
    "trip_mix",
    "veh_class",
)


def load(pool: Path) -> list[tuple[Path, str, dict[str, Any]]]:
    out = []
    for path in sorted(pool.glob("persona_*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        out.append((path, str(data.get("persona_id") or path.stem), data))
    return out


def varying_keys(rows: list[tuple[Path, str, dict[str, Any]]]) -> list[str]:
    """Dimensions that differ across the pool; constants cannot separate anyone."""
    dims = [r[2].get("dimensions") or {} for r in rows]
    return [
        key
        for key in sorted(dims[0])
        if len({str(d.get(key)) for d in dims}) > 1
    ]


def select(rows, axes: tuple[str, ...], keys: list[str], cap: int | None):
    dims = [r[2].get("dimensions") or {} for r in rows]
    targets = {a: {str(d.get(a)) for d in dims} for a in axes if a in dims[0]}
    needed = sum(len(v) for v in targets.values())

    def distance(i: int, j: int) -> float:
        return sum(1 for k in keys if dims[i].get(k) != dims[j].get(k)) / len(keys)

    chosen: list[int] = []
    covered: dict[str, set[str]] = {a: set() for a in targets}
    while sum(len(v) for v in covered.values()) < needed:
        if cap is not None and len(chosen) >= cap:
            break
        pool = [i for i in range(len(rows)) if i not in chosen]
        if not pool:
            break
        # Gain first, distance only to break ties: a persona that adds a case
        # nobody covers beats one that is merely unlike the others.
        def gain(i: int) -> int:
            return sum(1 for a in targets if str(dims[i].get(a)) not in covered[a])

        def spread(i: int) -> float:
            return min((distance(i, s) for s in chosen), default=1.0)

        pick = max(pool, key=lambda i: (gain(i), spread(i)))
        chosen.append(pick)
        for axis in targets:
            covered[axis].add(str(dims[pick].get(axis)))
    return chosen, targets, covered, distance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pool", type=Path)
    parser.add_argument("--out", type=Path, help="defaults to reducing in place")
    parser.add_argument("--max", type=int, help="stop at this many even if coverage is short")
    parser.add_argument("--apply", action="store_true", help="write; otherwise report only")
    args = parser.parse_args()

    rows = load(args.pool)
    if not rows:
        print("no persona_*.yaml under {}".format(args.pool))
        return 1
    keys = varying_keys(rows)
    chosen, targets, covered, distance = select(rows, COVER_AXES, keys, args.max)

    print("{} personas -> {}".format(len(rows), len(chosen)))
    print("  " + " ".join(rows[i][1] for i in chosen))

    short = [a for a in targets if len(covered[a]) < len(targets[a])]
    print("\naxis coverage:")
    for axis in targets:
        missing = targets[axis] - covered[axis]
        note = "   MISSING {}".format(sorted(missing)) if missing else ""
        print("  {:28s} {}/{}{}".format(axis, len(covered[axis]), len(targets[axis]), note))

    if len(chosen) > 1:
        before = statistics.mean(
            1 - distance(a, b) for a, b in itertools.combinations(range(len(rows)), 2)
        )
        after = statistics.mean(
            1 - distance(a, b) for a, b in itertools.combinations(chosen, 2)
        )
        print("\npairwise agreement: {:.0f}% across the pool -> {:.0f}% in the coreset".format(
            before * 100, after * 100))

    if short:
        print("\nWARNING: --max cut the search short; these axes lost values.")
    if not args.apply:
        print("\nreport only, nothing written")
        return 0

    out_dir = args.out or args.pool
    keep = {rows[i][0].name for i in chosen}

    def rewrite_manifest(target: Path) -> None:
        """A manifest still claiming the old roster is worse than none.

        The playground reads the count from here, not from the directory, so a
        stale manifest makes the UI advertise personas that no longer exist.
        """
        path = target / "manifest.json"
        if not path.is_file():
            return
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        names = sorted(keep)
        if "personas" in data:
            data["personas"] = names
        for field in ("count", "personaCount"):
            if field in data:
                data[field] = len(names)
        data["coreset"] = {
            "selectedFrom": len(rows),
            "coverAxes": list(targets),
            "note": "reduced by scripts/select_persona_coreset.py",
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if out_dir.resolve() == args.pool.resolve():
        for path, _, _ in rows:
            if path.name not in keep:
                path.unlink()
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        for extra in args.pool.iterdir():
            if extra.is_file() and not extra.name.startswith("persona_"):
                shutil.copy2(extra, out_dir / extra.name)
        for path, _, _ in rows:
            if path.name in keep:
                shutil.copy2(path, out_dir / path.name)
    rewrite_manifest(out_dir)
    print("\nwrote {} personas to {}".format(len(chosen), out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
