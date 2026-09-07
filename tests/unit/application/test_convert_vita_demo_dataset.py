import pytest

from application.scripts.convert_vita_demo_dataset import (
    DemoConversionError,
    build_demo_case_record,
)

ROW = {
    "intent_code": "journey_navigation_places",
    "subintent_code": "destination_poi",
    "subintent_name": "Tìm điểm đến/POI",
    "input": "Dẫn đường đến trạm xăng gần nhất.",
    "vehicle_state": "driving",
    "ASSISTANT_MODE": "quiet",
    "source": "generated",
    "note": None,
}


def test_case_id_is_zero_padded():
    assert build_demo_case_record(ROW, 0)["case_id"] == "vd_0001"
    assert build_demo_case_record(ROW, 275)["case_id"] == "vd_0276"


def test_identifiers_and_display_string_are_separated():
    record = build_demo_case_record(ROW, 0)
    assert record["subintent_code"] == "destination_poi"
    assert record["parent_intent_code"] == "journey_navigation_places"
    assert record["subintent_label_vi"] == "Tìm điểm đến/POI"
    assert record["user_input"] == "Dẫn đường đến trạm xăng gần nhất."


def test_state_carries_the_two_experiment_factors():
    assert build_demo_case_record(ROW, 0)["state"] == {
        "vehicle_state": "driving",
        "assistant_mode": "quiet",
    }


def test_no_input_constraint_because_there_is_no_ground_truth():
    assert build_demo_case_record(ROW, 0)["input_constraint"] == "none"


def test_provenance_is_recorded_so_reports_can_disclose_it():
    assert build_demo_case_record(ROW, 0)["source"] == "generated"


def test_subintent_code_must_agree_with_the_taxonomy():
    with pytest.raises(DemoConversionError):
        build_demo_case_record({**ROW, "subintent_code": "charger_search"}, 0)


def test_parent_intent_must_agree_with_the_taxonomy():
    with pytest.raises(DemoConversionError):
        build_demo_case_record({**ROW, "intent_code": "my_car"}, 0)


def test_unknown_vehicle_state_raises():
    with pytest.raises(DemoConversionError):
        build_demo_case_record({**ROW, "vehicle_state": "flying"}, 0)


def test_unknown_assistant_mode_raises():
    with pytest.raises(DemoConversionError):
        build_demo_case_record({**ROW, "ASSISTANT_MODE": "chatty"}, 0)


def test_empty_input_raises():
    with pytest.raises(DemoConversionError):
        build_demo_case_record({**ROW, "input": "   "}, 0)


from application.scripts.convert_vita_demo_dataset import (  # noqa: E402
    REAL_PROFILES,
    rebuild_grid_over_profiles,
)


def _grid():
    records = []
    for sub in ("destination_poi", "climate"):
        for state in ("driving", "parking"):
            for i in range(3):
                records.append(
                    {
                        "case_id": "vd_{:04d}".format(len(records) + 1),
                        "subintent_code": sub,
                        "parent_intent_code": "x",
                        "user_input": "{}-{}-{}".format(sub, state, i),
                        "input_constraint": "none",
                        "state": {"vehicle_state": state, "assistant_mode": "quiet"},
                        "source": "generated",
                    }
                )
    return records


def test_profiles_are_the_seven_the_deployment_actually_exposes():
    assert REAL_PROFILES == ("normal", "sweet", "chao", "cheeky", "bright", "rustic", "calm")


def test_grid_is_pairs_times_profiles():
    out = rebuild_grid_over_profiles(_grid())
    assert len(out) == 4 * len(REAL_PROFILES)   # 2 subintent x 2 state x 7


def test_every_profile_gets_the_same_number_of_cases():
    import collections

    counts = collections.Counter(c["state"]["assistant_profile_id"] for c in rebuild_grid_over_profiles(_grid()))
    assert set(counts.values()) == {4}


def test_the_dead_assistant_mode_factor_is_gone():
    for case in rebuild_grid_over_profiles(_grid()):
        assert "assistant_mode" not in case["state"]


def test_prompt_is_rotated_so_profile_and_wording_are_not_confounded():
    """A profile always paired with the same prompt would confound the two."""
    out = rebuild_grid_over_profiles(_grid())
    for profile in REAL_PROFILES:
        prompts = {c["user_input"] for c in out if c["state"]["assistant_profile_id"] == profile}
        assert len(prompts) > 1, profile


def test_case_ids_are_renumbered_and_unique():
    out = rebuild_grid_over_profiles(_grid())
    assert out[0]["case_id"] == "vd_0001"
    assert len({c["case_id"] for c in out}) == len(out)
