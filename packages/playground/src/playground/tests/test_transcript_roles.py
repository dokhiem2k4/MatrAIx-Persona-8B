"""Chat transcripts must survive the round trip into the debrief view."""

from __future__ import annotations

from playground.harbor.playground import _build_turns_from_messages


def _messages(user_role: str, assistant_role: str):
    return {
        "sessionId": "s1",
        "messages": [
            {"role": user_role, "content": "Vita, tìm trạm sạc gần nhất."},
            {"role": assistant_role, "content": "Đã tìm thấy trạm sạc."},
            {"role": user_role, "content": "Dẫn đường đi."},
            {"role": assistant_role, "content": "Đang dẫn đường."},
        ],
    }


def test_customer_support_roles_build_turns():
    """``chat_eval`` writes customer/support; the debrief used to read only
    user/assistant and silently rendered every chat trial as zero turns."""
    turns = _build_turns_from_messages(_messages("customer", "support"))

    assert len(turns) == 2
    assert turns[0]["userMessage"] == "Vita, tìm trạm sạc gần nhất."
    assert turns[0]["assistantMessage"] == "Đã tìm thấy trạm sạc."


def test_user_assistant_roles_still_build_turns():
    turns = _build_turns_from_messages(_messages("user", "assistant"))

    assert len(turns) == 2
    assert turns[1]["userMessage"] == "Dẫn đường đi."


def test_roles_are_matched_case_insensitively():
    turns = _build_turns_from_messages(_messages("Customer", "SUPPORT"))

    assert len(turns) == 2


def test_unknown_roles_produce_no_turns():
    turns = _build_turns_from_messages(_messages("narrator", "chorus"))

    assert turns == []


def test_assistant_without_a_preceding_user_message_is_skipped():
    turns = _build_turns_from_messages(
        {"messages": [{"role": "support", "content": "Xin chào"}]}
    )

    assert turns == []
