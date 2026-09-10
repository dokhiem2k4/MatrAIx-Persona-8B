"""Probes measure the behaviour a directive names, so they must not drift.

The distance scorer read 0 of 21 fields as having an effect. Two of those
fields move the output plainly: flipping cog_verbosity shortens the utterance,
and flipping vn_address_register replaces the pronouns outright -- none of
base-a's survive in the mutated arm. Bigram Jaccard could not see either
against a noise floor that already moved 41% of bigrams.

These tests pin the probes themselves. A probe that silently stops matching
would turn a real effect back into "unproven" without anything failing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("scripts").resolve()))

from score_persona_probes import (  # noqa: E402
    ADDRESS_MARKERS,
    _fold,
    _words,
    probe_accent,
    probe_address_pair,
    probe_politeness,
    probe_word_count,
)


def test_fold_strips_vietnamese_diacritics():
    assert _fold("Chị") == "chi"
    assert _fold("điều hòa") == "dieu hoa"
    assert _fold("ĐỘ") == "do"


def test_word_count_ignores_punctuation():
    assert probe_word_count("Vita ơi, giảm nhiệt độ.") == 5


def test_politeness_separates_deference_from_slang():
    assert probe_politeness("Vita, giảm nhiệt độ giúp chị nhé") == 2
    assert probe_politeness("giảm nhiệt độ đi") == -1
    assert probe_politeness("giảm nhiệt độ") == 0


def test_address_probe_matches_only_its_own_register():
    chi_em = probe_address_pair("chi/em")
    minh_ban = probe_address_pair("minh/ban")

    utterance = "Vita ơi, giảm nhiệt độ xuống 22 độ cho chị."
    assert chi_em(utterance) > 0
    assert minh_ban(utterance) == 0


def test_address_markers_cover_every_schema_value():
    import json

    schema = {
        d["id"]: d["values"]
        for d in json.loads(Path("persona/schema/dimensions.json").read_text())[
            "dimensions"
        ]
    }
    assert set(ADDRESS_MARKERS) == set(schema["vn_address_register"])


def test_accent_probe_signs_north_negative_and_south_positive():
    assert probe_accent("rẽ phải rồi đi ô tô") < 0
    assert probe_accent("quẹo phải rồi đi xe hơi") > 0
    assert probe_accent("giảm nhiệt độ") == 0


@pytest.mark.parametrize(
    "text,expected",
    [("", []), ("   ", []), ("a, b. c", ["a", "b", "c"])],
)
def test_words_handles_empty_and_punctuated_input(text, expected):
    assert _words(text) == expected


def test_recorded_finding_the_distance_scorer_missed():
    """The reading this whole file exists to protect, checked against the run.

    Not a threshold to tune -- a record of what the committed arms show, so a
    future change to the probes or the arms cannot quietly erase it.
    """
    import json

    probes = json.loads(Path("data/ablation/probes.json").read_text())

    verbosity = next(p for p in probes["probes"] if p["field"] == "cog_verbosity")
    assert verbosity["verdict"] == "LIVE"
    assert verbosity["delta"] < 0, "flipping to Terse shortened the utterance"

    address = next(
        c for c in probes["compliance"] if c["field"] == "vn_address_register"
    )
    assert address["base_value_survived_in_arm"] == 0.0, (
        "the mutated arm kept none of base-a's pronouns -- the field moved the "
        "output, whatever the distance scorer read"
    )
    assert address["arm_followed_its_own_value"] < 0.5, (
        "and it did not land on the value it was told to use"
    )
