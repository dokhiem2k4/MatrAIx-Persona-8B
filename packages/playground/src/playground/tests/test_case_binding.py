import json

from playground.case_binding import (
    build_case_brief,
    case_id_from_trial,
    load_cases,
    resolve_session_body,
)

CASE_OMIT = {
    "case_id": "vg_0137",
    "subintent_code": "destination_poi",
    "subintent_label_vi": "Tìm điểm đến/POI",
    "user_input": "Dẫn tôi đến đó",
    "input_constraint": "omit_detail",
    "state": {"network_connectivity": None, "service_state": None},
    "expected": {"decision": "clarify_or_offer"},
}
CASE_PRESERVE = {
    **CASE_OMIT,
    "case_id": "vg_0200",
    "input_constraint": "preserve_invalid_value",
    "user_input": "Vingroup thành lập năm 1850 à?",
}
CASE_FREE = {
    **CASE_OMIT,
    "case_id": "vg_0001",
    "input_constraint": "none",
    "user_input": "Chỉnh nhiệt độ điều hòa 23 độ",
}

SESSION_BODY = {
    "networkConnectivity": "${case.state.network_connectivity}",
    "serviceState": "${case.state.service_state}",
    "constant": "keep-me",
}


def test_resolve_drops_none_values():
    assert resolve_session_body(SESSION_BODY, CASE_OMIT) == {"constant": "keep-me"}


def test_resolve_fills_present_values():
    case = {**CASE_OMIT, "state": {"network_connectivity": "offline", "service_state": None}}
    assert resolve_session_body(SESSION_BODY, case) == {
        "networkConnectivity": "offline",
        "constant": "keep-me",
    }


def test_resolve_without_case_drops_every_placeholder():
    assert resolve_session_body(SESSION_BODY, None) == {"constant": "keep-me"}


def test_resolve_unknown_path_drops_key():
    assert resolve_session_body({"x": "${case.state.nope}"}, CASE_OMIT) == {}


def test_load_cases_returns_empty_when_file_absent(tmp_path):
    assert load_cases("application/tasks/chat_none", repo_root=tmp_path) == {}


def test_load_cases_indexes_by_case_id(tmp_path):
    input_dir = tmp_path / "application" / "tasks" / "chat_x" / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "cases.jsonl").write_text(
        json.dumps(CASE_OMIT, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    cases = load_cases("application/tasks/chat_x", repo_root=tmp_path)
    assert set(cases) == {"vg_0137"}
    assert cases["vg_0137"]["subintent_code"] == "destination_poi"


def test_brief_contains_the_user_input_verbatim():
    assert "Dẫn tôi đến đó" in build_case_brief(CASE_OMIT)


def test_brief_never_leaks_the_expected_decision():
    for case in (CASE_OMIT, CASE_PRESERVE, CASE_FREE):
        assert "clarify_or_offer" not in build_case_brief(case)


def test_omit_brief_forbids_adding_detail():
    brief = build_case_brief(CASE_OMIT)
    assert "do NOT add" in brief
    assert "do NOT correct" not in brief


def test_preserve_brief_forbids_correcting():
    brief = build_case_brief(CASE_PRESERVE)
    assert "do NOT correct" in brief
    assert "do NOT add" not in brief


def test_free_brief_allows_rephrasing_without_extra_constraint():
    brief = build_case_brief(CASE_FREE)
    assert "do NOT add" not in brief
    assert "do NOT correct" not in brief
    assert "own words" in brief


def test_case_id_prefers_the_environment_variable(tmp_path):
    assert case_id_from_trial(tmp_path, {"MATRIX_CHATBOT_CASE_ID": "vg_0009"}) == "vg_0009"


def test_case_id_falls_back_to_trial_config(tmp_path):
    (tmp_path / "config.json").write_text(
        json.dumps({"agent": {"kwargs": {"persona_path": "p.yaml", "case_id": "vg_0137"}}}),
        encoding="utf-8",
    )
    assert case_id_from_trial(tmp_path, {}) == "vg_0137"


def test_case_id_falls_back_to_result_json(tmp_path):
    (tmp_path / "result.json").write_text(
        json.dumps({"config": {"agent": {"kwargs": {"case_id": "vg_0200"}}}}),
        encoding="utf-8",
    )
    assert case_id_from_trial(tmp_path, {}) == "vg_0200"


def test_case_id_is_empty_for_a_legacy_trial(tmp_path):
    assert case_id_from_trial(tmp_path, {}) == ""


def test_case_id_is_empty_without_a_trial_dir():
    assert case_id_from_trial(None, {}) == ""
