"""A prompt tells the model what to do, not what the character is.

The ablation could not separate any of 21 fields from the noise floor. Every
field reached the model as ``- Formality: Very formal`` -- a fact about the
character, from which a behaviour has to be inferred. Three such labels
(formality, verbosity, expected tone) contradicted each other in the same list.

A directive names the behaviour instead: how many words, which address words,
what to do on a retry. Coval's persona guidance is the same shape -- concrete
word choice and conversational patterns rather than generic labels.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from matraix.agents.persona.loader import load_persona
from matraix.persona_speech import (
    DIRECTIVE_PACK_PATH,
    build_directive_sections,
    load_speech_directives,
)
from matraix.persona_tiers import PROMPT_FIELDS, prompt_tier_dimensions

VN_DRIVER = "persona/datasets/vn-drivers/persona_vn-drv-001.yaml"
SCHEMA = Path("persona/schema/dimensions.json")


def test_every_directive_id_and_value_exists_in_the_schema():
    """A typo in the pack silently drops a field: assert against the schema."""
    schema = {d["id"]: d for d in json.loads(SCHEMA.read_text())["dimensions"]}
    pack = load_speech_directives()

    for dim_id, entries in pack.directives.items():
        assert dim_id in schema, f"unknown dimension: {dim_id}"
        allowed = set(schema[dim_id]["values"])
        for value in entries:
            assert value in allowed, f"{dim_id}: unknown value {value!r}"


def test_directives_cover_every_value_of_every_field_they_claim():
    """Partial coverage means a persona silently falls back to a bare label."""
    schema = {d["id"]: d for d in json.loads(SCHEMA.read_text())["dimensions"]}
    pack = load_speech_directives()

    for dim_id, entries in pack.directives.items():
        missing = set(schema[dim_id]["values"]) - set(entries)
        assert not missing, f"{dim_id} missing directives for {sorted(missing)}"


def test_pack_covers_the_fields_that_shape_an_utterance():
    pack = load_speech_directives()
    for dim_id in (
        "vn_address_register",
        "cog_verbosity",
        "cog_formality",
        "tone_expected",
        "accent_region",
        "vn_retry_tolerance",
    ):
        assert dim_id in pack.directives, f"{dim_id} still renders as a bare label"


def test_uncovered_prompt_fields_are_named_so_the_gap_is_visible():
    """Not every prompt field needs a directive -- but the gap must be explicit."""
    pack = load_speech_directives()
    uncovered = [f for f in PROMPT_FIELDS if f not in pack.directives]
    assert uncovered == [], f"prompt-tier fields with no directive: {uncovered}"


def test_sections_render_as_imperatives_not_label_value_pairs():
    persona = load_persona(VN_DRIVER)
    dims = prompt_tier_dimensions(persona.data)
    sections = build_directive_sections(dims)
    text = "\n".join(sections)

    # vn-drv-001: chi/em, Balanced, Very formal, Concise, Northern, Annoyed
    assert 'tự xưng là "chị"' in text
    assert "12-20 chữ" in text
    assert "cộc hơn" in text

    assert "Formality: Very formal" not in text
    assert "- Verbosity:" not in text


def test_unknown_value_is_skipped_rather_than_crashing():
    sections = build_directive_sections({"cog_verbosity": "Not A Real Value"})
    assert sections == []


def test_pack_file_is_committed_where_the_loader_looks():
    assert DIRECTIVE_PACK_PATH.is_file()


@pytest.mark.parametrize("dim_id", ["cog_verbosity", "vn_address_register"])
def test_directive_text_is_second_person(dim_id):
    """'Bạn ...' -- addressed to the model, not describing a third party."""
    pack = load_speech_directives()
    for text in pack.directives[dim_id].values():
        assert "Bạn" in text or "bạn" in text, text


def test_system_prompt_carries_directives_instead_of_style_labels():
    """End to end: what the model is actually handed."""
    from matraix.agents.persona.templating import (
        PERSONA_SYSTEM_TEMPLATE,
        render_persona_template,
        resolve_persona_template,
    )

    persona = load_persona(VN_DRIVER)
    template = resolve_persona_template(persona, None, PERSONA_SYSTEM_TEMPLATE)
    prompt = render_persona_template(template, persona)

    assert "Bùi Minh Châu" in prompt
    assert 'tự xưng là "chị"' in prompt
    assert "12-20 chữ" in prompt

    for label in ("Verbosity: Balanced", "Formality: Very formal",
                  "Expected tone: Concise", "Regional accent: Northern"):
        assert label not in prompt, f"label survived beside its directive: {label}"

    assert "Default written language" in prompt, "output contract still stands"
