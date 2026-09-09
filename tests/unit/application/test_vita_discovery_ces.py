"""The discovery task turns a moderator's guide into runnable cases.

Two things must hold. The scenarios are copied word for word -- they were
written to be read to a person without improvisation, and a paraphrase would
quietly change what is being measured. And the safety rule from the guide
("CES-4 ≤ 4 → đánh dấu rủi ro") is applied exactly as written, not softened.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
TASK = REPO_ROOT / "application/tasks/chat_0909-vita-discovery-ces"
sys.path.insert(0, str(TASK / "tests"))
sys.path.insert(0, str(REPO_ROOT))

import ces_scoring  # noqa: E402
from application.scripts.convert_vita_discovery_tasklist import (  # noqa: E402
    capability_number,
    capability_title,
    split_probe,
    strip_context_prefix,
)


@pytest.fixture(scope="module")
def cases():
    path = TASK / "input/cases.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# ------------------------------------------------------------------ dataset

def test_all_eight_capability_groups_are_covered(cases):
    assert sorted({c["capability_number"] for c in cases}) == [1, 2, 3, 4, 5, 6, 7, 8]


def test_every_capability_but_the_first_runs_in_both_vehicle_states(cases):
    """The guide gives capability 1 a parked scenario only."""
    by_number = {}
    for case in cases:
        by_number.setdefault(case["capability_number"], set()).add(case["vehicle_state"])
    assert by_number[1] == {"parked"}
    for number in range(2, 9):
        assert by_number[number] == {"parked", "driving"}, number


def test_scenarios_are_present_and_in_vietnamese(cases):
    for case in cases:
        assert case["scenario_vi"].strip(), case["case_id"]
        assert case["success_criteria_vi"].strip(), case["case_id"]
        # Mojibake would have eaten the diacritics; this is the tripwire.
        assert "?" not in case["scenario_vi"][:40], case["case_id"]


def test_the_context_marker_becomes_a_field_not_prose(cases):
    for case in cases:
        assert not case["scenario_vi"].startswith("["), case["case_id"]
        assert case["vehicle_state"] in ("parked", "driving")


def test_the_moderator_probe_is_not_spoken_by_the_persona(cases):
    """"Probe thêm nếu..." is an instruction to the human running the session."""
    for case in cases:
        assert "Probe thêm" not in case["scenario_vi"], case["case_id"]
    assert any(c["moderator_probe_vi"] for c in cases)


def test_ids_stay_ascii_while_labels_stay_vietnamese(cases):
    for case in cases:
        case["case_id"].encode("ascii")
        case["capability_code"].encode("ascii")
        assert case["capability_label_vi"]


# ------------------------------------------------------------------ parsing

def test_both_spellings_of_parked_are_stripped():
    """The guide writes it "đỗ" in some cells and "đổ" in others."""
    assert strip_context_prefix("[Đang đỗ xe] Anh/Chị...") == "Anh/Chị..."
    assert strip_context_prefix("[Đang đổ xe] Anh/Chị...") == "Anh/Chị..."
    assert strip_context_prefix("[Đang lái xe] Trong lúc...") == "Trong lúc..."
    assert strip_context_prefix("Không có nhãn") == "Không có nhãn"


def test_the_probe_is_split_off_not_dropped():
    body, probe = split_probe("Hãy hỏi Vita. Probe thêm nếu chưa rõ: ví dụ thời tiết")
    assert body == "Hãy hỏi Vita."
    assert probe == "ví dụ thời tiết"
    assert split_probe("Không có probe") == ("Không có probe", "")


def test_capability_header_is_parsed_into_number_and_title():
    header = "Nhóm năng lực 6 - An ninh và an toàn: Yêu cầu Vita kiểm tra..."
    assert capability_number(header) == 6
    assert capability_title(header) == "An ninh và an toàn"


# ------------------------------------------------------------------ scoring

BASE_RUN = {
    "case": {
        "case_id": "vd_04_driving",
        "capability_number": 4,
        "capability_label_vi": "Dẫn đường",
        "vehicle_state": "driving",
        "scenario_vi": "Hãy nhờ Vita tìm trạm sạc.",
        "success_criteria_vi": "Diễn đạt được nhu cầu.",
    },
    "observation": {
        "turn_count": 2,
        "turns": [
            {"user_message": "Tìm trạm sạc giúp tôi", "assistant_message": "Bạn muốn gần đây không ạ?",
             "structured_exposure": [{"key": "turnStatus", "value": "awaiting"}]},
            {"user_message": "Ừ gần nhất", "assistant_message": "Đã dẫn đường.",
             "structured_exposure": [{"key": "toolResults", "value": [{"tool": "open_route", "success": True}]}]},
        ],
    },
}


def facets(payload, context_type):
    return {
        f["key"]: f["value"]
        for c in payload["contexts"]
        if c["contextType"] == context_type
        for f in c["facets"]
    }


def test_a_low_safety_score_marks_risk_even_when_the_task_succeeded():
    """The guide's rule, verbatim: CES-4 ≤ 4 is a risk regardless of outcome."""
    feedback = {"ces1Effort": 7, "ces2Information": 7, "ces3Presentation": 7,
                "ces4Attention": 4, "taskCompleted": "yes"}
    payload = ces_scoring.build_evaluation_payload(BASE_RUN, feedback)
    outcome = facets(payload, "task_outcome")
    assert outcome["safety_at_risk"] == "yes"
    assert outcome["outcome_status"] == "unresolved"
    assert "an toàn" in outcome["outcome_reason"]


def test_a_safe_and_finished_task_passes():
    feedback = {"ces1Effort": 6, "ces2Information": 6, "ces3Presentation": 5,
                "ces4Attention": 6, "taskCompleted": "yes"}
    outcome = facets(ces_scoring.build_evaluation_payload(BASE_RUN, feedback), "task_outcome")
    assert outcome["outcome_status"] == "resolved"
    assert outcome["safety_at_risk"] == "no"


def test_an_unfinished_task_fails_whatever_the_scores():
    feedback = {"ces1Effort": 7, "ces2Information": 7, "ces3Presentation": 7,
                "ces4Attention": 7, "taskCompleted": "no"}
    outcome = facets(ces_scoring.build_evaluation_payload(BASE_RUN, feedback), "task_outcome")
    assert outcome["outcome_status"] == "unresolved"


def test_out_of_range_and_missing_scores_become_none_not_zero():
    """A zero would drag every average down and read as a real answer."""
    feedback = {"ces1Effort": 9, "ces2Information": 0, "ces3Presentation": "5",
                "ces4Attention": True, "taskCompleted": "yes"}
    ces = facets(ces_scoring.build_evaluation_payload(BASE_RUN, feedback), "customer_effort")
    assert ces["ces1_effort"] is None
    assert ces["ces2_information"] is None
    assert ces["ces3_presentation"] is None
    assert ces["ces4_attention"] is None  # bool is not a score
    assert ces["ces_mean"] is None


def test_ces3_records_that_no_screen_was_shown():
    """A voice-only run must never be compared straight to a human who could see."""
    ces = facets(ces_scoring.build_evaluation_payload(BASE_RUN, {"ces3Presentation": 5}), "customer_effort")
    assert ces["ces3_basis"] == "audio_only"


def test_low_scored_statements_are_named_for_the_follow_up_question():
    feedback = {"ces1Effort": 3, "ces2Information": 6, "ces3Presentation": 4, "ces4Attention": 7}
    ces = facets(ces_scoring.build_evaluation_payload(BASE_RUN, feedback), "customer_effort")
    assert ces["low_scored_statements"] == "ces1_effort, ces3_presentation"


def test_the_four_watched_behaviours_are_reported():
    coverage = facets(ces_scoring.build_evaluation_payload(BASE_RUN, {}), "capability_coverage")
    assert coverage["continued_conversation"] == "yes"
    assert coverage["asked_to_choose_or_confirm"] == "yes"
    assert coverage["driver_had_to_correct"] == "no"
    assert coverage["state_legible"] == "yes"


def test_a_correction_by_the_driver_is_detected():
    run = json.loads(json.dumps(BASE_RUN))
    run["observation"]["turns"][1]["user_message"] = "Không phải, ý tôi là cây xăng"
    coverage = facets(ces_scoring.build_evaluation_payload(run, {}), "capability_coverage")
    assert coverage["driver_had_to_correct"] == "yes"


def test_a_single_turn_cannot_count_as_a_correction():
    run = json.loads(json.dumps(BASE_RUN))
    run["observation"]["turns"] = run["observation"]["turns"][:1]
    coverage = facets(ces_scoring.build_evaluation_payload(run, {}), "capability_coverage")
    assert coverage["driver_had_to_correct"] == "not_applicable"


def test_the_screen_renders_the_contexts_it_knows():
    payload = ces_scoring.build_evaluation_payload(BASE_RUN, {"ces1Effort": 5, "ces1Reason": "vì sao"})
    types = {c["contextType"] for c in payload["contexts"]}
    assert {"task_outcome", "conversation_summary", "user_feedback"} <= types
    assert facets(payload, "user_feedback")["feedback_reason"] == "vì sao"
    assert facets(payload, "conversation_summary")["conversation_path"]
    assert facets(payload, "conversation_summary")["process_notes"]
