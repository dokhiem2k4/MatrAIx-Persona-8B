"""A derived field has one correct value, so nothing about it is a judgement.

att_voice_assistant is a function of vn_assistant_task_scope. Two code paths
computed it and disagreed about the parent: the crosswalk used the task scope,
the shipped pool recorded derived_from:att_self_driving_cars. 29 of 42 personas
held a value the map does not produce.

The audit that surfaced it (scripts/audit_persona_conflicts.py) flagged
att_voice_assistant + vn_assistant_task_scope on 15 personas as the pair no
respondent ever produced -- which is what a broken function looks like from the
outside.
"""

from __future__ import annotations

import glob

import pytest
import yaml

from matraix.persona_derivations import (
    DERIVATIONS,
    apply_derivations,
    broken_derivations,
    expected_value,
)


@pytest.mark.parametrize(
    "scope,stance",
    [
        ("None", "Opposed"),
        ("Navigation only", "Skeptical"),
        ("Navigation and media", "Neutral"),
        ("Most non-driving tasks", "Positive"),
        ("Everything including vehicle control", "Enthusiast"),
    ],
)
def test_every_parent_value_maps(scope, stance):
    assert expected_value({"vn_assistant_task_scope": scope},
                          "att_voice_assistant") == stance


def test_the_map_covers_the_whole_schema_domain():
    import json
    from pathlib import Path

    schema = {
        d["id"]: d["values"]
        for d in json.loads(Path("persona/schema/dimensions.json").read_text())[
            "dimensions"
        ]
    }
    parent, mapping = DERIVATIONS["att_voice_assistant"]
    assert set(mapping) == set(schema[parent])
    assert set(mapping.values()) <= set(schema["att_voice_assistant"])


def test_a_broken_derivation_is_reported():
    persona = {
        "dimensions": {
            "vn_assistant_task_scope": "Navigation and media",
            "att_voice_assistant": "Opposed",
        }
    }
    assert broken_derivations(persona) == [
        ("att_voice_assistant", "Opposed", "Neutral")
    ]


def test_a_holding_derivation_is_silent():
    persona = {
        "dimensions": {
            "vn_assistant_task_scope": "Navigation and media",
            "att_voice_assistant": "Neutral",
        }
    }
    assert broken_derivations(persona) == []


def test_an_absent_parent_is_undecidable_not_wrong():
    persona = {"dimensions": {"att_voice_assistant": "Opposed"}}
    assert broken_derivations(persona) == []


def test_repair_records_what_it_changed_and_names_the_right_parent():
    persona = {
        "dimensions": {
            "vn_assistant_task_scope": "Everything including vehicle control",
            "att_voice_assistant": "Positive",
        },
        "grounding": {
            "att_voice_assistant": {"evidence": "derived_from:att_self_driving_cars"}
        },
    }
    apply_derivations(persona)

    assert persona["dimensions"]["att_voice_assistant"] == "Enthusiast"
    entry = persona["grounding"]["att_voice_assistant"]
    assert entry["evidence"] == "derived_from:vn_assistant_task_scope"
    assert entry["corrected_from"] == "Positive"
    assert entry["assignment_type"] == "derived"


@pytest.mark.parametrize(
    "pool", ["persona/datasets/vn-drivers"]
)
def test_no_committed_persona_carries_a_broken_derivation(pool):
    paths = [p for p in glob.glob(f"{pool}/persona_*.yaml")
             if not p.endswith(".prompt.yaml")]
    assert paths
    broken = [p for p in paths if broken_derivations(yaml.safe_load(open(p)))]
    assert not broken, f"{len(broken)}/{len(paths)} personas: {broken[:3]}"
