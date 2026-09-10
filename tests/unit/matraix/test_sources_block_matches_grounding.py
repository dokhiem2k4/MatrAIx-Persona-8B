""""sources" counted a persona that no longer exists.

The block at the head of every vn-driver file claims how many values each
source contributed. It was written before the trim step cut 1,306 dimensions
down to 48 and nothing recomputed it, so vn-drv-001 declares full_dag: 1266
while its grounding holds seven, and vn_driver_survey_2026: 8 against an actual
22. Whoever reads the header reads a persona 27 times larger than the file.

Same class as the grounding_summary break -- a counter nobody updated -- and
the same consequence: a corrected counter is indistinguishable from deleted
data unless the correction is written down.
"""

from __future__ import annotations

import glob

import pytest
import yaml

from matraix.persona_sources import recompute_sources, sources_disagree

POOLS = ["persona/datasets/vn-drivers"]


def _personas(pool):
    return [p for p in glob.glob(f"{pool}/persona_*.yaml")
            if not p.endswith(".prompt.yaml")]


def test_recompute_counts_what_the_grounding_actually_says():
    persona = {
        "dimensions": {"a": 1, "b": 2, "c": 3},
        "grounding": {
            "a": {"source_ref": "survey", "assignment_type": "observed"},
            "b": {"source_ref": "survey", "assignment_type": "observed"},
            "c": {"source_ref": "dag", "assignment_type": "generated"},
        },
    }
    sources = recompute_sources(persona)
    assert sources["survey"]["values"] == 2
    assert sources["survey"]["measured"] is True
    assert sources["dag"]["values"] == 1
    assert sources["dag"]["measured"] is False
    assert sources["survey"]["assignment_types"] == {"observed": 2}


def test_a_source_with_no_surviving_dimension_disappears():
    """The trim removed every field a source contributed: it is not a source."""
    persona = {
        "dimensions": {"a": 1},
        "grounding": {"a": {"source_ref": "survey", "assignment_type": "observed"}},
        "sources": {"dag": {"values": 1266}},
    }
    assert "dag" not in recompute_sources(persona)


def test_grounding_entries_without_a_dimension_are_not_counted():
    """A removed_incoherent record documents a deletion; it contributed nothing."""
    persona = {
        "dimensions": {"a": 1},
        "grounding": {
            "a": {"source_ref": "survey", "assignment_type": "observed"},
            "gone": {"assignment_type": "removed_incoherent"},
        },
    }
    assert recompute_sources(persona) == {
        "survey": {
            "values": 1,
            "assignment_types": {"observed": 1},
            "measured": True,
        }
    }


@pytest.mark.parametrize("pool", POOLS)
def test_every_committed_persona_declares_what_it_holds(pool):
    paths = _personas(pool)
    assert paths, f"no personas in {pool}"
    wrong = [p for p in paths if sources_disagree(yaml.safe_load(open(p)))]
    assert not wrong, f"{len(wrong)}/{len(paths)} personas have a stale sources block"
