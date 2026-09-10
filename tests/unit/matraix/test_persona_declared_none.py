""""None" is an answer, not a missing answer, when the schema declares it.

The renderer dropped any dimension whose value stringified to "none", to keep
free-text placeholders out of a profile. But 420 of the 1,306 dimensions
declare "None" as one of their values, and it is the most informative one they
have: skill_driving=None is a person who cannot drive, and
vn_assistant_task_scope=None is a driver who delegates nothing to the
assistant. Both vanished from the prompt entirely.

It also silently changed what the field ablation measured. An arm that flipped
a field to "None" removed a line from the prompt instead of changing it, so
three of the twenty-one arms tested a weaker perturbation than the rest while
their verdicts were read off the same table.

The rule: drop a nullish-looking value only when the schema does not declare it
for that dimension.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from matraix.persona_dimension_catalog import (
    build_dimension_narrative,
    collect_dimension_items,
)

SCHEMA = json.loads(Path("persona/schema/dimensions.json").read_text())
BY_ID = {d["id"]: d for d in SCHEMA["dimensions"]}


def _rendered_ids(dimensions, *, skip_defaults=True):
    grouped = collect_dimension_items(dimensions, skip_defaults=skip_defaults)
    return {item[0] for items in grouped.values() for item in items}


@pytest.mark.parametrize(
    "dim_id",
    ["english_proficiency", "vn_assistant_task_scope", "cog_patience",
     "cog_skepticism"],
)
def test_declared_none_is_rendered(dim_id):
    """Fields with no schema default: "None" is simply their value."""
    assert "None" in BY_ID[dim_id]["values"], "precondition: schema declares it"
    assert BY_ID[dim_id].get("defaultValue") is None, "precondition: no default"
    assert dim_id in _rendered_ids({dim_id: "None"})


def test_declared_none_that_is_also_the_default_needs_a_tier():
    """skill_driving defaults to "None", so it is elided on an open profile.

    Suppressing defaults keeps a 1,306-field profile readable. Once a tier has
    chosen the field the suppression is wrong: a driver who cannot drive is
    exactly what the prompt needs to know.
    """
    assert BY_ID["skill_driving"]["defaultValue"] == "None"
    assert "skill_driving" not in _rendered_ids({"skill_driving": "None"})
    assert "skill_driving" in _rendered_ids(
        {"skill_driving": "None"}, skip_defaults=False
    )


def test_undeclared_nullish_is_still_dropped():
    """A placeholder in a free-text field must not reach the prompt."""
    assert "N/A" not in BY_ID["domain"]["values"]
    assert _rendered_ids({"domain": "N/A"}) == set()
    assert _rendered_ids({"domain": "prefer not to say"}) == set()


def test_a_real_absent_value_is_still_dropped():
    assert _rendered_ids({"skill_driving": None}) == set()
    assert _rendered_ids({"skill_driving": ""}) == set()


def test_none_reaches_the_narrative_text():
    text = "\n".join(build_dimension_narrative({"vn_assistant_task_scope": "None"}))
    assert "None" in text


def test_the_whole_schema_agrees_none_is_common():
    """Guards the scale of this: a regression here is not a corner case."""
    declared = [d["id"] for d in SCHEMA["dimensions"] if "None" in (d.get("values") or [])]
    assert len(declared) > 400
