"""Turning prompt-tier fields into instructions the model can act on.

``- Formality: Very formal`` states a fact about the character and leaves the
model to infer what to do with it. The ablation measured the result: none of 21
fields moved the utterance further than re-running the identical prompt did.
Three of those fields -- formality, verbosity and expected tone -- were rendered
as independent labels in the same list, so "Very formal" and "Concise" and
"Balanced" arrived together with nothing to reconcile them.

A directive names the behaviour instead: how many words, which address words,
what changes on a retry. The text lives in a locale pack rather than here,
because canonical ids and values stay English everywhere data is stored or
scored and only the rendered text is localised.

This module holds no Vietnamese.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DIRECTIVE_PACK_PATH = (
    REPO_ROOT / "persona/schema/labels/speech_directives.vi.json"
)

#: Key inside a per-dimension block naming which rendered section it joins.
SECTION_KEY = "_section"

#: Order sections appear in the prompt: how they speak, what they will accept,
#: then the situation the request comes from. Speech first because it is the
#: only group that changes every single utterance.
SECTION_ORDER = ("speech", "stance", "situation")

#: A directive is written in the language the persona speaks -- "dài 7-12 chữ"
#: only means anything to a model producing Vietnamese. The pack is therefore
#: locale-scoped, and a persona from another pool gets no directives rather
#: than Vietnamese ones: the dev-sample pool speaks English, and handing Ethan
#: Brooks a Vietnamese address-register rule is worse than a bare label.
LANGUAGE_LOCALES = {"Vietnamese": "vi"}


@dataclass(frozen=True)
class SpeechDirectivePack:
    locale: str
    sections: dict[str, str]
    directives: dict[str, dict[str, str]]

    def section_of(self, dim_id: str) -> str:
        return self._raw_sections.get(dim_id, SECTION_ORDER[0])

    # Populated by load_speech_directives; kept off the public surface because
    # the section tag is an authoring detail of the pack, not of a persona.
    _raw_sections: dict[str, str] = None  # type: ignore[assignment]


def load_speech_directives(
    path: Path | str = DIRECTIVE_PACK_PATH,
) -> SpeechDirectivePack:
    """Read the directive pack, splitting the section tags out of each block."""
    raw: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    directives: dict[str, dict[str, str]] = {}
    sections_of: dict[str, str] = {}
    for dim_id, block in (raw.get("directives") or {}).items():
        if not isinstance(block, dict):
            continue
        sections_of[dim_id] = str(block.get(SECTION_KEY) or SECTION_ORDER[0])
        directives[dim_id] = {
            str(value): str(text)
            for value, text in block.items()
            if value != SECTION_KEY
        }
    pack = SpeechDirectivePack(
        locale=str(raw.get("locale") or ""),
        sections=dict(raw.get("sections") or {}),
        directives=directives,
    )
    object.__setattr__(pack, "_raw_sections", sections_of)
    return pack


def locale_for(dimensions: dict[str, Any]) -> str | None:
    """Directive locale a persona qualifies for, from the language it speaks."""
    return LANGUAGE_LOCALES.get(str(dimensions.get("primary_language") or ""))


def pack_for(
    dimensions: dict[str, Any],
    *,
    pack: SpeechDirectivePack | None = None,
) -> SpeechDirectivePack | None:
    """The directive pack this persona may use, or None if its language differs."""
    locale = locale_for(dimensions)
    if locale is None:
        return None
    pack = pack or load_speech_directives()
    return pack if pack.locale == locale else None


def build_directive_sections(
    dimensions: dict[str, Any],
    *,
    pack: SpeechDirectivePack | None = None,
) -> list[str]:
    """Markdown blocks of directives for the dimensions this persona holds.

    A dimension with no directive, or a value the pack does not cover, is
    skipped rather than guessed at: a wrong instruction is worse than none.
    Callers render the remaining fields as labels alongside these blocks.
    """
    pack = pack or load_speech_directives()
    grouped: dict[str, list[str]] = {name: [] for name in SECTION_ORDER}

    # Pack order, not persona order: the pack is authored most-decisive first
    # (who you address, then how long you talk, then register), while a persona
    # file's key order is an artefact of how it was sampled.
    for dim_id, entries in pack.directives.items():
        if dim_id not in dimensions:
            continue
        value = dimensions.get(dim_id)
        if value is None:
            continue
        text = entries.get(str(value))
        if not text:
            continue
        grouped.setdefault(pack.section_of(dim_id), []).append(text)

    blocks: list[str] = []
    for name in SECTION_ORDER:
        lines = grouped.get(name) or []
        if not lines:
            continue
        heading = pack.sections.get(name, name)
        blocks.append("\n".join([f"### {heading}"] + [f"- {line}" for line in lines]))
    return blocks


def covered_dimensions(
    pack: SpeechDirectivePack | None = None,
) -> frozenset[str]:
    """Dimension ids the pack renders as directives rather than labels."""
    pack = pack or load_speech_directives()
    return frozenset(pack.directives)
