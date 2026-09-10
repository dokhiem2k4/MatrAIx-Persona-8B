"""Only the prompt tier reaches the model.

A persona record carries every field it was built from, tiered by what the
field is for. The record is the input to a job -- no config points at the
rendered view -- so the tier has to be honoured where the prompt is built, or
it is not honoured anywhere. Before this, all 48 fields of a vn-driver persona
were rendered, including the 22 marked "no effect on assistant output".

The renderer reads the tier stamped in the persona's own grounding rather than
a list of field names, so a pool that never tiered its fields keeps rendering
all of them.
"""

from __future__ import annotations

import pytest

from matraix.agents.persona.loader import load_persona
from matraix.persona_dimension_catalog import build_dimension_narrative
from matraix.persona_tiers import (
    label_overrides,
    prompt_tier_dimensions,
    stamped_tiers,
)

VN_DRIVER = "persona/datasets/vn-drivers/persona_row-000.yaml"
UNTIERED = "persona/datasets/matraix-persona-dev-sample/persona_0018.yaml"


def test_prompt_tier_keeps_only_prompt_fields():
    persona = load_persona(VN_DRIVER)
    kept = prompt_tier_dimensions(persona.data)

    assert "tone_expected" in kept, "prompt tier must survive"
    assert "vn_address_register" in kept

    assert "demo_children_count" not in kept, "archive tier must not render"
    assert "domain" not in kept
    assert "religiosity" not in kept

    assert "age_bracket" not in kept, "guard tier is never rendered"
    assert "veh_class" not in kept


def test_prompt_tier_matches_the_pools_declared_count():
    """18 prompt-tier fields, plus primary_language as an output contract."""
    persona = load_persona(VN_DRIVER)
    kept = prompt_tier_dimensions(persona.data)

    tiers = stamped_tiers(persona.data)
    assert sum(1 for k in kept if tiers.get(k) == "prompt") == 18
    assert set(kept) - {k for k in kept if tiers.get(k) == "prompt"} == {
        "primary_language"
    }


def test_untiered_persona_renders_every_dimension():
    """A pool with no tier stamped must not silently lose its fields."""
    persona = load_persona(UNTIERED)
    kept = prompt_tier_dimensions(persona.data)

    assert kept == persona.dimensions


def test_narrative_drops_archive_fields():
    persona = load_persona(VN_DRIVER)
    text = "\n".join(build_dimension_narrative(prompt_tier_dimensions(persona.data)))

    assert "Expected tone" in text
    assert "Children" not in text
    assert "Citizenship status" not in text
    assert "Agriculture" not in text


def test_rendered_prompt_drops_the_archive_bullets():
    """Count the lines, not the characters.

    The pool was trimmed to the 31 fields something reads, so the untiered
    render is 31 bullets rather than the 45 it was before. The tier filter is
    what takes it to 19, and that is the number this test is about.
    """
    persona = load_persona(VN_DRIVER)
    full = "\n".join(build_dimension_narrative(persona.dimensions))
    tiered = "\n".join(build_dimension_narrative(prompt_tier_dimensions(persona.data)))

    def bullets(text):
        return [line for line in text.splitlines() if line.startswith("- ")]

    assert len(bullets(full)) == 31, "every field the record still holds"
    assert len(bullets(tiered)) == 19, "18 prompt tier plus the language contract"
    assert len(tiered) < len(full) * 0.75


@pytest.mark.parametrize(
    "dim_id,expected",
    [
        ("cog_skepticism", "Nghi ngờ thông tin"),
        ("trust_level", "Tin tưởng người lạ (WVS)"),
    ],
)
def test_label_overrides_are_available_to_the_renderer(dim_id, expected):
    """Two fields whose default Vietnamese labels both read as 'trust'."""
    assert label_overrides()[dim_id] == expected


def test_system_prompt_renders_only_the_prompt_tier():
    """End to end: the text the model receives, not the helper's return value."""
    from matraix.agents.persona.templating import (
        PERSONA_SYSTEM_TEMPLATE,
        render_persona_template,
        resolve_persona_template,
    )

    persona = load_persona(VN_DRIVER)
    template = resolve_persona_template(persona, None, PERSONA_SYSTEM_TEMPLATE)
    prompt = render_persona_template(template, persona)

    assert "Lý Văn Hải" in prompt, "identity still leads the prompt"
    # tone_expected reaches the model as a directive now, not as a label.
    assert "đi thẳng vào việc" in prompt

    # The trim removed most archive fields outright; the four still on file are
    # kept for the rules, and must not reach the prompt either.
    for archived in ("Secondary", "150-300 km", "Enthusiast"):
        assert f"- {archived}" not in prompt, f"archive tier leaked: {archived}"
    for guarded in ("SUV or crossover", "35-44", "Hung Yen"):
        assert guarded not in prompt, f"guard tier leaked: {guarded}"


def test_untiered_persona_prompt_is_unchanged():
    from matraix.agents.persona.templating import (
        PERSONA_SYSTEM_TEMPLATE,
        render_persona_template,
        resolve_persona_template,
    )

    persona = load_persona(UNTIERED)
    template = resolve_persona_template(persona, None, PERSONA_SYSTEM_TEMPLATE)
    prompt = render_persona_template(template, persona)

    assert "Verbosity: Concise" in prompt


def test_language_contract_survives_the_tier_filter():
    """primary_language is archive tier, but it is an output contract.

    The tier says what changes the *character*; the language instruction says
    what language the answer comes back in. Filtering the second on the tier of
    the first silently dropped the only line telling the model to answer in
    Vietnamese.
    """
    from matraix.agents.persona.templating import (
        PERSONA_SYSTEM_TEMPLATE,
        render_persona_template,
        resolve_persona_template,
    )

    persona = load_persona(VN_DRIVER)
    template = resolve_persona_template(persona, None, PERSONA_SYSTEM_TEMPLATE)
    prompt = render_persona_template(template, persona)

    assert "Default written language" in prompt
