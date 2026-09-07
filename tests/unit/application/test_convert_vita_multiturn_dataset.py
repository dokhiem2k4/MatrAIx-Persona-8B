import pytest

from application.scripts.convert_vita_multiturn_dataset import (
    MIN_SEED_WORDS,
    MultiturnConversionError,
    build_conversation_record,
    group_conversations,
)

ROWS = [
    {"Parent_intent": "journey_navigation_places", "sub_intent": "destination_poi",
     "turn_index": 1, "role": "user", "content": "tìm quán cà phê gần đây giúp tôi"},
    {"Parent_intent": "journey_navigation_places", "sub_intent": "destination_poi",
     "turn_index": 1, "role": "assistant", "content": "Dạ em tìm ngay ạ."},
    {"Parent_intent": "journey_navigation_places", "sub_intent": "destination_poi",
     "turn_index": 2, "role": "user", "content": "chọn quán gần nhất nhé"},
    {"Parent_intent": "journey_navigation_places", "sub_intent": "destination_poi",
     "turn_index": 2, "role": "assistant", "content": "Dạ rồi ạ."},
]


def test_group_conversations_keys_by_subintent():
    grouped = group_conversations(ROWS)
    assert list(grouped) == [("journey_navigation_places", "destination_poi")]


def test_record_uses_only_the_first_user_turn_as_the_seed():
    record = build_conversation_record(("journey_navigation_places", "destination_poi"), ROWS, 0)
    assert record["seed_user_turn"] == "tìm quán cà phê gần đây giúp tôi"


def test_record_never_ships_the_reference_assistant_turns():
    """The persona must not be able to read the answers it is meant to elicit."""
    record = build_conversation_record(("journey_navigation_places", "destination_poi"), ROWS, 0)
    serialised = repr(record)
    assert "Dạ em tìm ngay" not in serialised
    assert "assistant" not in serialised


def test_record_keeps_the_reference_turn_count_as_a_hint_only():
    record = build_conversation_record(("journey_navigation_places", "destination_poi"), ROWS, 0)
    assert record["reference_turn_count"] == 2


def test_case_id_is_zero_padded():
    record = build_conversation_record(("journey_navigation_places", "destination_poi"), ROWS, 45)
    assert record["case_id"] == "vm_0046"


def test_taxonomy_parent_is_cross_checked():
    rows = [{**r, "Parent_intent": "my_car"} for r in ROWS]
    with pytest.raises(MultiturnConversionError):
        build_conversation_record(("my_car", "destination_poi"), rows, 0)


def test_unknown_subintent_code_raises():
    rows = [{**r, "sub_intent": "not_a_real_code"} for r in ROWS]
    with pytest.raises(MultiturnConversionError):
        build_conversation_record(("journey_navigation_places", "not_a_real_code"), rows, 0)


def test_missing_first_user_turn_raises():
    rows = [r for r in ROWS if not (r["role"] == "user" and r["turn_index"] == 1)]
    with pytest.raises(MultiturnConversionError):
        build_conversation_record(("journey_navigation_places", "destination_poi"), rows, 0)


def test_short_seed_is_flagged_not_dropped():
    """A bad seed stays visible in the data; the recipe decides whether to run it."""
    rows = [{**r, "content": "gì"} if r["role"] == "user" and r["turn_index"] == 1 else r for r in ROWS]
    record = build_conversation_record(("journey_navigation_places", "destination_poi"), rows, 0)
    assert record["seed_word_count"] == 1
    assert record["seed_quality"] == "too_short"


def test_long_enough_seed_is_marked_ok():
    record = build_conversation_record(("journey_navigation_places", "destination_poi"), ROWS, 0)
    assert record["seed_word_count"] >= MIN_SEED_WORDS
    assert record["seed_quality"] == "ok"
