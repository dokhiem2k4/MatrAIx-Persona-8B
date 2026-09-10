"""Style axes that cannot both hold, and which field gives way when they clash.

cog_verbosity, cog_formality and tone_expected each control a different part of
an utterance -- how long it is, which register it uses, and how it opens -- so
they are kept as three fields rather than collapsed into one. Collapsing them
would lose a real distinction: a driver can be curt and formal at once.

What they cannot be is contradictory, and the sampler drew each of them from
its own distribution with nothing reconciling the three. The 42-persona pool
holds 38 distinct combinations, among them a driver who rambles past 35 words
while going straight to the point from the first word.

The bar here is the same as ``scripts/validate_persona_rules.py``: a pair is
listed only when it is a contradiction by definition. Very formal and playful
is unusual, not impossible, and a survey exists to capture unusual people.

None of these three fields is measured -- all three are sampled -- so no real
respondent can falsify a pair, and none of them is protected as evidence. That
cuts both ways: the rule cannot be checked against people, so it is kept narrow
and every entry carries the contradiction that justifies it.
"""

from __future__ import annotations

from typing import Any

#: ((field, value), (field, value), why). Order within a pair is display only.
INCOMPATIBLE_STYLE_PAIRS: tuple[
    tuple[tuple[str, str], tuple[str, str]], ...
] = (
    # Terse caps the utterance at six words; Detailed requires naming concrete
    # parameters. One of the two has to go unsaid.
    (("cog_verbosity", "Terse"), ("tone_expected", "Detailed")),
    # Rambling tells the situation before the request; Concise is defined as
    # arriving at the request in the first word.
    (("cog_verbosity", "Rambling"), ("tone_expected", "Concise")),
    # Slang and clipped forms against a register that keeps its distance.
    (("cog_formality", "Slangy"), ("tone_expected", "Formal")),
    # Very formal ends the sentence with a deferential particle; Blunt is
    # defined by dropping exactly those.
    (("cog_formality", "Very formal"), ("tone_expected", "Blunt")),
)

#: Which field to move first when a pair fires, least-evidenced first.
#:
#: tone_expected is a bare draw from the synthesis graph. cog_verbosity carries
#: a forum calibration behind it -- pool shares fitted to median words per post
#: on otofun.net.vn -- so moving it discards more than moving tone_expected
#: does. cog_formality sits between the two.
REPAIR_PREFERENCE: tuple[str, ...] = (
    "tone_expected",
    "cog_formality",
    "cog_verbosity",
)


def style_conflict(dimensions: dict[str, Any]) -> str | None:
    """The first contradiction among the style axes, or None.

    A field the persona does not carry never fires: an absent value is unknown,
    not permissive, and refusing a persona for a field it was never given would
    fail every pool but this one.
    """
    for (field_a, value_a), (field_b, value_b) in INCOMPATIBLE_STYLE_PAIRS:
        if dimensions.get(field_a) == value_a and dimensions.get(field_b) == value_b:
            return "{}={} with {}={}".format(field_a, value_a, field_b, value_b)
    return None


def conflicting_fields(dimensions: dict[str, Any]) -> tuple[str, ...]:
    """Fields implicated in the first conflict, in repair-preference order."""
    for (field_a, value_a), (field_b, value_b) in INCOMPATIBLE_STYLE_PAIRS:
        if dimensions.get(field_a) == value_a and dimensions.get(field_b) == value_b:
            involved = {field_a, field_b}
            return tuple(f for f in REPAIR_PREFERENCE if f in involved)
    return ()


#: Every value tone_expected may take, so a repair can name the complement of
#: the conflicting one rather than blanking the field.
TONE_VALUES: tuple[str, ...] = (
    "Concise",
    "Detailed",
    "Warm / empathetic",
    "Formal",
    "Playful",
    "Blunt",
)


def allowed_tones(dimensions: dict[str, Any]) -> set[str]:
    """Tones compatible with this persona's verbosity and formality.

    The repair moves one field, not three. tone_expected is the one that moves
    because it is a bare synthesis-graph draw, while cog_verbosity carries a
    forum word-count calibration and cog_formality feeds the address register.
    Blanking all three would answer a contradiction by deleting the character.
    """
    blocked = {
        tone
        for (field_a, value_a), (field_b, value_b) in INCOMPATIBLE_STYLE_PAIRS
        if field_b == "tone_expected"
        for tone in (value_b,)
        if dimensions.get(field_a) == value_a
    }
    return set(TONE_VALUES) - blocked
