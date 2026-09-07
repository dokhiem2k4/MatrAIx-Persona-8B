import collections
import json
from pathlib import Path

CASES_PATH = (
    Path(__file__).resolve().parents[3]
    / "application/tasks/chat_vita-drive-golden-error-recovery/input/cases.jsonl"
)
DECISIONS = {
    "execute",
    "clarify_or_offer",
    "defer_retry",
    "guide_precondition",
    "refuse_not_supported",
}


def _cases():
    with CASES_PATH.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_row_count_matches_spec():
    assert len(_cases()) == 364


def test_case_ids_are_unique():
    ids = [case["case_id"] for case in _cases()]
    assert len(set(ids)) == 364


def test_case_type_distribution_matches_spec():
    counts = collections.Counter(case["case_type"] for case in _cases())
    assert counts == {"unhappy": 304, "happy": 60}


def test_decision_distribution_matches_spec():
    counts = collections.Counter(case["expected"]["decision"] for case in _cases())
    assert counts == {
        "clarify_or_offer": 155,
        "defer_retry": 115,
        "execute": 63,
        "guide_precondition": 21,
        "refuse_not_supported": 10,
    }


def test_input_constraint_distribution_matches_spec():
    counts = collections.Counter(case["input_constraint"] for case in _cases())
    assert counts == {"none": 212, "preserve_invalid_value": 80, "omit_detail": 72}


def test_cases_needing_state_injection_matches_spec():
    needing = [
        case
        for case in _cases()
        if any(value is not None for value in case["state"].values())
    ]
    assert len(needing) == 158


def test_every_decision_is_known():
    assert {case["expected"]["decision"] for case in _cases()} <= DECISIONS


def test_only_execute_cases_expect_tool_calls():
    """``case_type`` does not predict tool calls, but ``decision`` does.

    Six unhappy rows still expect a call: under ``vehicle_state_unavailable`` the
    sensor cannot be read back but the command can still be sent. Eight happy
    rows expect none: they are answered conversationally.
    """
    for case in _cases():
        if case["expected"]["decision"] != "execute":
            assert case["expected"]["tool_calls"] == [], case["case_id"]


def test_every_tool_call_is_normalized():
    for case in _cases():
        for call in case["expected"]["tool_calls"]:
            assert set(call) == {"module", "key", "params"}, case["case_id"]
            assert call["module"] and call["key"], case["case_id"]


def test_identifiers_are_ascii():
    for case in _cases():
        for key in ("case_id", "case_type", "group", "error_type", "subintent_code"):
            assert case[key].isascii(), (case["case_id"], key)


def test_every_subintent_code_is_in_the_taxonomy_file():
    taxonomy = json.loads((CASES_PATH.parent / "intent_taxonomy.json").read_text(encoding="utf-8"))
    for case in _cases():
        assert case["subintent_code"] in taxonomy, case["case_id"]
        assert taxonomy[case["subintent_code"]]["parent_intent_code"] == case["parent_intent_code"]
