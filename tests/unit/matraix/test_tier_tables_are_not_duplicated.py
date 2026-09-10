"""The tier tables live in the package; the scripts re-export, never copy.

``matraix.persona_pool`` exists because a second copy of the "is this a
persona file" predicate drifted from the first. Adding the render-time tier
filter reintroduced exactly that shape: ``src/matraix/persona_tiers.py`` and
``scripts/persona_tiers.py`` each declared PROMPT_FIELDS, GUARD_FIELDS,
ARCHIVE_REASONS and LABEL_OVERRIDES. They agreed on the day they were written,
which is the only day a duplicate ever does.

Identity, not equality: two lists that happen to match today pass an equality
check and still drift tomorrow.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("scripts").resolve()))

import persona_tiers as script_module  # noqa: E402

from matraix import persona_tiers as package_module  # noqa: E402


@pytest.mark.parametrize(
    "name",
    [
        "PROMPT_FIELDS",
        "GUARD_FIELDS",
        "ARCHIVE_REASONS",
        "LABEL_OVERRIDES",
        "UNCONDITIONED",
        "NO_EFFECT",
        "CONSEQUENCE",
        "LOW_CONFIDENCE",
        "DUPLICATE",
    ],
)
def test_script_reexports_the_package_table(name):
    assert getattr(script_module, name) is getattr(package_module, name), (
        f"{name} is a copy, not a re-export"
    )


def test_tier_of_is_the_package_function():
    assert script_module.tier_of is package_module.tier_of


def test_the_script_file_declares_no_table_of_its_own():
    source = Path("scripts/persona_tiers.py").read_text(encoding="utf-8")
    for name in ("PROMPT_FIELDS = (", "GUARD_FIELDS = (", "ARCHIVE_REASONS = {"):
        assert name not in source, f"{name.split()[0]} is declared, not imported"
