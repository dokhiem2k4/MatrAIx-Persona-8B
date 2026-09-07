from playground.user_sim.kickoff import get_goal_context, load_goal_contexts


def test_registry_has_seeded_contexts():
    ids = {gc.id for gc in load_goal_contexts()}
    assert ids == {"scenario_default", "assigned_case"}


def test_goal_context_labels():
    labels = {gc.id: gc.label for gc in load_goal_contexts()}
    assert labels["scenario_default"] == "Realistic scenario"
    assert "gradual_reveal" not in labels  # collapsed; no longer offered


def test_template_consumes_required_fields():
    t = get_goal_context("scenario_default").template
    for key in ("{domain}", "{sut_description}", "{persona_context}"):
        assert key in t


def test_unknown_raises():
    import pytest
    with pytest.raises(KeyError):
        get_goal_context("nope")


def test_assigned_case_template_consumes_required_fields():
    t = get_goal_context("assigned_case").template
    for key in ("{domain}", "{sut_description}", "{persona_context}", "{case_brief}"):
        assert key in t


def test_assigned_case_does_not_ask_persona_to_invent_a_goal():
    t = get_goal_context("assigned_case").template
    assert "First decide what realistic goal" not in t


def test_scenario_default_has_no_case_slot():
    assert "{case_brief}" not in get_goal_context("scenario_default").template
