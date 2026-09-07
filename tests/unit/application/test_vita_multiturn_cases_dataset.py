import collections
import json
from pathlib import Path

TASK_DIR = (
    Path(__file__).resolve().parents[3]
    / "application/tasks/chat_0709-vita-drive-multiturn-coverage"
)
CASES_PATH = TASK_DIR / "input/cases.jsonl"


def _cases():
    with CASES_PATH.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_one_seed_per_subintent():
    cases = _cases()
    assert len(cases) == 46
    assert len({case["subintent_code"] for case in cases}) == 46


def test_case_ids_are_unique():
    assert len({case["case_id"] for case in _cases()}) == 46


def test_no_reference_assistant_turn_is_shipped_to_the_persona():
    """The persona must never be able to read the sample answers."""
    raw = CASES_PATH.read_text(encoding="utf-8")
    assert "assistant" not in raw
    for case in _cases():
        assert "reference_turns" not in case
        assert "assistant_message" not in case


def test_seed_quality_flags_the_short_seeds():
    counts = collections.Counter(case["seed_quality"] for case in _cases())
    assert counts["too_short"] == 6
    assert counts["ok"] == 40


def test_short_seeds_are_kept_not_dropped():
    """Flagged seeds stay in the data; the recipe decides whether to run them."""
    short = [c for c in _cases() if c["seed_quality"] == "too_short"]
    assert all(c["seed_word_count"] < 4 for c in short)
    assert all(c["seed_user_turn"].strip() for c in short)


def test_reference_turn_count_is_present_for_every_seed():
    assert all(case["reference_turn_count"] >= 1 for case in _cases())


def test_review_sheet_lists_every_seed():
    review = (TASK_DIR / "seed_review.md").read_text(encoding="utf-8")
    for case in _cases():
        assert case["case_id"] in review


def test_identifiers_are_ascii():
    for case in _cases():
        for key in ("case_id", "subintent_code", "parent_intent_code", "seed_quality"):
            assert case[key].isascii(), (case["case_id"], key)
