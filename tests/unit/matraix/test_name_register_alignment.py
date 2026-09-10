"""A persona instructed to say "chị" must not be introduced with a man's name.

vn-driver personas fuse a questionnaire respondent with a WVS respondent,
paired at random. gender_identity is guard tier and never rendered, so the
pairing usually stays invisible -- but the display name is rendered, and the
prompt can open "You are <man's name>" and then instruct the speaker to call
herself "chị". Two of the seven registers state a gender; the other five state
none and those personas are left alone.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("scripts").resolve()))

from align_persona_names_to_register import needs_realignment  # noqa: E402


def _persona(register, gender, assignment="observed"):
    return {
        "persona_id": "row-000",
        "display_name": "Lý Hải Yến",
        "dimensions": {"vn_address_register": register, "gender_identity": gender},
        "grounding": {"vn_address_register": {"assignment_type": assignment}},
    }


def test_contradiction_is_reported():
    assert needs_realignment(_persona("anh/em", "Woman")) == "Man"
    assert needs_realignment(_persona("chi/em", "Man")) == "Woman"


def test_agreement_needs_no_change():
    assert needs_realignment(_persona("anh/em", "Man")) is None
    assert needs_realignment(_persona("chi/em", "Woman")) is None


@pytest.mark.parametrize(
    "register", ["toi/ban", "minh/ban", "em/anh-chi", "bac/chau", "co-chu/con"]
)
def test_a_register_that_states_no_gender_is_left_alone(register):
    assert needs_realignment(_persona(register, "Woman")) is None


def test_a_generated_register_is_not_treated_as_evidence():
    """Only a register the respondent stated may override a paired demographic."""
    assert needs_realignment(_persona("anh/em", "Woman", "generated")) is None


def test_absent_register_is_ignored():
    assert needs_realignment(_persona(None, "Woman")) is None
