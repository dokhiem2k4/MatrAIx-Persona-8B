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
    assert facets["decision_match"] == "unknown"
    assert facets["tool_call_match"] == "unknown"
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
