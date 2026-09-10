"""Three generated style axes, drawn independently, describe an impossible speaker.

cog_verbosity, cog_formality and tone_expected were each sampled from their own
distribution, so the 42-persona pool holds 38 distinct combinations of the
three -- including a driver who rambles past 35 words while going straight to
the point from the first word, and one who speaks in slang while keeping a
formal distance.

Rendered as labels this was invisible; the model averaged it away and the
ablation measured no effect from any of the three. Rendered as directives the
contradiction is explicit in the prompt, so it has to be refused at generation
time instead.

Only contradictions by definition are listed. A very formal driver who is also
playful is unusual, not impossible, and a survey exists to capture unusual
people -- so that pair is deliberately absent.
"""

from __future__ import annotations

import glob

import pytest
import yaml

from matraix.persona_style_rules import (
    INCOMPATIBLE_STYLE_PAIRS,
    REPAIR_PREFERENCE,
    style_conflict,
)

POOL = "persona/datasets/vn-drivers"


@pytest.mark.parametrize(
    "dims",
    [
        {"cog_verbosity": "Terse", "tone_expected": "Detailed"},
        {"cog_verbosity": "Rambling", "tone_expected": "Concise"},
        {"cog_formality": "Slangy", "tone_expected": "Formal"},
        {"cog_formality": "Very formal", "tone_expected": "Blunt"},
    ],
)
def test_impossible_pairs_are_refused(dims):
    assert style_conflict(dims) is not None


@pytest.mark.parametrize(
    "dims",
    [
        {"cog_verbosity": "Terse", "cog_formality": "Very formal"},
        {"cog_formality": "Very formal", "tone_expected": "Playful"},
        {"cog_verbosity": "Balanced", "cog_formality": "Slangy",
         "tone_expected": "Blunt"},
        {"cog_verbosity": "Concise", "tone_expected": "Detailed"},
    ],
)
def test_merely_unusual_combinations_pass(dims):
    """The bar is contradiction, not improbability."""
    assert style_conflict(dims) is None


def test_missing_fields_never_fire():
    assert style_conflict({}) is None
    assert style_conflict({"cog_verbosity": "Terse"}) is None


def test_conflict_names_both_fields_and_values():
    detail = style_conflict({"cog_verbosity": "Terse", "tone_expected": "Detailed"})
    assert "cog_verbosity=Terse" in detail
    assert "tone_expected=Detailed" in detail


def test_repair_prefers_the_least_evidenced_field():
    """tone_expected is a bare full_dag draw; cog_verbosity is forum-calibrated."""
    assert REPAIR_PREFERENCE.index("tone_expected") < REPAIR_PREFERENCE.index(
        "cog_verbosity"
    )


def test_every_listed_pair_uses_real_schema_values():
    import json
    from pathlib import Path

    schema = {
        d["id"]: set(d["values"])
        for d in json.loads(Path("persona/schema/dimensions.json").read_text())[
            "dimensions"
        ]
    }
    for (field_a, value_a), (field_b, value_b) in INCOMPATIBLE_STYLE_PAIRS:
        assert value_a in schema[field_a], f"{field_a}={value_a}"
        assert value_b in schema[field_b], f"{field_b}={value_b}"


def test_pool_conflicts_are_counted_not_assumed():
    """Records how many of the 42 personas the rule fires on today.

    Not a threshold to satisfy -- a number to notice when it moves. A rule that
    fires on most of a pool is a rule about the sampler, not about the people.
    """
    paths = [p for p in glob.glob(f"{POOL}/persona_*.yaml")
             if not p.endswith(".prompt.yaml")]
    assert len(paths) == 42

    hits = [
        p for p in paths
        if style_conflict(yaml.safe_load(open(p))["dimensions"]) is not None
    ]
    assert len(hits) <= 42 // 3, (
        f"{len(hits)}/42 personas conflict -- too many for a rule about people"
    )


def test_tone_values_match_the_schema():
    import json
    from pathlib import Path
    from matraix.persona_style_rules import TONE_VALUES

    schema = {
        d["id"]: d["values"]
        for d in json.loads(Path("persona/schema/dimensions.json").read_text())[
            "dimensions"
        ]
    }
    assert set(TONE_VALUES) == set(schema["tone_expected"])


def test_allowed_tones_excludes_only_the_conflicting_one():
    from matraix.persona_style_rules import allowed_tones

    assert "Detailed" not in allowed_tones({"cog_verbosity": "Terse"})
    assert "Concise" in allowed_tones({"cog_verbosity": "Terse"})

    assert "Concise" not in allowed_tones({"cog_verbosity": "Rambling"})
    assert "Formal" not in allowed_tones({"cog_formality": "Slangy"})


def test_repair_clears_the_conflict_without_touching_the_other_axes():
    dims = {"cog_verbosity": "Terse", "cog_formality": "Neutral",
            "tone_expected": "Detailed"}
    from matraix.persona_style_rules import allowed_tones

    for tone in sorted(allowed_tones(dims)):
        repaired = dict(dims, tone_expected=tone)
        assert style_conflict(repaired) is None
        assert repaired["cog_verbosity"] == "Terse"
        assert repaired["cog_formality"] == "Neutral"
