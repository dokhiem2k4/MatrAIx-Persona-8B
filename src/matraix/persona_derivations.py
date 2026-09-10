"""Derived fields must equal the thing they say they were derived from.

A derived value is not evidence and not a draw: it is a function of another
field, so it has exactly one correct value and can be checked rather than
argued about. Nothing checked it.

``att_voice_assistant`` is derived from ``vn_assistant_task_scope`` -- how much
a driver actually hands over is a firmer signal of their stance than a claim
would be. Two code paths computed it. The crosswalk used the task scope; the
pool that shipped recorded ``derived_from:att_self_driving_cars``, a different
parent entirely, and 29 of 42 personas ended up with a value the map does not
produce: vn-drv-001 delegates navigation and media, which is Neutral, and was
written Opposed.

A repair here is not a resample. The function is deterministic, so the fix is
to evaluate it -- and because the parent may itself be generated, the
correction says nothing about how well grounded the value is, only that it is
now the value it claims to be.
"""

from __future__ import annotations

from typing import Any

#: field -> (parent field, mapping from parent value to derived value).
#: Mirrors ``crosswalks/vn_drivers.py``; the crosswalk builds a persona from a
#: survey row, this checks one that already exists.
DERIVATIONS: dict[str, tuple[str, dict[str, str]]] = {
    "att_voice_assistant": (
        "vn_assistant_task_scope",
        {
            "None": "Opposed",
            "Navigation only": "Skeptical",
            "Navigation and media": "Neutral",
            "Most non-driving tasks": "Positive",
            "Everything including vehicle control": "Enthusiast",
        },
    ),
}


def expected_value(dimensions: dict[str, Any], field: str) -> str | None:
    """What ``field`` must be, given its parent, or None when undecidable."""
    spec = DERIVATIONS.get(field)
    if spec is None:
        return None
    parent, mapping = spec
    parent_value = dimensions.get(parent)
    if parent_value is None:
        return None
    return mapping.get(str(parent_value))


def broken_derivations(persona: dict[str, Any]) -> list[tuple[str, Any, str]]:
    """(field, current value, required value) for each derivation that does not hold."""
    dimensions = persona.get("dimensions") or {}
    out = []
    for field in DERIVATIONS:
        if field not in dimensions:
            continue
        required = expected_value(dimensions, field)
        if required is None:
            continue
        if dimensions.get(field) != required:
            out.append((field, dimensions.get(field), required))
    return out


def apply_derivations(persona: dict[str, Any]) -> list[tuple[str, Any, str]]:
    """Evaluate every derivation in place; returns what was corrected.

    The grounding entry is rewritten too: the parent it names was wrong, and a
    provenance string that points at the wrong field is worse than none.
    """
    dimensions = persona.setdefault("dimensions", {})
    grounding = persona.setdefault("grounding", {})
    corrected = broken_derivations(persona)
    for field, before, required in corrected:
        parent, _ = DERIVATIONS[field]
        dimensions[field] = required
        entry = grounding.setdefault(field, {})
        entry["assignment_type"] = "derived"
        entry["evidence"] = "derived_from:{}".format(parent)
        entry["corrected_from"] = before
    # A derivation that already held may still name the wrong parent.
    for field, (parent, _) in DERIVATIONS.items():
        if field in dimensions and field in grounding:
            grounding[field]["evidence"] = "derived_from:{}".format(parent)
    return corrected
