import pytest

from application.scripts.convert_vita_golden_dataset import (
    ConversionError,
    build_case_record,
    derive_input_constraint,
)

HAPPY_ROW = {
    "case_type": "happy",
    "group": "Không lỗi",
    "error_type": "Happy case",
    "subintent": "Điều hòa",
    "data_availability": None,
    "vehicle_sensor": None,
    "network_connectivity": None,
    "service_state": None,
    "vehicle_state": None,
    "user_input": "Chỉnh nhiệt độ điều hòa 23 độ",
    "param_validity": "ok",
    "expected_decision": "execute",
    "expected_assistant_response": "Dạ, em đã chỉnh nhiệt độ điều hòa lên 23 độ ạ",
    "expected_tool_calls": '[{"module": "climate", "key": "set_temperature", "params": {"temperature": 23}}]',
    "expected_final_state": "nhiệt độ điều hòa đã được set về 23°C",
    "expected_response_intent": "xác nhận đã chỉnh nhiệt độ lên 23 độ",
}

OFFLINE_ROW = {
    **HAPPY_ROW,
    "case_type": "unhappy",
    "group": "Connectivity",
    "error_type": "No Internet",
    "subintent": "Tìm điểm đến/POI",
    "network_connectivity": "offline",
    "user_input": "Tìm cây xăng gần nhất",
    "expected_decision": "defer_retry",
    "expected_tool_calls": "[]",
}


def test_input_constraint_mapping():
    assert derive_input_constraint("ok") == "none"
    assert derive_input_constraint("missing") == "omit_detail"
    assert derive_input_constraint("invalid") == "preserve_invalid_value"


def test_unknown_param_validity_raises():
    with pytest.raises(ConversionError):
        derive_input_constraint("weird")


def test_case_id_is_zero_padded_and_stable():
    assert build_case_record(HAPPY_ROW, 0)["case_id"] == "vg_0001"
    assert build_case_record(HAPPY_ROW, 363)["case_id"] == "vg_0364"


def test_happy_row_maps_identifiers_to_english():
    record = build_case_record(HAPPY_ROW, 0)
    assert record["subintent_code"] == "climate"
    assert record["parent_intent_code"] == "cabin_vehicle_control"
    assert record["error_type"] == "happy_case"
    assert record["group"] == "no_error"
    assert record["input_constraint"] == "none"


def test_vietnamese_kept_only_as_display_strings():
    record = build_case_record(HAPPY_ROW, 0)
    assert record["subintent_label_vi"] == "Điều hòa"
    assert record["user_input"] == "Chỉnh nhiệt độ điều hòa 23 độ"
    assert record["expected"]["response_intent"] == "xác nhận đã chỉnh nhiệt độ lên 23 độ"


def test_tool_calls_parsed_into_objects():
    record = build_case_record(HAPPY_ROW, 0)
    assert record["expected"]["tool_calls"] == [
        {"module": "climate", "key": "set_temperature", "params": {"temperature": 23}}
    ]


def test_empty_state_values_become_none():
    record = build_case_record(HAPPY_ROW, 0)
    assert record["state"] == {
        "data_availability": None,
        "vehicle_sensor": None,
        "network_connectivity": None,
        "service_state": None,
        "vehicle_state": None,
    }


def test_state_is_carried_through():
    record = build_case_record(OFFLINE_ROW, 5)
    assert record["state"]["network_connectivity"] == "offline"
    assert record["expected"]["tool_calls"] == []
    assert record["expected"]["decision"] == "defer_retry"


def test_unknown_decision_raises():
    with pytest.raises(ConversionError):
        build_case_record({**HAPPY_ROW, "expected_decision": "escalate"}, 0)


def test_malformed_tool_calls_raises():
    with pytest.raises(ConversionError):
        build_case_record({**HAPPY_ROW, "expected_tool_calls": "{not json"}, 0)


def test_unknown_subintent_raises():
    with pytest.raises(ConversionError):
        build_case_record({**HAPPY_ROW, "subintent": "Chưa có nhãn này"}, 0)
