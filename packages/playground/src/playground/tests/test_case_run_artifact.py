from playground.case_binding import build_case_run_artifact
from playground.types import PlaygroundTurn

CASE = {"case_id": "vg_0137", "user_input": "Dẫn tôi đến đó", "input_constraint": "omit_detail"}

TURNS = [
    PlaygroundTurn(
        turn_index=0,
        user_message="Dẫn giúp em tới chỗ đó với",
        assistant_message="Em chưa rõ anh chị muốn đến đâu ạ.",
        structured_exposure=[{"key": "decision", "value": "clarify_or_offer"}],
    ),
    PlaygroundTurn(
        turn_index=1,
        user_message="Aeon Long Biên nhé",
        assistant_message="Dạ em dẫn đường ngay ạ.",
        structured_exposure=[{"key": "decision", "value": "execute"}],
    ),
]


def test_returns_none_without_a_case():
    assert build_case_run_artifact(None, TURNS) is None


def test_carries_the_whole_case():
    artifact = build_case_run_artifact(CASE, TURNS)
    assert artifact["case_id"] == "vg_0137"
    assert artifact["case"] == CASE


def test_observation_anchors_on_the_first_turn():
    observation = build_case_run_artifact(CASE, TURNS)["observation"]
    assert observation["first_user_message"] == "Dẫn giúp em tới chỗ đó với"
    assert observation["first_assistant_message"] == "Em chưa rõ anh chị muốn đến đâu ạ."
    assert observation["structured_exposure"] == [{"key": "decision", "value": "clarify_or_offer"}]
    assert observation["turn_count"] == 2


def test_empty_transcript_yields_empty_observation():
    observation = build_case_run_artifact(CASE, [])["observation"]
    assert observation["first_assistant_message"] == ""
    assert observation["structured_exposure"] == []
    assert observation["turn_count"] == 0


def test_observation_carries_every_turn_for_multi_turn_tasks():
    turns = build_case_run_artifact(CASE, TURNS)["observation"]["turns"]
    assert [t["turn_index"] for t in turns] == [0, 1]
    assert turns[1]["user_message"] == "Aeon Long Biên nhé"
    assert turns[1]["assistant_message"] == "Dạ em dẫn đường ngay ạ."


def test_turns_is_empty_for_an_empty_transcript():
    assert build_case_run_artifact(CASE, [])["observation"]["turns"] == []
