"""The self-report is read by Vietnamese reviewers; its prose must match."""

import yaml
from pathlib import Path

SCHEMAS = sorted(
    (Path(__file__).resolve().parents[3] / "application/tasks").glob(
        "chat_0709-*/input/self_report_schema.yaml"
    )
)


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_every_task_ships_a_schema():
    assert len(SCHEMAS) == 3


def test_free_text_is_required_in_vietnamese():
    """Without saying so, the persona model answers in whichever language it likes.

    A results table mixing Vietnamese and English cannot be filtered or compared.
    """
    for path in SCHEMAS:
        text = _load(path)["instructions"]
        assert "TIẾNG VIỆT" in text.upper(), path.parent.parent.name


def test_enum_values_stay_english_because_they_are_data():
    for path in SCHEMAS:
        for field in _load(path)["fields"]:
            for choice in field.get("choices") or ():
                assert str(choice).isascii(), (path.parent.parent.name, choice)


def test_keys_stay_english_identifiers():
    for path in SCHEMAS:
        for field in _load(path)["fields"]:
            assert field["key"].isascii()
            explanation = field.get("explanation")
            if explanation:
                assert explanation["key"].isascii()


def test_explanations_ask_for_a_specific_turn():
    """"Vita was bad" cannot be acted on; "at turn 1 Vita did X" can."""
    for path in SCHEMAS:
        prompts = [
            f["explanation"]["prompt"]
            for f in _load(path)["fields"]
            if f.get("explanation")
        ]
        assert any("lượt" in p for p in prompts), path.parent.parent.name
