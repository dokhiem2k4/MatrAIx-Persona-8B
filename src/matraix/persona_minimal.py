"""The smallest persona that still does every job a persona is asked to do.

Trimming for readability is easy to get wrong in one specific way: the prompt
is unaffected -- guard and archive are never rendered, so the cut is safe for
the model by construction -- and the *checks* quietly stop working. A rule
whose input is gone does not fail; it returns None, reports zero violations,
and the pool that produced a bicycle commuter driving 300 km a week goes
unexamined.

So the keep set is defined by who reads a field, not by which tier it sits in:

  18  prompt tier          what the model is given
   8  guard tier           R1, R4, R6 and the sampler's coherence constraints
   4  archive, but read    drv_exposure (R1), english_proficiency and
                           highest_education (R5), att_voice_assistant (its own
                           derivation)
   1  primary_language     the output-language contract, and R5's third input
  --
  31

The seventeen that go are read by nothing: no rule, no derivation, no
renderer. They are provenance and nothing else, which is a real loss -- most of
them are answers a person gave -- and it is the trade this module exists to
make explicit rather than to pretend away.

``RULE_DEPENDENCIES`` is written out rather than derived from the rule sources,
because parsing ``d.get("...")`` out of a function body would fail silently the
first time someone writes a rule differently. The guarantee comes from tests
instead: each rule is handed a persona trimmed by this module with a known
violation injected, and has to still catch it.
"""

from __future__ import annotations

import copy
from typing import Any

from matraix.persona_sources import MEASURED_TYPES, apply_sources
from matraix.persona_tiers import GUARD_FIELDS, OUTPUT_CONTRACT_FIELDS, PROMPT_FIELDS

#: Fields outside the prompt and guard tiers that a rule or derivation reads.
#: Adding a rule that reads an archive field means adding it here, and the
#: injection tests fail until you do.
RULE_DEPENDENCIES = frozenset(
    {
        "drv_exposure",          # R1: driving far without a car
        "english_proficiency",   # R5: native English without a reason
        "highest_education",     # R5
        "att_voice_assistant",   # its own derivation from vn_assistant_task_scope
    }
)


def keep_set() -> frozenset[str]:
    """Every field something still reads."""
    return frozenset(
        set(PROMPT_FIELDS)
        | set(GUARD_FIELDS)
        | set(RULE_DEPENDENCIES)
        | set(OUTPUT_CONTRACT_FIELDS)
    )


def dropped_fields(persona: dict[str, Any]) -> list[str]:
    """Fields this persona holds that nothing reads, in file order."""
    keep = keep_set()
    return [k for k in (persona.get("dimensions") or {}) if k not in keep]


def trim_to_keep_set(persona: dict[str, Any], *, in_place: bool = True) -> dict[str, Any]:
    """Drop every field nothing reads, and rewrite the counters that describe it.

    The grounding entry goes with the dimension. Leaving it behind would keep
    the file long while making ``grounding`` describe fields that are no longer
    there -- the shape that made ``sources`` claim a persona twenty-seven times
    larger than the file.
    """
    if not in_place:
        persona = copy.deepcopy(persona)
    keep = keep_set()
    dimensions = persona.get("dimensions") or {}
    grounding = persona.get("grounding") or {}

    for key in [k for k in dimensions if k not in keep]:
        del dimensions[key]
        grounding.pop(key, None)

    # Grounding entries that outlived their dimension: the removed_incoherent
    # records document a deletion, and a record about a field that is itself
    # gone documents nothing.
    for key in [k for k in grounding if k not in dimensions]:
        del grounding[key]

    by_type: dict[str, int] = {}
    sources: set[str] = set()
    for key in dimensions:
        entry = grounding.get(key)
        kind = str((entry or {}).get("assignment_type") or "unknown")
        by_type[kind] = by_type.get(kind, 0) + 1
        ref = (entry or {}).get("source_ref")
        if ref:
            sources.add(str(ref))
    persona["grounding_summary"] = {
        "scoreable": sum(by_type.get(t, 0) for t in MEASURED_TYPES),
        "byAssignmentType": dict(sorted(by_type.items())),
        "sources": sorted(sources),
        "dimensionCount": len(dimensions),
    }
    apply_sources(persona)
    return persona
