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
