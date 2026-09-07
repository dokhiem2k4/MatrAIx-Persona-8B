import collections
import json
from pathlib import Path

CASES_PATH = (
    Path(__file__).resolve().parents[3]
    / "application/tasks/chat_vita-drive-assistant-mode-ab/input/cases.jsonl"
)


def _cases():
    with CASES_PATH.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_row_count_matches_spec():
    assert len(_cases()) == 276


def test_case_ids_are_unique():
    assert len({case["case_id"] for case in _cases()}) == 276


def test_the_factorial_grid_is_perfectly_balanced():
    """Every mode x vehicle-state cell must hold the same 46 cases.

    Comparing cells is only valid without reweighting while this holds.
    """
    cells = collections.Counter(
        (case["state"]["assistant_mode"], case["state"]["vehicle_state"]) for case in _cases()
    )
    assert len(cells) == 6
    assert set(cells.values()) == {46}


def test_every_cell_covers_all_46_subintents():
    by_cell = collections.defaultdict(set)
    for case in _cases():
        key = (case["state"]["assistant_mode"], case["state"]["vehicle_state"])
        by_cell[key].add(case["subintent_code"])
    assert {len(codes) for codes in by_cell.values()} == {46}


def test_no_case_declares_an_input_constraint():
    assert {case["input_constraint"] for case in _cases()} == {"none"}


def test_provenance_is_uniformly_machine_generated():
    """If this ever stops holding, the report's disclaimer must change too."""
    assert {case["source"] for case in _cases()} == {"generated"}


def test_identifiers_are_ascii():
    for case in _cases():
        for key in ("case_id", "subintent_code", "parent_intent_code"):
            assert case[key].isascii(), (case["case_id"], key)
