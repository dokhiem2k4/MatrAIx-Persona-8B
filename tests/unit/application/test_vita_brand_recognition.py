"""What a first-time driver takes away about the assistant itself.

The guide asks this after showing a brand message and an avatar. Neither
exists here, so the basis is swapped for the conversation the persona just
had -- and the payload has to say so, or a reader will compare these numbers
straight to respondents who saw the poster.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
TASK = REPO_ROOT / "application/tasks/chat_0909-vita-brand-recognition"
sys.path.insert(0, str(TASK / "tests"))
sys.path.insert(0, str(REPO_ROOT))

import brand_scoring  # noqa: E402


@pytest.fixture(scope="module")
def cases():
    path = TASK / "input/cases.jsonl"
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def facets(payload, context_type):
    return {
        f["key"]: f["value"]
        for c in payload["contexts"]
        if c["contextType"] == context_type
        for f in c["facets"]
    }


RUN = {
    "case": {"case_id": "vb_ask_directly", "encounter_code": "ask_directly",
             "encounter_label_vi": "Hỏi thẳng", "scenario_vi": "Hãy hỏi thẳng Vita là gì."},
    "observation": {"turn_count": 2, "turns": [
        {"user_message": "Vita ơi em là gì?", "assistant_message": "Mình là trợ lý trên xe."},
    ]},
}


# ------------------------------------------------------------------ dataset

def test_every_encounter_carries_a_scenario_and_a_probe_intent(cases):
    assert len(cases) == 4
    for case in cases:
        assert case["scenario_vi"].strip(), case["case_id"]
        assert case["probe_intent"] in ("role", "positioning", "character")
        # These scenarios are not in the guide; the note must say so.
        assert case["source_note"].strip(), case["case_id"]


def test_the_three_guide_sections_are_all_probed(cases):
    assert {c["probe_intent"] for c in cases} == {"role", "positioning", "character"}


# ------------------------------------------------------------------ matching

def test_the_three_brand_axes_are_detected_from_a_driver_s_own_words():
    assert brand_scoring.axes_detected("nó nắm được ý mình") == ["hieu_y"]
    assert brand_scoring.axes_detected("gọn lẹ, làm được việc") == ["duoc_viec"]
    assert brand_scoring.axes_detected("lịch sự và tế nhị") == ["dung_muc"]
    assert brand_scoring.axes_detected("hiểu ý, được việc, đúng mực") == [
        "hieu_y", "duoc_viec", "dung_muc"
    ]


def test_matching_survives_missing_diacritics():
    """People type without tone marks; the measurement should not care."""
    assert brand_scoring.axes_detected("nam duoc y minh") == ["hieu_y"]


def test_words_outside_the_list_are_a_miss_not_a_failure():
    """A blank axis means "not detected"; the verbatim answer is kept alongside."""
    assert brand_scoring.axes_detected("cũng tàm tạm") == []
    payload = brand_scoring.build_evaluation_payload(
        RUN, {"assistantRole": "trợ lý", "threeWords": "tàm tạm, bình thường, ổn",
              "moreThanCarControl": "broader_daily_assistant"}
    )
    brand = facets(payload, "brand_recognition")
    assert brand["brand_axes_hit"] == 0
    assert brand["brand_axis_basis"] == "lexical_proxy"
    assert brand["role_stated"] == "trợ lý"  # kept so a reader can overrule


def test_three_words_split_on_whatever_punctuation_was_used():
    assert brand_scoring.three_words("Thông minh, đáng tin và tinh tế") == [
        "Thông minh", "đáng tin", "tinh tế"
    ]
    assert brand_scoring.three_words("nhanh/gọn/lịch sự") == ["nhanh", "gọn", "lịch sự"]
    assert brand_scoring.three_words("") == []


def test_more_than_three_words_are_trimmed_not_rejected():
    assert len(brand_scoring.three_words("a, b, c, d, e")) == 3


# ------------------------------------------------------------------ verdict

def test_seeing_only_a_car_control_assistant_falls_short_of_the_guide_s_bar():
    """"không chỉ là trợ lý điều khiển xe bằng giọng nói" is the stated criterion."""
    payload = brand_scoring.build_evaluation_payload(
        RUN, {"assistantRole": "chỉ bật tắt điều hoà", "threeWords": "nhanh, gọn, ổn",
              "moreThanCarControl": "car_control_only"}
    )
    outcome = facets(payload, "task_outcome")
    assert outcome["outcome_status"] == "partially_resolved"
    assert outcome["recognised_broader_role"] == "no"


def test_recognising_the_broader_role_with_two_axes_passes():
    payload = brand_scoring.build_evaluation_payload(
        RUN, {"assistantRole": "trợ lý hằng ngày", "assistantPromises": "hiểu ý mình, làm được việc",
              "threeWords": "hiểu ý, được việc, nhanh", "moreThanCarControl": "broader_daily_assistant"}
    )
    assert facets(payload, "task_outcome")["outcome_status"] == "resolved"


def test_a_driver_who_could_not_describe_it_at_all_fails():
    payload = brand_scoring.build_evaluation_payload(RUN, {"assistantRole": ""})
    assert facets(payload, "task_outcome")["outcome_status"] == "unresolved"


def test_the_payload_says_no_poster_was_shown():
    """Without this a reader compares these numbers to respondents who saw one."""
    payload = brand_scoring.build_evaluation_payload(RUN, {"assistantRole": "trợ lý"})
    assert facets(payload, "brand_recognition")["impression_basis"] == "conversation_only"


def test_the_screen_renders_the_contexts_it_knows():
    payload = brand_scoring.build_evaluation_payload(
        RUN, {"assistantRole": "trợ lý", "threeWordsReason": "vì lượt 2"}
    )
    types = {c["contextType"] for c in payload["contexts"]}
    assert {"task_outcome", "conversation_summary", "user_feedback"} <= types
    assert facets(payload, "user_feedback")["feedback_reason"] == "vì lượt 2"
    assert facets(payload, "conversation_summary")["process_notes"]


def test_the_scenario_reaches_the_persona(cases):
    """Same trap as the discovery task: a brief with no goal in it."""
    from playground.case_binding import build_case_brief

    for case in cases:
        assert case["scenario_vi"][:40] in build_case_brief(case), case["case_id"]
