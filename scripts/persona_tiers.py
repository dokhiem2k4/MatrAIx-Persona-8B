#!/usr/bin/env python3
"""Tier assignment and grounding bookkeeping shared by the persona scripts.

Two jobs that kept being done wrong in separate places, so they live here once.

``recompute_grounding_summary`` exists because ``grounding_summary`` was written
when a persona still held 1,297 dimensions and no later step updated it. Both
sampled files claimed ``generated: 1268`` while actually holding twenty-two,
which makes the one field that says how much of a persona is evidence unusable.
Any script that adds or removes a dimension must call this before writing.

Fixing it also broke comparability: a corrected counter is indistinguishable
from deleted data unless you know the counter was the thing that changed. See
``docs/persona/grounding-summary-break.md`` before quoting any figure derived
from ``grounding_summary`` on a persona written before commit 850a83c.

``TIERS`` splits the fields by what they are for, rather than deleting any:

  prompt   changes what the assistant would say back, so it is rendered
  guard    never rendered, but the validator uses it to check the prompt tier
           is internally possible -- age and gender constrain the address
           register, locality constrains the accent, and so on
  archive  kept for provenance only: no effect on the assistant's output, or a
           consequence of another field rather than a cause, or not trustworthy

Nothing is dropped from a persona file. A field that leaves the prompt is still
there to answer "where did this come from".
"""

from __future__ import annotations

import collections
from pathlib import Path
from typing import Any

#: The tier tables live in the package: the prompt renderer needs them too, and
#: the second copy is where the drift starts -- the same lesson as
#: ``matraix.persona_pool``. Re-exported here so the scripts keep one import
#: site, never redeclared.
from matraix.persona_tiers import (  # noqa: E402,F401
    ARCHIVE_REASONS,
    CONSEQUENCE,
    DUPLICATE,
    GUARD_FIELDS,
    LABEL_OVERRIDES,
    LOW_CONFIDENCE,
    NO_EFFECT,
    PROMPT_FIELDS,
    UNCONDITIONED,
    tier_of,
)

OBSERVED_TYPES = {"observed", "direct", "forum_measured"}


from matraix.persona_pool import persona_paths  # noqa: E402,F401




def recompute_grounding_summary(persona: dict[str, Any]) -> dict[str, Any]:
    """Rewrite grounding_summary from the persona's own fields.

    The invariant the acceptance criteria ask for: the assignment-type counts
    add up to the number of dimensions actually present.
    """
    dims = persona.get("dimensions") or {}
    grounding = persona.get("grounding") or {}
    by_type: collections.Counter = collections.Counter()
    sources: set[str] = set()
    for key in dims:
        entry = grounding.get(key)
        if not isinstance(entry, dict):
            by_type["unknown"] += 1
            continue
        by_type[str(entry.get("assignment_type") or "unknown")] += 1
        ref = entry.get("source_ref")
        if ref:
            sources.add(str(ref))
    summary = {
        "scoreable": sum(by_type[t] for t in OBSERVED_TYPES),
        "byAssignmentType": dict(sorted(by_type.items())),
        "sources": sorted(sources),
        "dimensionCount": len(dims),
    }
    persona["grounding_summary"] = summary
    return summary


def apply_tiers(persona: dict[str, Any]) -> dict[str, int]:
    """Stamp every grounding entry with its tier; return the tier counts."""
    dims = persona.get("dimensions") or {}
    grounding = persona.setdefault("grounding", {})
    counts: collections.Counter = collections.Counter()
    for key in dims:
        entry = grounding.get(key)
        if not isinstance(entry, dict):
            entry = {"assignment_type": "unknown"}
            grounding[key] = entry
        tier = tier_of(key)
        entry["tier"] = tier
        if tier == "archive":
            entry["excluded_reason"] = ARCHIVE_REASONS.get(key, NO_EFFECT)
        else:
            entry.pop("excluded_reason", None)
        counts[tier] += 1
    return dict(counts)


def _prompt_grounding(entry: dict[str, Any] | None, field: str) -> dict[str, Any]:
    entry = entry or {}
    out: dict[str, Any] = {
        "assignment_type": entry.get("assignment_type"),
        "confidence": entry.get("confidence"),
    }
    if field in UNCONDITIONED:
        out["unconditioned"] = True
        out["unconditioned_reason"] = UNCONDITIONED[field]
    return out


def prompt_view(persona: dict[str, Any]) -> dict[str, Any]:
    """The tier-A subset, ready to render.

    A separate file rather than a filter at render time: whoever writes the
    prompt should not have to know the tier rules, and a view on disk can be
    diffed when an utterance comes out wrong.
    """
    dims = persona.get("dimensions") or {}
    grounding = persona.get("grounding") or {}
    kept = {k: dims[k] for k in PROMPT_FIELDS if k in dims and dims[k] is not None}
    return {
        "persona_id": persona.get("persona_id"),
        "display_name": persona.get("display_name"),
        "tier": "prompt",
        "dimensions": kept,
        "grounding": {k: _prompt_grounding(grounding.get(k), k) for k in kept},
        "label_overrides": {k: v for k, v in LABEL_OVERRIDES.items() if k in kept},
    }
