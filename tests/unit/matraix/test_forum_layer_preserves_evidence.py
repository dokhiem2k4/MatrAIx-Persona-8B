"""The forum layer fills empty fields; it must never overwrite an answered one.

The layer was written when ``vn_address_register`` was null on all 42 personas
and ``cog_verbosity`` came from the synthesis graph, so overwriting both
unconditionally was right. Rebuilding the pool from survey rows changed the
premise: 40 of 81 respondents state their own address register, and running the
layer as written replaced 35 of those 40 measured answers with a draw, marking
each of them ``generated``.

That is the failure the pipeline exists to prevent -- a sampler editing evidence
to look tidy destroys the only thing in the file worth having.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("scripts").resolve()))

from apply_forum_persona_layer import may_overwrite  # noqa: E402


@pytest.mark.parametrize("assignment", ["observed", "direct", "forum_measured"])
def test_a_measured_value_is_never_replaced(assignment):
    persona = {
        "dimensions": {"vn_address_register": "toi/ban"},
        "grounding": {"vn_address_register": {"assignment_type": assignment}},
    }
    assert not may_overwrite(persona, "vn_address_register")


@pytest.mark.parametrize("assignment", ["generated", "derived", "unknown"])
def test_an_unmeasured_value_may_be_filled(assignment):
    persona = {
        "dimensions": {"cog_verbosity": "Balanced"},
        "grounding": {"cog_verbosity": {"assignment_type": assignment}},
    }
    assert may_overwrite(persona, "cog_verbosity")


def test_an_absent_field_may_be_filled():
    assert may_overwrite({"dimensions": {}, "grounding": {}}, "cog_verbosity")


def test_a_null_value_may_be_filled_even_if_grounding_says_observed():
    """An observed null is a question the respondent skipped, not an answer."""
    persona = {
        "dimensions": {"vn_address_register": None},
        "grounding": {"vn_address_register": {"assignment_type": "observed"}},
    }
    assert may_overwrite(persona, "vn_address_register")
