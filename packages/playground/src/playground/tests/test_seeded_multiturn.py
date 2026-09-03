"""A seeded trial must open on its dataset row, not on an invented need."""

from __future__ import annotations

import json
from pathlib import Path

from playground.types import Persona, PlaygroundConfig
from playground.user_sim.runner import run_playground
from playground.user_sim.seed import ChatSeed, resolve_chat_seed
from playground.user_sim.tool_client import FakeToolStepClient
from playground.user_sim.tools import ToolCall

SEED_ROW = {
    "row_id": "row-0120",
    "scenario": "Tôi đang lái xe một mình trên đường về sau buổi họp kéo dài.",
    "first_input": "Vita, tìm trạm sạc xe điện gần nhất.",
    "intent_code": "journey_navigation_places",
    "subintent_code": "destination_poi",
    "vehicle_state": "driving",
    "ASSISTANT_MODE": "quiet",
    "persona_id": "wiki-0252555c74ec",
}


class FakeSession:
    def __init__(self, turns):
        self._turns = list(turns)
        self.calls = []

    @property
    def session_id(self) -> str:
        return "sess-seeded"

    def run_turn_sync(self, message):
        self.calls.append(message)
        return self._turns.pop(0)


class RecordingSelfReportClient:
    """Captures the self-report prompt so we can assert what the rater saw."""

    def __init__(self):
        self.user_prompt = ""

    def complete_json(self, system, user):
        self.user_prompt = user
        return {
            "needConstraintSatisfaction": "yes",
            "personalPreferenceSatisfaction": "partially",
            "overallExperienceRating": 7,
            "reason": "turn 2 dẫn đường đúng chỗ.",
            "askedUsefulClarificationQuestions": True,
            "clarifyingNotes": "turn 1 hỏi lại vị trí.",
        }


def _run(monkeypatch, *, seed):
    report_client = RecordingSelfReportClient()
    monkeypatch.setattr(
        "playground.user_sim.runner.build_json_client",
        lambda *_a, **_k: report_client,
    )
    client = FakeToolStepClient(
        [
            [ToolCall("send_message", {"message": "Pin sắp cạn, chỗ sạc gần đây?"})],
            [ToolCall("end_conversation", {"reason": "satisfied"})],
        ]
    )
    monkeypatch.setattr(
        "playground.user_sim.runner.build_tool_step_client",
        lambda *_a, **_k: client,
    )
    session = FakeSession([{"assistantMessage": "Đã tìm thấy trạm sạc.", "recommendedItems": []}])
    result = run_playground(
        session,
        Persona(id="p1", name="Mai", summary="Tài xế", context="Name: Mai"),
        "Vita drive assistant",
        PlaygroundConfig(domain="automotive_ai", max_turns=3),
        created_at="2026-06-30T00:00:00Z",
        task_path="application/tasks/chat_vita-drive-assistant",
        repo_root=Path(__file__).resolve().parents[5],
        seed=seed,
    )
    return result, report_client


def test_seed_anchors_the_kickoff_prompt(monkeypatch):
    result, _ = _run(monkeypatch, seed=SEED_ROW)

    task_prompt = result.prompts["taskPrompt"]
    assert "Vita, tìm trạm sạc xe điện gần nhất." in task_prompt
    assert "sau buổi họp kéo dài" in task_prompt
    assert "Vehicle state: driving" in task_prompt
    # The persona must reword it rather than replay the row verbatim.
    assert "do not copy the sentence above verbatim" in task_prompt


def test_kickoff_reaches_the_simulator_system_prompt(monkeypatch):
    """Regression: the kickoff used to be recorded but never sent.

    ``prompt_bundle`` built a "## Application kickoff" block for the emitted
    ``prompts`` event while ``UserSimSession`` built its own system prompt
    without it, so asserting on ``result.prompts`` alone proves nothing about
    what the model actually saw. Assert on the messages the client received.
    """
    seen = {}

    class CapturingToolClient(FakeToolStepClient):
        def complete_with_tools(self, messages):
            seen.setdefault("system", messages[0]["content"])
            return super().complete_with_tools(messages)

    report_client = RecordingSelfReportClient()
    monkeypatch.setattr(
        "playground.user_sim.runner.build_json_client",
        lambda *_a, **_k: report_client,
    )
    client = CapturingToolClient(
        [
            [ToolCall("send_message", {"message": "Pin sắp cạn, chỗ sạc gần đây?"})],
            [ToolCall("end_conversation", {"reason": "satisfied"})],
        ]
    )
    monkeypatch.setattr(
        "playground.user_sim.runner.build_tool_step_client",
        lambda *_a, **_k: client,
    )
    run_playground(
        FakeSession([{"assistantMessage": "Đã tìm thấy.", "recommendedItems": []}]),
        Persona(id="p1", name="Mai", summary="Tài xế", context="Name: Mai"),
        "Vita drive assistant",
        PlaygroundConfig(domain="automotive_ai", max_turns=3),
        created_at="2026-06-30T00:00:00Z",
        task_path="application/tasks/chat_vita-drive-assistant",
        repo_root=Path(__file__).resolve().parents[5],
        seed=SEED_ROW,
    )

    assert "## Application kickoff" in seen["system"]
    assert SEED_ROW["first_input"] in seen["system"]


def test_unseeded_run_keeps_the_invent_your_own_goal_kickoff(monkeypatch):
    result, _ = _run(monkeypatch, seed=None)

    task_prompt = result.prompts["taskPrompt"]
    # The row's own wording must be absent; the task instruction still mentions
    # charging stations generally, so assert on the seed sentence itself.
    assert SEED_ROW["first_input"] not in task_prompt
    assert "sau buổi họp kéo dài" not in task_prompt
    assert "settles on a realistic need" in task_prompt


def test_self_report_sees_the_seeded_need_and_numbered_turns(monkeypatch):
    _, report_client = _run(monkeypatch, seed=SEED_ROW)

    prompt = report_client.user_prompt
    assert "What you came in wanting" in prompt
    assert "sau buổi họp kéo dài" in prompt
    # Turn numbering is what makes "cite turn N" a checkable instruction.
    assert "turn 1 | you:" in prompt
    assert 'Cite the turn number(s) it rests on, as "turn N"' in prompt


def test_unseeded_self_report_has_no_dangling_need_section(monkeypatch):
    _, report_client = _run(monkeypatch, seed=None)

    assert "What you came in wanting" not in report_client.user_prompt


def test_seed_resolution_prefers_job_config_over_env():
    from_env = json.dumps({"scenario": "env row", "first_input": "env input"})

    seed = resolve_chat_seed(SEED_ROW, environ={"MATRIX_CHATBOT_SEED": from_env})

    assert seed is not None
    assert seed.first_input == "Vita, tìm trạm sạc xe điện gần nhất."
    assert seed.assistant_mode == "quiet"


def test_seed_resolution_falls_back_to_env_when_kwargs_absent():
    from_env = json.dumps({"scenario": "env row", "first_input": "env input"})

    seed = resolve_chat_seed(None, environ={"MATRIX_CHATBOT_SEED": from_env})

    assert seed is not None
    assert seed.first_input == "env input"


def test_unusable_seed_never_takes_the_trial_down():
    assert resolve_chat_seed({"scenario": "", "first_input": ""}, environ={}) is None
    assert resolve_chat_seed("{not json", environ={}) is None
    assert resolve_chat_seed(12345, environ={}) is None


def test_seed_accepts_an_already_built_object():
    seed = resolve_chat_seed(ChatSeed(scenario="s", first_input="f"), environ={})

    assert seed is not None and seed.first_input == "f"
