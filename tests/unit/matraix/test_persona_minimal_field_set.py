"""Cutting a persona down to what something actually reads.

48 fields per persona is 32,000 lines across a pool and nobody reviews that.
The cut is safe for the prompt by construction -- guard and archive are never
rendered -- but "changes no prompt" is not the only property worth keeping. A
rule that reads a field it no longer has stops firing, silently, and the pool
that produced a bicycle commuter driving 300 km a week goes unchecked again.

So the keep set is defined by consumers, not by tier:

  prompt tier          the 18 fields the model is given
  guard tier           read by R1, R4 and R6, and by the sampler
  five archive fields  read by R1, R5 and the att_voice_assistant derivation
  primary_language     the output-language contract

31 fields. The 17 that go are read by nothing at all.

The proof that matters is not "the file got shorter". It is that every rule
still catches the violation it was written for, checked by injecting one, and
that all 81 prompts come back byte-identical.
"""

from __future__ import annotations

import copy
import glob

import pytest
import yaml

from matraix.persona_minimal import (
    RULE_DEPENDENCIES,
    keep_set,
    trim_to_keep_set,
)
from matraix.persona_tiers import GUARD_FIELDS, PROMPT_FIELDS

POOLS = ["persona/datasets/vn-drivers", "persona/datasets/vn-drivers-rows"]

#: One known violation per rule, as the rule's own tests state it.
INJECTIONS = {
    "R1": {"veh_class": "Does not own", "drv_exposure": "300+ km"},
    "R3": {
        "att_self_driving_cars": "Opposed",
        "vn_assistant_task_scope": "Everything including vehicle control",
    },
    "R4": {"urbanicity": "Rural", "vn_locality": "Ha Noi"},
    "R5": {
        "english_proficiency": "Native",
        "primary_language": "Vietnamese",
        "highest_education": "Secondary",
    },
    "R6": {
        "veh_assistant_builtin": "None, uses no assistant",
        "assistant_usage_freq": "Almost every trip",
    },
    "R7": {"cog_verbosity": "Terse", "tone_expected": "Detailed"},
}


def _persona(pool):
    path = sorted(
        p for p in glob.glob(f"{pool}/persona_*.yaml")
        if not p.endswith(".prompt.yaml")
    )[0]
    return yaml.safe_load(open(path))


def test_keep_set_is_the_three_tiers_plus_what_rules_read():
    keep = keep_set()
    assert set(PROMPT_FIELDS) <= keep, "the prompt tier is the point"
    assert set(GUARD_FIELDS) <= keep, "R1, R4 and R6 read guard fields"
    assert RULE_DEPENDENCIES <= keep
    assert "primary_language" in keep, "output-language contract"
    assert len(keep) == 31


@pytest.mark.parametrize("pool", POOLS)
def test_the_committed_pool_holds_exactly_the_keep_set(pool):
    """The pools were trimmed; this is the state, not a step."""
    persona = _persona(pool)
    assert set(persona["dimensions"]) == keep_set()
    assert len(persona["dimensions"]) == 31


@pytest.mark.parametrize("pool", POOLS)
def test_trimming_again_changes_nothing(pool):
    """Idempotent, so the script is safe to re-run after any pool rebuild."""
    persona = _persona(pool)
    trimmed = trim_to_keep_set(copy.deepcopy(persona))

    assert set(trimmed["dimensions"]) == set(persona["dimensions"])
    assert trimmed["grounding_summary"] == persona["grounding_summary"]


def test_the_seventeen_dropped_fields_are_read_by_nothing():
    """Named, so removing a consumer's input cannot pass unnoticed."""
    dropped = {
        "cabin_noise", "cult_vietnam", "demo_children_count",
        "demo_citizenship_status", "demo_employment_status",
        "demo_marital_status", "demo_religion_affiliation", "domain",
        "lang_vietnamese", "life_stage", "need_state", "region", "religiosity",
        "safety_sensitivity", "socioeconomic_band", "topic_cars", "trust_level",
    }
    assert len(dropped) == 17
    assert not (dropped & keep_set())


@pytest.mark.parametrize("pool", POOLS)
def test_every_prompt_survives_byte_identical(pool):
    """The constraint the whole cut exists to satisfy."""
    import os
    import tempfile

    from matraix.agents.persona.loader import load_persona
    from matraix.agents.persona.templating import (
        PERSONA_SYSTEM_TEMPLATE,
        render_persona_template,
        resolve_persona_template,
    )

    def render(doc):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as handle:
            yaml.safe_dump(doc, handle, allow_unicode=True, sort_keys=False)
            path = handle.name
        try:
            persona = load_persona(path)
            return render_persona_template(
                resolve_persona_template(persona, None, PERSONA_SYSTEM_TEMPLATE),
                persona,
            )
        finally:
            os.unlink(path)

    paths = sorted(
        p for p in glob.glob(f"{pool}/persona_*.yaml")
        if not p.endswith(".prompt.yaml")
    )
    for path in paths:
        doc = yaml.safe_load(open(path))
        assert render(doc) == render(trim_to_keep_set(copy.deepcopy(doc))), path


@pytest.mark.parametrize("code", sorted(INJECTIONS))
def test_every_rule_still_fires_after_the_cut(code):
    """A shorter file that stops catching contradictions is not a saving."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path("scripts").resolve()))
    from validate_persona_rules import violations

    persona = trim_to_keep_set(_persona(POOLS[1]))
    for field, value in INJECTIONS[code].items():
        assert field in persona["dimensions"], f"{code} lost its input: {field}"
        persona["dimensions"][field] = value

    assert any(c == code for c, _ in violations(persona))


def test_the_derivation_check_still_has_its_inputs():
    from matraix.persona_derivations import broken_derivations

    persona = trim_to_keep_set(_persona(POOLS[1]))
    persona["dimensions"]["vn_assistant_task_scope"] = "Navigation and media"
    persona["dimensions"]["att_voice_assistant"] = "Opposed"
    assert broken_derivations(persona)


@pytest.mark.parametrize("pool", POOLS)
def test_counters_are_rewritten_not_left_stale(pool):
    from matraix.persona_sources import sources_disagree

    trimmed = trim_to_keep_set(_persona(pool))
    assert trimmed["grounding_summary"]["dimensionCount"] == 31
    assert not sources_disagree(trimmed)
