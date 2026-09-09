"""Segment headings come from the schema, not from the id spelled out.

Deriving them produced "Att electric vehicles" and "Demo children count" on
every report while the schema already said "Attitude: Electric vehicles" and
"Children".
"""

from backend.service.job_aggregation import _humanize_persona_dimension


def test_the_schema_label_wins_over_the_id():
    assert _humanize_persona_dimension("att_electric_vehicles") == (
        "Attitude: Electric vehicles"
    )
    assert _humanize_persona_dimension("demo_children_count") == "Children"
    assert _humanize_persona_dimension("cog_formality") == "Formality"
    assert _humanize_persona_dimension("demo_driver_status") == "Driving status"


def test_the_short_overrides_still_win_over_the_schema():
    """These are shorter than the schema wording and long-standing in reports."""
    assert _humanize_persona_dimension("age_bracket") == "Age"
    assert _humanize_persona_dimension("cog_skepticism") == "Skepticism"


def test_an_unknown_dimension_still_reads_as_words():
    assert _humanize_persona_dimension("some_new_thing") == "Some new thing"
    assert _humanize_persona_dimension("") == ""
