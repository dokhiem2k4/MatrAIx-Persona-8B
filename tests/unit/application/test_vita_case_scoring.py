import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[3]
        / "application/tasks/chat_0709-vita-drive-golden-error-recovery/tests"
    ),
)

from case_scoring import classify_case_integrity  # noqa: E402

OMIT = {"input_constraint": "omit_detail", "user_input": "Dẫn tôi đến đó"}
PRESERVE = {"input_constraint": "preserve_invalid_value", "user_input": "Vingroup thành lập năm 1850 à?"}
FREE = {"input_constraint": "none", "user_input": "Chỉnh nhiệt độ điều hòa 23 độ"}


def test_free_case_is_not_applicable():
    assert classify_case_integrity(FREE, "Cho anh 23 độ nhé") == "not_applicable"


def test_omit_case_stays_ok_when_still_vague():
    assert classify_case_integrity(OMIT, "Dẫn giúp em tới chỗ đó với") == "ok"


def test_omit_case_violated_when_persona_names_a_place():
    assert classify_case_integrity(OMIT, "Dẫn em tới Aeon Long Biên với") == "violated"


def test_omit_case_violated_when_persona_adds_a_number():
    assert classify_case_integrity(
        {"input_constraint": "omit_detail", "user_input": "Chỉnh nhiệt độ"},
        "Chỉnh nhiệt độ lên 23 độ nhé",
    ) == "violated"


def test_preserve_case_ok_when_wrong_number_kept():
    assert classify_case_integrity(PRESERVE, "Vingroup lập năm 1850 đúng không anh?") == "ok"


def test_preserve_case_violated_when_wrong_number_dropped():
    assert classify_case_integrity(PRESERVE, "Vingroup thành lập năm nào nhỉ?") == "violated"


def test_empty_message_is_violated_for_constrained_cases():
    assert classify_case_integrity(OMIT, "") == "violated"


from case_scoring import build_evaluation_payload, observed_decision, tool_calls_match  # noqa: E402


def _facets(payload):
    return {
        facet["key"]: facet["value"]
        for context in payload["contexts"]
        if context["contextType"] == "error_recovery"
        for facet in context["facets"]
    }


def test_decision_read_from_structured_exposure():
    assert observed_decision([{"key": "decision", "value": "clarify_or_offer"}]) == (
        "clarify_or_offer",
        "structured",
    )


def test_decision_unavailable_when_exposure_empty():
    assert observed_decision([]) == ("", "unavailable")


def test_decision_unavailable_when_key_missing():
    assert observed_decision([{"key": "toolCalls", "value": []}]) == ("", "unavailable")


def test_tool_calls_match_ignores_params():
    expected = [{"module": "climate", "key": "set_temperature", "params": {"temperature": 23}}]
    observed = [{"module": "climate", "key": "set_temperature", "params": {"temperature": 24}}]
    assert tool_calls_match(expected, observed) is True


def test_tool_calls_match_is_order_insensitive():
    expected = [{"module": "a", "key": "x"}, {"module": "b", "key": "y"}]
    observed = [{"module": "b", "key": "y"}, {"module": "a", "key": "x"}]
    assert tool_calls_match(expected, observed) is True


def test_tool_calls_mismatch_on_extra_call():
    assert tool_calls_match([], [{"module": "climate", "key": "set_temperature"}]) is False


def test_tool_calls_accepts_the_action_alias_from_the_sut():
    assert tool_calls_match(
        [{"module": "phone", "key": "make_call"}],
        [{"module": "phone", "action": "make_call"}],
    ) is True


CASE_RUN_MATCH = {
    "case_id": "vg_0137",
    "case": {
        "case_id": "vg_0137",
        "case_type": "unhappy",
        "group": "understanding",
        "error_type": "missing_information",
        "subintent_code": "destination_poi",
        "input_constraint": "omit_detail",
        "user_input": "Dẫn tôi đến đó",
        "expected": {"decision": "clarify_or_offer", "tool_calls": []},
    },
    "observation": {
        "first_user_message": "Dẫn giúp em tới chỗ đó với",
        "first_assistant_message": "Em chưa rõ anh chị muốn đến đâu ạ.",
        "structured_exposure": [{"key": "decision", "value": "clarify_or_offer"}],
        "turn_count": 2,
    },
}


def test_payload_marks_match_and_carries_facets():
    facets = _facets(build_evaluation_payload(CASE_RUN_MATCH, None))
    assert facets["decision_match"] == "match"
    assert facets["tool_call_match"] == "match"
    assert facets["case_integrity"] == "ok"
    assert facets["decision_source"] == "structured"
    assert facets["error_type"] == "missing_information"
    assert facets["subintent_code"] == "destination_poi"


def test_payload_marks_mismatch_when_decision_differs():
    case_run = {
        **CASE_RUN_MATCH,
        "observation": {
            **CASE_RUN_MATCH["observation"],
            "structured_exposure": [{"key": "decision", "value": "execute"}],
        },
    }
    facets = _facets(build_evaluation_payload(case_run, None))
    assert facets["decision_match"] == "mismatch"
    assert facets["observed_decision"] == "execute"
    assert facets["expected_decision"] == "clarify_or_offer"


def test_payload_flags_a_leaking_persona_without_blaming_the_sut():
    case_run = {
        **CASE_RUN_MATCH,
        "observation": {
            **CASE_RUN_MATCH["observation"],
            "first_user_message": "Dẫn em tới Aeon Long Biên với",
        },
    }
    assert _facets(build_evaluation_payload(case_run, None))["case_integrity"] == "violated"


def test_payload_marks_unknown_when_decision_unavailable():
    case_run = {
        "case_id": "vg_0001",
        "case": {
            "case_id": "vg_0001",
            "case_type": "happy",
            "group": "no_error",
            "error_type": "happy_case",
            "subintent_code": "climate",
            "input_constraint": "none",
            "user_input": "Chỉnh nhiệt độ điều hòa 23 độ",
            "expected": {"decision": "execute", "tool_calls": []},
        },
        "observation": {
            "first_user_message": "Cho anh 23 độ nhé",
            "first_assistant_message": "Dạ em chỉnh rồi ạ.",
            "structured_exposure": [],
            "turn_count": 1,
        },
    }
    facets = _facets(build_evaluation_payload(case_run, None))
    # Nothing came back at all -> unavailable, which is a different problem from
    # "the SUT answered but its signals do not separate the two classes".
    assert facets["decision_match"] == "unavailable"
    assert facets["tool_call_match"] == "unavailable"
    assert facets["decision_source"] == "unavailable"


def test_payload_appends_user_feedback_when_present():
    payload = build_evaluation_payload(CASE_RUN_MATCH, {"overallExperienceRating": 8})
    types = [context["contextType"] for context in payload["contexts"]]
    assert types == ["error_recovery", "user_feedback"]


import json  # noqa: E402

CASES_PATH = (
    Path(__file__).resolve().parents[3]
    / "application/tasks/chat_0709-vita-drive-golden-error-recovery/input/cases.jsonl"
)


def test_integrity_heuristic_has_no_false_positives_on_the_real_dataset():
    """A persona that says the case verbatim must never be flagged as violating.

    This guards the heuristic against drifting into blaming the harness for
    trials that were actually clean.
    """
    with CASES_PATH.open(encoding="utf-8") as handle:
        cases = [json.loads(line) for line in handle if line.strip()]
    verdicts = [classify_case_integrity(case, case["user_input"]) for case in cases]
    assert verdicts.count("violated") == 0
    assert verdicts.count("not_applicable") == 212
    assert verdicts.count("ok") == 152


from case_scoring import (  # noqa: E402
    decision_from_signals,
    observed_tool_names,
)


def _exp(**kw):
    return [{"key": k, "value": v} for k, v in kw.items()]


def test_permission_signal_maps_to_guide_precondition():
    assert decision_from_signals(_exp(needsPermission=True)) == ("guide_precondition", "derived")


def test_follow_up_signal_maps_to_clarify():
    assert decision_from_signals(_exp(needsFollowUp=True)) == ("clarify_or_offer", "derived")


def test_confirmation_signal_maps_to_clarify():
    assert decision_from_signals(_exp(needsConfirmation=True)) == ("clarify_or_offer", "derived")


def test_permission_wins_over_follow_up():
    got, _ = decision_from_signals(_exp(needsPermission=True, needsFollowUp=True))
    assert got == "guide_precondition"


def test_successful_tool_run_maps_to_execute():
    exposure = _exp(turnStatus="completed", toolResults=[{"success": True, "tool": "set_hvac_temperature"}])
    assert decision_from_signals(exposure) == ("execute", "derived")


def test_failed_tool_run_maps_to_defer_retry():
    exposure = _exp(turnStatus="completed", toolResults=[{"success": False, "tool": "set_hvac_temperature"}])
    assert decision_from_signals(exposure) == ("defer_retry", "derived")


def test_plain_answer_stays_unknown_because_metadata_cannot_tell():
    """A conversational answer and a refusal look identical in metadata.

    Forcing one of them would invent data, so this stays unknown on purpose.
    """
    assert decision_from_signals(_exp(turnStatus="completed", intent="general_qa")) == ("", "unknown")


def test_empty_exposure_is_unavailable_not_unknown():
    assert decision_from_signals([]) == ("", "unavailable")


def test_observed_tool_names_read_from_vehicle_results():
    exposure = _exp(toolResults=[{"success": True, "tool": "set_hvac_temperature"},
                                 {"success": True, "tool": "get_vehicle_state"}])
    assert observed_tool_names(exposure) == ["get_vehicle_state", "set_hvac_temperature"]


def test_observed_tool_names_empty_when_no_tool_ran():
    assert observed_tool_names(_exp(turnStatus="completed")) == []


CASE_NO_TOOL = {
    "case_id": "vg_0137",
    "case": {"case_id": "vg_0137", "case_type": "unhappy", "group": "understanding",
             "error_type": "missing_information", "subintent_code": "destination_poi",
             "input_constraint": "omit_detail", "user_input": "Dẫn tôi đến đó",
             "expected": {"decision": "clarify_or_offer", "tool_calls": []}},
    "observation": {"first_user_message": "Dẫn giúp em tới chỗ đó với",
                    "first_assistant_message": "Em chưa rõ ạ.",
                    "structured_exposure": _exp(needsFollowUp=True, turnStatus="completed"),
                    "turn_count": 2},
}


def test_derived_decision_scores_a_no_tool_case_end_to_end():
    f = _facets(build_evaluation_payload(CASE_NO_TOOL, None))
    assert f["decision_match"] == "match"
    assert f["decision_source"] == "derived"
    assert f["tool_call_match"] == "match"      # kỳ vọng rỗng, SUT không chạy tool


def test_unexpected_tool_run_is_caught_without_any_name_mapping():
    case = {**CASE_NO_TOOL, "observation": {**CASE_NO_TOOL["observation"],
            "structured_exposure": _exp(needsFollowUp=True,
                                        toolResults=[{"success": True, "tool": "set_hvac_temperature"}])}}
    f = _facets(build_evaluation_payload(case, None))
    assert f["tool_call_match"] == "mismatch"
    assert f["observed_tools"] == "set_hvac_temperature"


def test_case_expecting_a_tool_is_unmapped_until_the_name_table_exists():
    case = {**CASE_NO_TOOL,
            "case": {**CASE_NO_TOOL["case"],
                     "expected": {"decision": "execute", "tool_calls": [{"module": "climate", "key": "set_temperature"}]}},
            "observation": {**CASE_NO_TOOL["observation"],
                            "structured_exposure": _exp(turnStatus="completed",
                                                        toolResults=[{"success": True, "tool": "set_hvac_temperature"}])}}
    f = _facets(build_evaluation_payload(case, None))
    assert f["decision_match"] == "match"       # execute suy được
    assert f["tool_call_match"] == "unmapped"   # tên tool chưa ánh xạ
