"""Task-declared auth/session headers for the external_http chat transport."""

from __future__ import annotations

from playground.chatbot_task_config import ChatbotConnectionConfig


def _conn(**headers):
    return ChatbotConnectionConfig(headers=headers)


def test_env_placeholder_is_expanded():
    conn = _conn(**{"x-app-password": "${VITA_APP_PASSWORD}"})

    assert conn.resolve_headers({"VITA_APP_PASSWORD": "pw-from-env"}) == {
        "x-app-password": "pw-from-env"
    }


def test_unset_env_drops_the_header_instead_of_sending_the_placeholder():
    """Sending the literal ``${VAR}`` would read as a wrong password, not a
    missing one -- and the unauthenticated local sidecar wants no header."""
    conn = _conn(**{"x-app-password": "${VITA_APP_PASSWORD}"})

    assert conn.resolve_headers({}) == {}


def test_trial_id_placeholder_differs_per_trial():
    conn = _conn(**{"x-vehicle-session": "${TRIAL_ID}"})

    first = conn.resolve_headers({}, trial_id="chat_task__AAA")
    second = conn.resolve_headers({}, trial_id="chat_task__BBB")

    assert first == {"x-vehicle-session": "chat_task__AAA"}
    assert second == {"x-vehicle-session": "chat_task__BBB"}
    assert first != second


def test_mixed_placeholders_resolve_together():
    conn = _conn(
        **{
            "x-app-password": "${VITA_APP_PASSWORD}",
            "x-vehicle-session": "${TRIAL_ID}",
            "x-static": "literal",
        }
    )

    assert conn.resolve_headers(
        {"VITA_APP_PASSWORD": "pw"}, trial_id="t1"
    ) == {
        "x-app-password": "pw",
        "x-vehicle-session": "t1",
        "x-static": "literal",
    }


def test_no_headers_declared_stays_empty():
    assert ChatbotConnectionConfig().resolve_headers({}, trial_id="t1") == {}
