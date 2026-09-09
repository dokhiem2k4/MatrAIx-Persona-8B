#!/usr/bin/env python3
"""Tier assignment and grounding bookkeeping shared by the persona scripts.

Two jobs that kept being done wrong in separate places, so they live here once.

``recompute_grounding_summary`` exists because ``grounding_summary`` was written
when a persona still held 1,297 dimensions and no later step updated it. Both
sampled files claimed ``generated: 1268`` while actually holding twenty-two,
which makes the one field that says how much of a persona is evidence unusable.
Any script that adds or removes a dimension must call this before writing.

``TIERS`` splits the fields by what they are for, rather than deleting any:

  prompt   changes what the assistant would say back, so it is rendered
  guard    never rendered, but the validator uses it to check the prompt tier
           is internally possible -- age and gender constrain the address
           register, locality constrains the accent, and so on
  archive  kept for provenance only: no effect on the assistant's output, or a
           consequence of another field rather than a cause, or not trustworthy

Nothing is dropped from a persona file. A field that leaves the prompt is still
there to answer "where did this come from".
"""

from __future__ import annotations

import collections
from typing import Any

#: Answers the assistant actually differ on. Grouped the way the brief reasons
#: about them: how the driver speaks, what they will accept, the situation the
#: request comes from, and how long they persist before giving up.
PROMPT_FIELDS = (
    # how they speak
    "vn_address_register",
    "tone_expected",
    "cog_verbosity",
    "cog_formality",
    "accent_region",
    # what content is acceptable
    "att_self_driving_cars",
    "att_electric_vehicles",
    "vn_assistant_task_scope",
    "cog_skepticism",
    "tech_savviness",
    # the situation the request comes from
    "demo_driver_status",
    "skill_driving",
    "trip_mix",
    "cabin_context",
    "vn_usual_companion",
    # thresholds
    "cog_patience",
    "vn_retry_tolerance",
    # Not in the original seventeen. Kept because 54% of surveyed drivers said
    # they are uncomfortable speaking aloud with a passenger present, which
    # decides whether a message may be read out at all. vn_usual_companion says
    # who is there; this says what the driver does about it.
    "vn_voice_privacy_comfort",
)

#: Never rendered. The validator reads these to decide whether the prompt tier
#: describes a person who could exist.
GUARD_FIELDS = (
    "age_bracket",
    "gender_identity",
    "vn_locality",
    "urbanicity",
    "lstyle_commute_mode",
    "veh_class",
    "veh_assistant_builtin",
    "assistant_usage_freq",
)

#: Why a field is neither rendered nor used as a constraint.
NO_EFFECT = "no_effect_on_assistant_output"
CONSEQUENCE = "consequence_not_cause"
LOW_CONFIDENCE = "low_confidence"
DUPLICATE = "duplicates_another_field"

ARCHIVE_REASONS = {
    "cult_vietnam": NO_EFFECT,
    "demo_children_count": NO_EFFECT,
    "demo_citizenship_status": NO_EFFECT,
    "demo_employment_status": NO_EFFECT,
    "demo_marital_status": NO_EFFECT,
    "demo_religion_affiliation": NO_EFFECT,
    "domain": NO_EFFECT,
    "english_proficiency": NO_EFFECT,
    "highest_education": NO_EFFECT,
    "lang_vietnamese": NO_EFFECT,
    "life_stage": NO_EFFECT,
    "primary_language": NO_EFFECT,
    "region": NO_EFFECT,
    "religiosity": NO_EFFECT,
    "safety_sensitivity": NO_EFFECT,
    "socioeconomic_band": NO_EFFECT,
    "topic_cars": DUPLICATE,
    "trust_level": DUPLICATE,
    "att_voice_assistant": LOW_CONFIDENCE,
    "drv_exposure": CONSEQUENCE,
    "need_state": CONSEQUENCE,
    "cabin_noise": CONSEQUENCE,
}

#: Two fields whose Vietnamese labels both read as "trust". They measure
#: different things -- one is how much a person trusts strangers, the other how
#: much they doubt a claim -- and rendering both invites an incoherent
#: character. Renamed at display time only; the ids stay put.
LABEL_OVERRIDES = {
    "trust_level": "Tin tưởng người lạ (WVS)",
    "cog_skepticism": "Nghi ngờ thông tin",
}

OBSERVED_TYPES = {"observed", "direct", "forum_measured"}


def tier_of(field_id: str) -> str:
    if field_id in PROMPT_FIELDS:
        return "prompt"
    if field_id in GUARD_FIELDS:
        return "guard"
    return "archive"


def recompute_grounding_summary(persona: dict[str, Any]) -> dict[str, Any]:
    """Rewrite grounding_summary from the persona's own fields.

    The invariant the acceptance criteria ask for: the assignment-type counts
    add up to the number of dimensions actually present.
    """
    dims = persona.get("dimensions") or {}
    grounding = persona.get("grounding") or {}
    by_type: collections.Counter = collections.Counter()
    sources: set[str] = set()
    for key in dims:
        entry = grounding.get(key)
        if not isinstance(entry, dict):
            by_type["unknown"] += 1
            continue
        by_type[str(entry.get("assignment_type") or "unknown")] += 1
        ref = entry.get("source_ref")
        if ref:
            sources.add(str(ref))
    summary = {
        "scoreable": sum(by_type[t] for t in OBSERVED_TYPES),
        "byAssignmentType": dict(sorted(by_type.items())),
        "sources": sorted(sources),
        "dimensionCount": len(dims),
    }
    persona["grounding_summary"] = summary
    return summary


def apply_tiers(persona: dict[str, Any]) -> dict[str, int]:
    """Stamp every grounding entry with its tier; return the tier counts."""
    dims = persona.get("dimensions") or {}
    grounding = persona.setdefault("grounding", {})
    counts: collections.Counter = collections.Counter()
    for key in dims:
        entry = grounding.get(key)
        if not isinstance(entry, dict):
            entry = {"assignment_type": "unknown"}
            grounding[key] = entry
        tier = tier_of(key)
        entry["tier"] = tier
        if tier == "archive":
            entry["excluded_reason"] = ARCHIVE_REASONS.get(key, NO_EFFECT)
        else:
            entry.pop("excluded_reason", None)
        counts[tier] += 1
    return dict(counts)


def prompt_view(persona: dict[str, Any]) -> dict[str, Any]:
    """The tier-A subset, ready to render.

    A separate file rather than a filter at render time: whoever writes the
    prompt should not have to know the tier rules, and a view on disk can be
    diffed when an utterance comes out wrong.
    """
    dims = persona.get("dimensions") or {}
    grounding = persona.get("grounding") or {}
    kept = {k: dims[k] for k in PROMPT_FIELDS if k in dims and dims[k] is not None}
    return {
        "persona_id": persona.get("persona_id"),
        "display_name": persona.get("display_name"),
        "tier": "prompt",
        "dimensions": kept,
        "grounding": {
            k: {
                "assignment_type": (grounding.get(k) or {}).get("assignment_type"),
                "confidence": (grounding.get(k) or {}).get("confidence"),
            }
            for k in kept
        },
        "label_overrides": {k: v for k, v in LABEL_OVERRIDES.items() if k in kept},
    }
