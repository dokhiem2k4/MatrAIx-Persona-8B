"""R1 failed three real respondents for describing a car they do not own.

The rule reads "owning no car means having no car to be equipped or driven
far", and two of its three clauses follow from that. The third does not: it
fires on *any* answer to cabin_noise, and a person who borrows, rents or is
lent a car can say how noisy it is inside. The questionnaire asks them.

The clause survived because the old 42-persona pool had cabin_noise sampled
rather than answered. Rebuilding the pool from survey rows made it evidence,
and three respondents -- who commute by bicycle, own no car, drive under 50 km
a week and use a phone assistant -- were refused for it. Every value in that
description is an answer someone gave.

Same shape as the R6 fix: the rule was wrong, not the respondents. R1's own
docstring anticipated it -- "revisit when the sample grows" -- and the sample
grew.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
sys.path.insert(0, str(Path("src").resolve()))

from validate_persona_rules import _r1  # noqa: E402

#: The respondent R1 refused, as they answered the form.
BORROWS_A_CAR = {
    "veh_class": "Does not own",
    "veh_assistant_builtin": "None, uses phone assistant",
    "drv_exposure": "Under 50 km",
    "lstyle_commute_mode": "Bike",
    "cabin_noise": "Moderate",
}


def test_a_real_respondent_who_borrows_a_car_is_not_refused():
    assert _r1(BORROWS_A_CAR) is None


def test_describing_cabin_noise_alone_never_fires():
    assert _r1({"veh_class": "Does not own", "cabin_noise": "Very loud"}) is None


def test_a_built_in_assistant_in_a_car_you_do_not_own_still_fires():
    """The clause that does follow from the rule's own claim."""
    detail = _r1(
        {"veh_class": "Does not own", "veh_assistant_builtin": "Built in and used"}
    )
    assert detail is not None
    assert "veh_assistant_builtin" in detail


def test_long_distance_without_a_car_still_fires():
    detail = _r1({"veh_class": "Does not own", "drv_exposure": "300+ km"})
    assert detail is not None
    assert "drv_exposure" in detail


def test_owning_a_car_exempts_everything():
    assert _r1(dict(BORROWS_A_CAR, veh_class="Sedan")) is None
