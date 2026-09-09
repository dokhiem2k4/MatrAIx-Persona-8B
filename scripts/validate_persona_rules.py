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
from pathlib import Path
from typing import Any, Callable

import yaml

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
    if d.get("veh_class") != "Does not own":
        return None
    problems = []
    if d.get("veh_assistant_builtin") in {"Built in and used", "Built in but unused"}:
        problems.append("veh_assistant_builtin={}".format(d["veh_assistant_builtin"]))
    if d.get("drv_exposure") not in SHORT_DISTANCES and d.get("drv_exposure"):
        problems.append("drv_exposure={}".format(d["drv_exposure"]))
    if d.get("cabin_noise"):
        problems.append("cabin_noise={}".format(d["cabin_noise"]))
    return "owns no car but " + ", ".join(problems) if problems else None


def _r2(d: dict) -> str | None:
    if d.get("lstyle_commute_mode") != "Bike":
        return None
    if d.get("demo_driver_status") != "Occasional driver":
        return None
    if d.get("drv_exposure") in SHORT_DISTANCES or not d.get("drv_exposure"):
        return None
    return "commutes by bike and drives occasionally, yet drv_exposure={}".format(
        d["drv_exposure"])


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
    builtin = str(d.get("veh_assistant_builtin") or "")
    if not builtin.startswith("None"):
        return None
    freq = d.get("assistant_usage_freq")
    if freq in {None, "", "Rarely", "Tried it and stopped"}:
        return None
    return "no built-in assistant yet assistant_usage_freq={}".format(freq)


RULES = [
    Rule("R1", "no car, yet equipped and driving distance", _r1),
    Rule("R2", "bike commuter driving occasionally cannot cover that distance", _r2),
    Rule("R3", "opposed to self-driving cannot delegate vehicle control", _r3),
    Rule("R4", "rural persona placed in a class-I city", _r4),
    Rule("R5", "native English without a reason to have it", _r5),
    Rule("R6", "no assistant present but reported usage", _r6),
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
        ("cabin_noise", lambda d: None),
    ],
    "R2": [("drv_exposure", lambda d: set(SHORT_DISTANCES))],
    "R3": [("vn_assistant_task_scope", lambda d: {
        "None", "Navigation only", "Navigation and media", "Most non-driving tasks"})],
    "R4": [("vn_locality", lambda d: None)],
    "R5": [("english_proficiency", lambda d: {"None", "Basic", "Conversational", "Fluent"})],
    "R6": [("assistant_usage_freq", lambda d: {"Rarely", "Tried it and stopped"})],
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

    paths = sorted(args.pool.glob("persona_*.yaml"))
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
