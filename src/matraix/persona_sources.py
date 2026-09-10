"""The ``sources`` block, recomputed from what the persona actually holds.

``grounding_summary`` had this bug and it was fixed; ``sources`` sits three
lines above it in the same file and was missed. It claims how many values each
source contributed, and it was written before the trim step cut a persona from
1,306 dimensions to 48. Nothing recomputed it, so vn-drv-001 declares
``full_dag: 1266`` while its grounding holds seven, and ``vn_driver_survey_2026:
8`` against an actual 22 -- a header describing a persona 27 times larger than
the file underneath it.

The counts come from ``grounding``, keyed by the dimensions that survive, so a
source whose every field was trimmed away stops being listed rather than
shrinking to a wrong number. Grounding entries with no surviving dimension --
the ``removed_incoherent`` records that document a deleted value -- contribute
nothing, because they contributed nothing.

Read ``docs/persona/grounding-summary-break.md`` before comparing any figure
derived from ``sources`` across the commit that introduced this: a corrected
counter is indistinguishable from deleted data.
"""

from __future__ import annotations

import collections
from typing import Any

#: Assignment types that mean "a person answered this". A source contributing
#: only these is measured; one contributing a draw is not.
MEASURED_TYPES = frozenset({"observed", "direct", "forum_measured"})


def recompute_sources(persona: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """What each source contributed to the dimensions this persona still has."""
    dimensions = persona.get("dimensions") or {}
    grounding = persona.get("grounding") or {}

    by_source: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for key in dimensions:
        entry = grounding.get(key)
        if not isinstance(entry, dict):
            continue
        ref = entry.get("source_ref")
        if not ref:
            continue
        by_source[str(ref)][str(entry.get("assignment_type") or "unknown")] += 1

    out: dict[str, dict[str, Any]] = {}
    for source in sorted(by_source):
        types = by_source[source]
        out[source] = {
            "values": sum(types.values()),
            "assignment_types": dict(sorted(types.items())),
            # Measured only when every value it supplied is an answer someone
            # gave. A source that mixes a draw into its contribution is not
            # evidence for the persona as a whole.
            "measured": bool(types) and set(types) <= MEASURED_TYPES,
        }
    return out


def sources_disagree(persona: dict[str, Any]) -> bool:
    """True when the declared block does not match the persona's own grounding."""
    return (persona.get("sources") or {}) != recompute_sources(persona)


def apply_sources(persona: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Rewrite the block in place; returns it. Call before writing a persona."""
    sources = recompute_sources(persona)
    persona["sources"] = sources
    return sources
