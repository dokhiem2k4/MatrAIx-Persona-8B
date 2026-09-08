import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[3]
        / "application/tasks/chat_0709-vita-drive-singleturn-mode-ab/tests"
    ),
)

from mode_ab_scoring import build_evaluation_payload, reply_length  # noqa: E402

CASE_RUN = {
    "case_id": "vd_0001",
    "case": {
        "case_id": "vd_0001",
        "subintent_code": "destination_poi",
        "parent_intent_code": "journey_navigation_places",
        "user_input": "Dẫn đường đến trạm xăng gần nhất.",
        "input_constraint": "none",
        "state": {"vehicle_state": "driving", "assistant_profile_id": "normal"},
        "source": "generated",
    },
    "observation": {
        "first_user_message": "Chỉ giúp anh cây xăng gần nhất với",
        "first_assistant_message": "Dạ, cây xăng gần nhất cách 800 m ạ.",
        "structured_exposure": [],
        "turn_count": 2,
    },
}


def _facets(payload, context_type="assistant_mode"):
    return {
        f["key"]: f["value"]
        for c in payload["contexts"]
        if c["contextType"] == context_type
        for f in c["facets"]
    }


def test_reply_length_counts_trimmed_characters():
    assert reply_length("  abc  ") == 3
    assert reply_length("") == 0
    assert reply_length(None) == 0


def test_payload_carries_both_experiment_factors():
    facets = _facets(build_evaluation_payload(CASE_RUN, None))
    assert facets["assistant_profile_id"] == "normal"
    assert facets["vehicle_state"] == "driving"


def test_payload_records_reply_length_and_reply_presence():
    facets = _facets(build_evaluation_payload(CASE_RUN, None))
    assert facets["reply_char_count"] == 35
    assert facets["replied"] == "yes"


def test_silent_assistant_is_recorded_not_hidden():
    case_run = {**CASE_RUN, "observation": {**CASE_RUN["observation"], "first_assistant_message": "  "}}
    facets = _facets(build_evaluation_payload(case_run, None))
    assert facets["replied"] == "no"
    assert facets["reply_char_count"] == 0


def test_payload_discloses_that_prompts_are_machine_generated():
    assert _facets(build_evaluation_payload(CASE_RUN, None))["prompt_source"] == "generated"


def test_payload_has_no_correctness_facet():
    facets = _facets(build_evaluation_payload(CASE_RUN, None))
    assert "decision_match" not in facets
    assert "tool_call_match" not in facets


def test_feedback_context_is_appended_when_present():
    payload = build_evaluation_payload(
        CASE_RUN,
        {
            "overallExperienceRating": 7,
            "needConstraintSatisfaction": "yes",
            "personalPreferenceSatisfaction": "partially",
        },
    )
    assert [c["contextType"] for c in payload["contexts"]][-1] == "user_feedback"
    fb = _facets(payload, "user_feedback")
    assert fb["overall_experience_rating"] == 7
    assert fb["need_constraint_satisfaction"] == "yes"
    assert fb["personal_preference_satisfaction"] == "partially"


from mode_ab_scoring import profile_applied  # noqa: E402


def test_profile_applied_when_served_matches_requested():
    case = {"state": {"assistant_profile_id": "cheeky"}}
    assert profile_applied(case, [{"key": "assistantProfileId", "value": "cheeky"}]) == "yes"


def test_profile_not_applied_is_caught_loudly():
    """The deployment answering as `normal` for a `cheeky` case must show up."""
    case = {"state": {"assistant_profile_id": "cheeky"}}
    assert profile_applied(case, [{"key": "assistantProfileId", "value": "normal"}]) == "no"


def test_profile_unknown_when_the_sut_says_nothing():
    case = {"state": {"assistant_profile_id": "cheeky"}}
    assert profile_applied(case, []) == "unknown"


def test_payload_reports_whether_the_factor_took_effect():
    case_run = {
        **CASE_RUN,
        "case": {**CASE_RUN["case"],
                 "state": {**CASE_RUN["case"]["state"], "assistant_profile_id": "cheeky"}},
        "observation": {**CASE_RUN["observation"],
                        "structured_exposure": [{"key": "assistantProfileId", "value": "normal"}]},
    }
    f = _facets(build_evaluation_payload(case_run, None))
    assert f["profile_applied"] == "no"
    assert f["served_profile"] == "normal"
