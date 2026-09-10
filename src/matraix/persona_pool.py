"""Listing the personas in a pool, without the views that sit beside them.

``persona_*.yaml`` was unambiguous until pools started carrying a rendered
projection of each persona as ``persona_<id>.prompt.yaml``. The glob matches
both, so every caller silently doubled its pool: a 42-persona pool reported 84
in the playground, the validator passed on views that carry no fields for a
rule to fire against, and a job builder would have run -- and billed -- twice.

A view is a projection of a persona, never an input beside it. One predicate,
used everywhere, so a future sibling file cannot reintroduce the same bug.
"""

from __future__ import annotations

from pathlib import Path

#: Suffixes that mark a file as a rendered view rather than a persona record.
VIEW_SUFFIXES = (".prompt.yaml",)


def is_persona_file(path: Path) -> bool:
    name = path.name
    return name.startswith("persona_") and not name.endswith(VIEW_SUFFIXES)


def persona_paths(pool: Path, *, recursive: bool = False) -> list[Path]:
    """Sorted persona records in ``pool``, excluding rendered views."""
    it = pool.rglob("persona_*.yaml") if recursive else pool.glob("persona_*.yaml")
    return sorted(p for p in it if is_persona_file(p))


def count_personas(pool: Path) -> int:
    return sum(1 for _ in persona_paths(pool))


def has_personas(pool: Path) -> bool:
    return any(True for _ in persona_paths(pool))
