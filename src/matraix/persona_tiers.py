"""Which persona fields reach the model, and which only answer provenance.

``scripts/persona_tiers.py`` decides the tier when a pool is written. This
module is the other half: honouring that decision when a prompt is built. The
two were never connected, so every job rendered all 48 fields of a vn-driver
persona -- the 22 marked ``no_effect_on_assistant_output`` included -- and the
tiering existed only in the file.

The tier is read from the persona's own ``grounding`` rather than from
``PROMPT_FIELDS``. A record states what it is; the renderer does not need a
list of vn-driver field names to render a vn-driver persona, and a pool that
never tiered anything keeps rendering everything.

Field-name constants live here rather than in ``scripts/`` because both the
authoring script and the package need them, and the second copy is where the
drift starts -- the same lesson as ``matraix.persona_pool``.
"""

from __future__ import annotations

from typing import Any

PROMPT = "prompt"
GUARD = "guard"
ARCHIVE = "archive"

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

#: Prompt-tier fields whose conditioning parents are themselves generated, so
#: the value carries no measured signal about this respondent -- it is a draw
#: from the pool's marginal, dressed as a conditional.
#:
#: trip_mix is conditioned on urbanicity and vn_locality. Neither is asked: the
#: questionnaire has no province or city question, so vn_locality is generated
#: and urbanicity is derived from it. Adding one province question to the form
#: is the cheapest way to make this field real.
UNCONDITIONED = {
    "trip_mix": "parents (urbanicity, vn_locality) are generated; no province "
                "question in the survey",
}


#: Archive-tier fields that reach the prompt anyway, because they are not
#: claims about the character at all.
#:
#: primary_language is tiered archive on the right grounds -- knowing a driver
#: is Vietnamese does not change what the assistant should say back. But the
#: renderer turns it into "use your primary language for outputs", which is an
#: output contract, and filtering that on the character tier dropped the only
#: line telling the model which language to answer in.
OUTPUT_CONTRACT_FIELDS = ("primary_language",)


def tier_of(field_id: str) -> str:
    if field_id in PROMPT_FIELDS:
        return PROMPT
    if field_id in GUARD_FIELDS:
        return GUARD
    return ARCHIVE


def stamped_tiers(persona: dict[str, Any]) -> dict[str, str]:
    """Tier per dimension as the persona file states it, for tiered pools only.

    Empty when no grounding entry carries a tier, which is how an untiered pool
    is told apart from one whose every field happens to be archive.
    """
    grounding = persona.get("grounding")
    if not isinstance(grounding, dict):
        return {}
    tiers: dict[str, str] = {}
    for key, entry in grounding.items():
        if not isinstance(entry, dict):
            continue
        tier = entry.get("tier")
        if tier:
            tiers[str(key)] = str(tier)
    return tiers


def prompt_tier_dimensions(persona: dict[str, Any]) -> dict[str, Any]:
    """The dimensions a prompt may render.

    Falls back to every dimension when the pool stamped no tiers: an older pool
    losing its whole profile to a filter it never opted into would be a worse
    failure than rendering too much.
    """
    dimensions = persona.get("dimensions")
    if not isinstance(dimensions, dict):
        return {}
    tiers = stamped_tiers(persona)
    if not tiers:
        return dict(dimensions)
    return {
        key: value
        for key, value in dimensions.items()
        if tiers.get(key, ARCHIVE) == PROMPT or key in OUTPUT_CONTRACT_FIELDS
    }


def label_overrides(persona: dict[str, Any] | None = None) -> dict[str, str]:
    """Display-name overrides, with the persona's own view winning.

    A rendered view carries ``label_overrides``; a persona record does not, so
    the module-level table is the default for both.
    """
    merged = dict(LABEL_OVERRIDES)
    if persona:
        own = persona.get("label_overrides")
        if isinstance(own, dict):
            merged.update({str(k): str(v) for k, v in own.items()})
    return merged
