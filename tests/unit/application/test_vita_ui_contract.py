"""The debrief screen renders contexts by name and ignores the rest.

Emitting only a task-specific context left that panel showing one raw FAIL
string while every computed facet sat unread in the file. These names are a
contract with the frontend, so they get a test.
"""

import sys
from pathlib import Path

TASKS = Path(__file__).resolve().parents[3] / "application/tasks"
for slug in (
    "chat_0709-vita-drive-golden-error-recovery",
    "chat_0709-vita-drive-singleturn-mode-ab",
    "chat_0709-vita-drive-multiturn-coverage",
):
    sys.path.insert(0, str(TASKS / slug / "tests"))

import case_scoring  # noqa: E402
import mode_ab_scoring  # noqa: E402
import multiturn_scoring  # noqa: E402

# ChatTrialDebrief.tsx reads exactly these three, by name.
RENDERED_CONTEXTS = {"task_outcome", "conversation_summary", "user_feedback"}

FEEDBACK = {"overallExperienceRating": 6, "reason": "vì sao", "clarifyingNotes": "ghi chú"}

GOLDEN_RUN = {
    "case_id": "vg_1",
    "case": {"case_id": "vg_1", "case_type": "happy", "group": "g", "error_type": "happy_case",
             "subintent_code": "climate", "input_constraint": "none", "user_input": "x",
             "expected": {"decision": "execute", "tool_calls": []}},
    "observation": {"first_user_message": "a", "first_assistant_message": "b",
                    "structured_exposure": [{"key": "turnStatus", "value": "completed"}],
                    "turn_count": 1, "turns": []},
}
MODE_RUN = {
    "case_id": "vd_1",
    "case": {"case_id": "vd_1", "subintent_code": "climate", "parent_intent_code": "p",
             "state": {"vehicle_state": "driving", "assistant_profile_id": "normal"}, "source": "generated"},
    "observation": {"first_user_message": "a", "first_assistant_message": "b",
                    "structured_exposure": [{"key": "assistantProfileId", "value": "normal"}],
                    "turn_count": 1, "turns": []},
}
MULTI_RUN = {
    "case_id": "vm_1",
    "case": {"case_id": "vm_1", "subintent_code": "s", "parent_intent_code": "p",
             "seed_quality": "ok", "reference_turn_count": 2},
    "observation": {"turn_count": 2, "turns": [
        {"user_message": "tìm quán cà phê", "assistant_message": "dạ"},
        {"user_message": "gần nhất", "assistant_message": "quán cà phê gần nhất"}]},
}


def _types(payload):
    return {c["contextType"] for c in payload["contexts"]}


def _facets(payload, ctype):
    return {
        f["key"]: f["value"]
        for c in payload["contexts"] if c["contextType"] == ctype for f in c["facets"]
    }


def test_every_task_emits_the_contexts_the_screen_renders():
    for module, run in (
        (case_scoring, GOLDEN_RUN),
        (mode_ab_scoring, MODE_RUN),
        (multiturn_scoring, MULTI_RUN),
    ):
        payload = module.build_evaluation_payload(run, FEEDBACK)
        missing = RENDERED_CONTEXTS - _types(payload)
        assert not missing, (module.__name__, missing)


def test_task_outcome_carries_the_keys_the_screen_reads():
    for module, run in (
        (case_scoring, GOLDEN_RUN),
        (mode_ab_scoring, MODE_RUN),
        (multiturn_scoring, MULTI_RUN),
    ):
        f = _facets(module.build_evaluation_payload(run, FEEDBACK), "task_outcome")
        assert {"outcome_status", "outcome_reason", "resolution_basis"} <= set(f), module.__name__
        assert f["outcome_reason"], module.__name__


def test_feedback_reason_uses_the_key_the_screen_looks_up():
    """It reads feedback_reason; anything else renders as 'no explanation'."""
    for module, run in (
        (case_scoring, GOLDEN_RUN),
        (mode_ab_scoring, MODE_RUN),
        (multiturn_scoring, MULTI_RUN),
    ):
        f = _facets(module.build_evaluation_payload(run, FEEDBACK), "user_feedback")
        assert f.get("feedback_reason") == "vì sao", module.__name__


def test_conversation_summary_is_not_empty():
    for module, run in (
        (case_scoring, GOLDEN_RUN),
        (mode_ab_scoring, MODE_RUN),
        (multiturn_scoring, MULTI_RUN),
    ):
        f = _facets(module.build_evaluation_payload(run, FEEDBACK), "conversation_summary")
        assert f["conversation_path"], module.__name__
        assert f["process_notes"], module.__name__
