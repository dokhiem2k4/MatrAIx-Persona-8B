"""A persona profile is prose the model reads, so it follows the display rule.

Ids and values stay English wherever data is stored, filtered, stratified or
scored; only the rendered sentence is translated. These tests pin both halves
of that: the prose changes, the keys do not.
"""

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from matraix.persona_dimension_catalog import (  # noqa: E402
    build_dimension_narrative,
    collect_dimension_items,
    load_label_pack,
    resolve_label_locale,
)

PERSONA = REPO_ROOT / "persona/datasets/vn-drivers/persona_row-000.yaml"


@pytest.fixture
def dimensions():
    return yaml.safe_load(PERSONA.read_text(encoding="utf-8"))["dimensions"]


def test_english_is_what_you_get_without_asking(dimensions, monkeypatch):
    """No other task's prompt may change under this."""
    monkeypatch.delenv("MATRIX_PERSONA_LABEL_LOCALE", raising=False)
    text = "\n".join(build_dimension_narrative(dimensions))
    assert "### Identity" in text
    assert "Age bracket:" in text


def test_vietnamese_translates_headings_labels_and_values(dimensions):
    text = "\n".join(build_dimension_narrative(dimensions, locale="vi"))
    assert "### Nhân thân" in text          # heading
    assert "Nhóm tuổi:" in text             # label
    assert "Nông thôn" in text              # value (urbanicity: Rural)
    assert "### Identity" not in text
    assert "Age bracket:" not in text


def test_the_canonical_ids_never_change(dimensions):
    """Grouping, filtering and scoring all key off dim_id."""
    en = collect_dimension_items(dimensions, locale="")
    vi = collect_dimension_items(dimensions, locale="vi")
    ids = lambda grouped: sorted(  # noqa: E731
        dim_id for items in grouped.values() for dim_id, _label, _value in items
    )
    assert ids(en) == ids(vi)
    # Section keys stay English too: build_dimension_narrative branches on them.
    assert set(en) == set(vi)


def test_the_written_language_instruction_is_translated(dimensions):
    """A Vietnamese profile must not end on an English directive."""
    text = "\n".join(build_dimension_narrative(dimensions, locale="vi"))
    assert "Ngôn ngữ viết mặc định" in text
    assert "Default written language" not in text


def test_a_locale_with_no_pack_falls_back_to_english(dimensions):
    assert load_label_pack("xx") == {}
    text = "\n".join(build_dimension_narrative(dimensions, locale="xx"))
    assert "### Identity" in text


def test_the_env_var_selects_the_locale(monkeypatch):
    monkeypatch.setenv("MATRIX_PERSONA_LABEL_LOCALE", "vi")
    assert resolve_label_locale() == "vi"
    # An explicit argument still wins, so a caller can force English.
    assert resolve_label_locale("") == ""


def test_an_unmapped_value_stays_readable_rather_than_vanishing():
    """Half-translated beats blank: an unknown term keeps its English."""
    grouped = collect_dimension_items({"age_bracket": "Not a real bracket"}, locale="vi")
    values = [value for items in grouped.values() for _id, _label, value in items]
    assert values == ["Not a real bracket"]
