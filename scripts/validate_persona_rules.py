#!/usr/bin/env python3
"""Refuse personas that describe someone who could not exist.

The sampler conditions each generated field on exactly one parent, so it will
happily produce a driver who commutes by bicycle, owns no car, drives 150-300km
a week, and has a built-in assistant they use. Every one of those was drawn from
a defensible distribution; together they are a person nobody could be.

These rules are the ones that can be stated without judgement -- each is a
contradiction by definition, not an improbability. A survey exists to capture
improbable people, so nothing merely unusual is failed here.

A rule only ever fires against a *generated* field. Where a measured value is
implicated the measured one is treated as the fact: two answers a person gave
cannot be repaired by a sampler, and a rule that silently rewrote them would
destroy the only evidence in the file.

    uv run python scripts/validate_persona_rules.py persona/datasets/vn-drivers
    uv run python scripts/validate_persona_rules.py <pool> --json-out report.json
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from persona_tiers import persona_paths  # noqa: E402

from matraix.persona_style_rules import (  # noqa: E402
    allowed_tones,
    style_conflict,
)

URBAN_CLASS_I = {
    "Ha Noi", "Ho Chi Minh City", "Da Nang", "Hai Phong", "Can Tho",
    "Hue", "Nha Trang", "Da Lat", "Vinh", "Quy Nhon", "Bien Hoa", "Vung Tau",
}

SHORT_DISTANCES = {"Under 50 km", "50-150 km"}


class Rule:
    def __init__(self, code: str, why: str, check: Callable[[dict], str | None]) -> None:
        self.code = code
        self.why = why
        self.check = check


def _r1(d: dict) -> str | None:
    """Owning no car is treated as having no car to be equipped or driven far.

    VALIDITY: two clauses survive. Owning no car and yet having a built-in
    assistant, or driving hundreds of kilometres a week, are contradictions of
    the rule's own claim. Describing the noise inside a car is not: people who
    borrow, rent or are lent a car answer that question, and the form asks it.

    A third clause used to fire on any answer to cabin_noise at all. It refused
    three real respondents -- bicycle commuters who own no car, drive under 50
    km a week and use a phone assistant -- every value of which is an answer
    someone gave. It survived only because cabin_noise was sampled in the
    42-persona pool; rebuilding from survey rows made it evidence and the rule
    failed against it. The docstring said "revisit when the sample grows"; the
    sample grew. Same correction as R6.

    DRIFT: while that clause stood, resampling under it moved cabin_noise by 17
    points of total variation, on top of 26 from the DAG change -- the largest
    shift of any field. Any cabin_noise distribution quoted from a pool written
    before this fix was reshaped by a rule that should not have fired.
    """
    if d.get("veh_class") != "Does not own":
        return None
    problems = []
    if d.get("veh_assistant_builtin") in {"Built in and used", "Built in but unused"}:
        problems.append("veh_assistant_builtin={}".format(d["veh_assistant_builtin"]))
    if d.get("drv_exposure") not in SHORT_DISTANCES and d.get("drv_exposure"):
        problems.append("drv_exposure={}".format(d["drv_exposure"]))
    return "owns no car but " + ", ".join(problems) if problems else None


# R2 stood here and is deliberately not coming back: "a bike commuter who
# drives occasionally cannot cover more than 150km a week". One of the 81
# respondents is exactly that person -- bikes to work every day, drives long
# trips at weekends. Commute mode says how someone gets to work, not how much
# they drive, and the two come apart for anyone who owns a car and does not
# commute in it. The rule had already resampled personas to satisfy a
# constraint that does not exist.


def _r3(d: dict) -> str | None:
    if d.get("att_self_driving_cars") != "Opposed":
        return None
    scope = str(d.get("vn_assistant_task_scope") or "")
    if "vehicle control" not in scope:
        return None
    return "opposed to self-driving yet vn_assistant_task_scope={!r}".format(scope)


def _r4(d: dict) -> str | None:
    if d.get("urbanicity") != "Rural":
        return None
    if d.get("vn_locality") not in URBAN_CLASS_I:
        return None
    return "urbanicity=Rural yet vn_locality={}".format(d["vn_locality"])


def _r5(d: dict) -> str | None:
    if d.get("english_proficiency") != "Native":
        return None
    if d.get("primary_language") and d["primary_language"] != "Vietnamese":
        return None
    if str(d.get("highest_education") or "") in {"Bachelor's", "Master's", "Doctorate"}:
        return None
    return "english_proficiency=Native with primary_language={} and education={}".format(
        d.get("primary_language"), d.get("highest_education"))


def _r6(d: dict) -> str | None:
    """Only the option that says they use no assistant at all constrains usage.

    The first version fired on any answer starting "None", which swept in
    "None, uses phone assistant" -- a person who plainly does use one, just not
    the car's. 22 of 81 real respondents answered exactly that, so the rule was
    wrong, not them, and it had already resampled sixteen personas to satisfy a
    constraint that does not exist.
    """
    if d.get("veh_assistant_builtin") != "None, uses no assistant":
        return None
    freq = d.get("assistant_usage_freq")
    if freq in {None, "", "Rarely", "Tried it and stopped"}:
        return None
    return "uses no assistant at all yet assistant_usage_freq={}".format(freq)


def _r7(d: dict) -> str | None:
    """Style axes drawn independently describing a speaker who cannot exist.

    The three fields are kept separate on purpose -- curt and formal is a real
    combination -- so only contradictions by definition are listed, in
    ``matraix.persona_style_rules``. None of the three is measured, so no
    respondent can falsify a pair; the table is kept narrow for that reason.
    """
    return style_conflict(d)


RULES = [
    Rule("R1", "no car, yet equipped and driving distance", _r1),
    # R2 removed -- see the block above _r3 for why.
    Rule("R3", "opposed to self-driving cannot delegate vehicle control", _r3),
    Rule("R4", "rural persona placed in a class-I city", _r4),
    Rule("R5", "native English without a reason to have it", _r5),
    Rule("R6", "no assistant present but reported usage", _r6),
    Rule("R7", "style axes contradict each other", _r7),
]


def violations(persona: dict[str, Any]) -> list[tuple[str, str]]:
    dims = persona.get("dimensions") or {}
    out = []
    for rule in RULES:
        detail = rule.check(dims)
        if detail:
            out.append((rule.code, detail))
    return out


#: For each rule, the generated fields that may be changed to satisfy it, and
#: the values each may take. Only generated fields appear here: a rule is never
#: allowed to rewrite a measured value, because two answers a person gave are
#: evidence, and a sampler that edits evidence to look tidy has destroyed the
#: only thing in the file worth having.
REPAIRS: dict[str, list[tuple[str, Callable[[dict], set[str] | None]]]] = {
    "R1": [
        ("veh_assistant_builtin", lambda d: {"None, uses phone assistant",
                                             "None, uses no assistant"}),
        ("drv_exposure", lambda d: set(SHORT_DISTANCES)),
    ],
    "R3": [("vn_assistant_task_scope", lambda d: {
        "None", "Navigation only", "Navigation and media", "Most non-driving tasks"})],
    "R4": [("vn_locality", lambda d: None)],
    "R5": [("english_proficiency", lambda d: {"None", "Basic", "Conversational", "Fluent"})],
    "R6": [("assistant_usage_freq", lambda d: {"Rarely", "Tried it and stopped"})],
    # One field moves, not three. tone_expected is a bare synthesis-graph draw;
    # cog_verbosity carries a forum word-count calibration and cog_formality
    # feeds the address register, so both are left alone. Blanking all three
    # would answer a contradiction by deleting the character.
    "R7": [("tone_expected", allowed_tones)],
}


def repair(
    persona: dict[str, Any],
    pool_values: dict[str, list[str]],
    *,
    rng,
) -> list[str]:
    """Resample the generated fields a violated rule implicates.

    Returns the rule codes it acted on. A field with no allowed value left is
    set to None rather than forced: an absent dimension is honest, an invented
    one is not.
    """
    dims = persona.get("dimensions") or {}
    grounding = persona.get("grounding") or {}
    acted = []
    for code, _ in violations(persona):
        for field, allowed_for in REPAIRS.get(code, []):
            if field not in dims:
                continue
            if (grounding.get(field) or {}).get("assignment_type") == "observed":
                continue
            allowed = allowed_for(dims)
            if allowed is None:
                dims[field] = None
                acted.append(code)
                continue
            options = [v for v in pool_values.get(field, []) if v in allowed]
            dims[field] = rng.choice(options) if options else None
            acted.append(code)
    return acted


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pool", type=Path)
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()

    paths = persona_paths(args.pool)
    if not paths:
        print("no persona_*.yaml under {}".format(args.pool))
        return 1

    per_rule: collections.Counter = collections.Counter()
    offenders: dict[str, list[tuple[str, str]]] = {}
    for path in paths:
        persona = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        found = violations(persona)
        if found:
            offenders[str(persona.get("persona_id") or path.stem)] = found
            for code, _ in found:
                per_rule[code] += 1

    print("{} personas checked, {} with at least one violation\n".format(
        len(paths), len(offenders)))
    print("{:<5}{:>7}  {}".format("rule", "hits", "meaning"))
    for rule in RULES:
        print("{:<5}{:>7}  {}".format(rule.code, per_rule[rule.code], rule.why))

    if offenders:
        print("\nper persona:")
        for pid in sorted(offenders):
            print("  {}".format(pid))
            for code, detail in offenders[pid]:
                print("     {}  {}".format(code, detail))

    if args.json_out:
        args.json_out.write_text(
            json.dumps(
                {
                    "checked": len(paths),
                    "violating": len(offenders),
                    "byRule": {r.code: per_rule[r.code] for r in RULES},
                    "personas": {k: [list(v) for v in vs] for k, vs in offenders.items()},
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print("\nwrote {}".format(args.json_out))
    return 1 if offenders else 0


if __name__ == "__main__":
    raise SystemExit(main())
