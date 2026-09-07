import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[3]
        / "application/tasks/chat_vita-drive-multiturn-coverage/tests"
    ),
)

from multiturn_scoring import (  # noqa: E402
    build_evaluation_payload,
    content_words,
    lexical_topic_overlap,
)

TURNS = [
    {"turn_index": 0, "user_message": "Tìm quán cà phê gần đây giúp em", "assistant_message": "Dạ em tìm ngay ạ."},
    {"turn_index": 1, "user_message": "Chọn quán gần nhất nhé", "assistant_message": "Quán cà phê gần nhất cách 400 m ạ."},
]

CASE_RUN = {
    "case_id": "vm_0001",
    "case": {
        "case_id": "vm_0001",
        "subintent_code": "destination_poi",
        "parent_intent_code": "journey_navigation_places",
        "seed_quality": "ok",
        "reference_turn_count": 2,
    },
    "observation": {"turn_count": 2, "turns": TURNS},
}


def _facets(payload, context_type="multiturn_coverage"):
    return {
        f["key"]: f["value"]
        for c in payload["contexts"]
        if c["contextType"] == context_type
        for f in c["facets"]
    }


def test_content_words_keeps_short_vietnamese_nouns_but_drops_function_words():
    """Vietnamese is monosyllabic, so a length filter alone would gut the signal."""
    assert content_words("Tìm quán cà phê, ok?") == {"tìm", "quán", "cà", "phê"}
    assert content_words("Xe còn bao nhiêu pin?") == {"xe", "nhiêu", "pin"}


def test_content_words_drops_pure_function_word_sentences():
    assert content_words("dạ vâng ạ") == set()


def test_overlap_is_not_applicable_for_a_single_turn():
    assert lexical_topic_overlap(TURNS[:1]) == "not_applicable"
    assert lexical_topic_overlap([]) == "not_applicable"


def test_overlap_detected_when_a_later_reply_reuses_an_opening_word():
    assert lexical_topic_overlap(TURNS) == "carried"


def test_overlap_absent_when_later_replies_share_nothing():
    turns = [
        TURNS[0],
        {"turn_index": 1, "user_message": "ừ", "assistant_message": "Dạ vâng ạ."},
    ]
    assert lexical_topic_overlap(turns) == "not_carried"


def test_opening_message_without_content_words_is_not_applicable():
    turns = [
        {"turn_index": 0, "user_message": "ừ", "assistant_message": "Dạ."},
        {"turn_index": 1, "user_message": "ok", "assistant_message": "Dạ vâng ạ."},
    ]
    assert lexical_topic_overlap(turns) == "not_applicable"


def test_payload_reports_coverage_and_the_proxy():
    facets = _facets(build_evaluation_payload(CASE_RUN, None))
    assert facets["subintent_code"] == "destination_poi"
    assert facets["lexical_topic_overlap"] == "carried"
    assert facets["turn_count"] == 2
    assert facets["assistant_reply_count"] == 2


def test_payload_keeps_seed_quality_so_noise_is_separable_from_failure():
    case_run = {**CASE_RUN, "case": {**CASE_RUN["case"], "seed_quality": "too_short"}}
    assert _facets(build_evaluation_payload(case_run, None))["seed_quality"] == "too_short"


def test_payload_has_no_correctness_facet():
    facets = _facets(build_evaluation_payload(CASE_RUN, None))
    assert "decision_match" not in facets
