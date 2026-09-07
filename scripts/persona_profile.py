#!/usr/bin/env python3
"""Render one persona record as a single readable line.

Both halves of the Vita pipeline need this line, for the same reason. A
stimulus is only interpretable next to the person who wrote it, and a rating is
only interpretable next to the person who gave it: "2/10" from someone with low
patience and high skepticism is a different signal than the same 2 from a
patient, trusting driver. Stage-1 and stage-2 exporters used to disagree about
whether that context belonged in the file at all -- the results workbook
carried it, the stimulus workbook did not -- so it now lives in one place and
both import it.

Import, do not run:
    from persona_profile import build_persona_profile, load_labels
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LABELS_VI = REPO_ROOT / "persona/schema/labels/dimensions.labels.vi.json"

#: Rendered into the profile line in this order. Chosen from the ~24 dimensions
#: a real respondent actually answered -- the rest of the 1,291 are sampled from
#: the synthesis graph and would dress a guess up as a fact.
#: Ordered who-they-are, how-they-drive, how-they-judge, what-they-think-of-cars,
#: because the last two groups are what move a rating.
PROFILE_KEYS = (
    "age_bracket",
    "gender_identity",
    "urbanicity",
    "highest_education",
    "demo_employment_status",
    "socioeconomic_band",
    "demo_marital_status",
    "demo_children_count",
    "demo_driver_status",
    "skill_driving",
    "lstyle_commute_mode",
    "cog_patience",
    "cog_skepticism",
    "trust_level",
    "att_electric_vehicles",
    "att_self_driving_cars",
    "topic_cars",
)

#: ``grounding`` assignment types that mean "a person answered this".
OBSERVED = {"observed", "direct", "forum_measured"}

FIELD_SEPARATOR = " · "
LABEL_SEPARATOR = ": "


def load_labels() -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """Vietnamese display names for dimensions and their enum values.

    The pack is a display-only overlay: canonical ids and values stay English
    everywhere data is stored or scored, so this module holds no Vietnamese
    text of its own.
    """
    if not LABELS_VI.is_file():
        return {}, {}
    pack = json.loads(LABELS_VI.read_text(encoding="utf-8")).get("dimensions", {})
    labels = {k: v["label"] for k, v in pack.items() if v.get("label")}
    values = {k: (v.get("values") or {}) for k, v in pack.items()}
    return labels, values


def build_persona_profile(
    persona_path: str | None,
    *,
    labels: dict[str, str],
    values: dict[str, dict[str, str]],
    cache: dict[str, str],
) -> str:
    """One readable line describing who this respondent is.

    Only dimensions the respondent actually answered are rendered -- a sampled
    value would read as a fact about a person when it is a draw from a graph.
    """
    if not persona_path:
        return ""
    if persona_path in cache:
        return cache[persona_path]

    path = Path(persona_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    try:
        persona = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except OSError:
        cache[persona_path] = ""
        return ""

    grounding = persona.get("grounding") or {}
    dimensions = persona.get("dimensions") or {}
    parts: list[str] = []
    for key in PROFILE_KEYS:
        if (grounding.get(key) or {}).get("assignment_type") not in OBSERVED:
            continue
        label = labels.get(key)
        raw = dimensions.get(key)
        if not label or raw in (None, ""):
            continue
        # Ranges like "18-24" carry no translation and need none; falling back
        # to the canonical value beats dropping the field.
        parts.append(label + LABEL_SEPARATOR + values.get(key, {}).get(str(raw), str(raw)))

    profile = FIELD_SEPARATOR.join(parts)
    cache[persona_path] = profile
    return profile
