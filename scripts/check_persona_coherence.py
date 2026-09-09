#!/usr/bin/env python3
"""Find persona dimensions that a sampler drew in contradiction to measured fact.

A persona carries ~1,292 dimensions of which roughly 24 were answered by a real
respondent; the rest come from the synthesis graph. The graph samples each
``lifex_*`` field independently of the measured demographics, so it happily
produces a 25-34 year old who is married AND widowed, with two children AND an
empty nest. The prompt renders all of them as equally confident bullets, giving
the model no way to tell which fact to act on.

Provenance is the arbiter this needs: a value a person actually answered wins
over a value drawn from a distribution. Where the two collide, the drawn one is
removed rather than replaced -- we know it is wrong, we do not know what the
right value would be, and substituting a second guess re-creates the problem
one step further along.

Rules are deliberately conservative. Only pairs whose contradiction is a matter
of definition are listed; anything merely improbable stays untouched, because a
survey exists to capture improbable people.

    # report only (default)
    uv run python scripts/check_persona_coherence.py persona/datasets/vn-drivers

    # write a repaired copy, leaving the original pool untouched
    uv run python scripts/check_persona_coherence.py persona/datasets/vn-drivers \
        --fix --out persona/datasets/vn-drivers-coherent
"""

from __future__ import annotations

import argparse
import collections
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from persona_tiers import persona_paths  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

#: ``grounding`` assignment types meaning "a person answered this".
OBSERVED = {"observed", "direct", "forum_measured"}

HAS_CHILDREN = {"1 child", "2 children", "3+ children"}
IMPLIES_CHILDREN = {
    "Young children",
    "Teenagers",
    "Grown children",
    "Empty nester",
    "Raising grandchildren",
}
IMPLIES_ADULT_CHILDREN = {"Empty nester", "Raising grandchildren", "Grown children"}
YOUNG_BRACKETS = {"18-24", "25-34"}
IMPLIES_PARTNER_HISTORY = {"Remarried", "Married once", "Long-term partnership"}


class Rule:
    """One contradiction, phrased as: measured `anchor` refutes generated `drawn`."""

    def __init__(
        self,
        anchor: str,
        drawn: str,
        conflict: Callable[[Any, Any], bool],
        why: str,
    ) -> None:
        self.anchor = anchor
        self.drawn = drawn
        self.conflict = conflict
        self.why = why


RULES = [
    Rule("demo_marital_status", "lifex_relationship_history",
         lambda a, d: (a == "Married" and d == "Widowed")
                      or (a == "Single" and d in IMPLIES_PARTNER_HISTORY),
         "marital status a person reported refutes the drawn relationship history"),
    Rule("demo_children_count", "lifex_parenting_journey",
         lambda a, d: (a == "None" and d in IMPLIES_CHILDREN)
                      or (a in HAS_CHILDREN and d == "No children"),
         "child count a person reported refutes the drawn parenting stage"),
    Rule("age_bracket", "lifex_parenting_journey",
         lambda a, d: a in YOUNG_BRACKETS and d in IMPLIES_ADULT_CHILDREN,
         "age a person reported cannot reach the drawn parenting stage"),
    Rule("demo_children_count", "life_stage",
         lambda a, d: a == "None" and d == "Parent of young kids",
         "child count a person reported refutes the drawn life stage"),
]


#: Pairs where both sides are measured, so neither can overrule the other.
#: These are reported and never repaired: a contradiction between two answers
#: the same person gave is a fact about the instrument, not a bad draw, and
#: silently picking a winner would hide the thing worth fixing. Found because a
#: reviewer noticed a daily driver whose main transport was a bicycle.
MEASURED_CONFLICTS = [
    (
        "demo_driver_status",
        "lstyle_commute_mode",
        lambda a, d: a == "Daily driver" and d in {"Bike", "Walk", "Public transit"},
        "drives daily yet names a non-car mode as their main daily transport",
    ),
]


def provenance(grounding: dict[str, Any], key: str) -> str:
    entry = grounding.get(key)
    if not isinstance(entry, dict):
        return "unknown"
    return str(entry.get("assignment_type") or "unknown")


def findings_for(persona: dict[str, Any]) -> list[tuple[Rule, Any, Any]]:
    """Conflicts where the anchor is measured and the drawn value is not."""
    dims = persona.get("dimensions") or {}
    grounding = persona.get("grounding") or {}
    out = []
    for rule in RULES:
        if rule.anchor not in dims or rule.drawn not in dims:
            continue
        # Only a measured anchor may overrule; two sampled values have no
        # arbiter, and picking one would just be a third guess.
        if provenance(grounding, rule.anchor) not in OBSERVED:
            continue
        if provenance(grounding, rule.drawn) in OBSERVED:
            continue
        anchor_value, drawn_value = dims[rule.anchor], dims[rule.drawn]
        if rule.conflict(anchor_value, drawn_value):
            out.append((rule, anchor_value, drawn_value))
    return out


def repair(persona: dict[str, Any], findings: list[tuple[Rule, Any, Any]]) -> None:
    """Drop each refuted value and leave an audit trail in ``grounding``."""
    dims = persona["dimensions"]
    grounding = persona.setdefault("grounding", {})
    for rule, anchor_value, drawn_value in findings:
        dims.pop(rule.drawn, None)
        grounding[rule.drawn] = {
            "assignment_type": "removed_incoherent",
            "removed_value": drawn_value,
            "refuted_by": rule.anchor,
            "refuted_by_value": anchor_value,
            "reason": rule.why,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pool", type=Path, help="directory of persona_*.yaml")
    parser.add_argument("--fix", action="store_true", help="write repaired personas")
    parser.add_argument("--out", type=Path, help="destination pool for --fix")
    args = parser.parse_args()

    files = persona_paths(args.pool)
    if not files:
        print("no persona_*.yaml under {}".format(args.pool))
        return 1
    if args.fix and not args.out:
        print("--fix needs --out; refusing to overwrite the pool in place")
        return 2

    tally: collections.Counter = collections.Counter()
    affected = 0
    repaired_docs: list[tuple[Path, dict[str, Any]]] = []

    measured_clashes: list[tuple[str, str, Any, str, Any, str]] = []
    for path in files:
        persona = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        dims_now = persona.get("dimensions") or {}
        ground_now = persona.get("grounding") or {}
        for left, right, clash, why in MEASURED_CONFLICTS:
            if provenance(ground_now, left) not in OBSERVED:
                continue
            if provenance(ground_now, right) not in OBSERVED:
                continue
            if clash(dims_now.get(left), dims_now.get(right)):
                measured_clashes.append(
                    (path.stem, left, dims_now.get(left), right, dims_now.get(right), why)
                )
        findings = findings_for(persona)
        if findings:
            affected += 1
            print("{}".format(path.stem.replace("persona_", "")))
            for rule, anchor_value, drawn_value in findings:
                print("   {} = {!r} (measured)  vs  {} = {!r} (generated)".format(
                    rule.anchor, anchor_value, rule.drawn, drawn_value))
                tally["{} vs {}".format(rule.anchor, rule.drawn)] += 1
        if args.fix:
            repair(persona, findings)
            repaired_docs.append((path, persona))

    if measured_clashes:
        print("\nBOTH SIDES MEASURED -- reported, not repaired ({} personas):".format(
            len(measured_clashes)))
        tallied: collections.Counter = collections.Counter()
        for _, left, left_value, right, right_value, why in measured_clashes:
            tallied["{} = {!r}  vs  {} = {!r}   ({})".format(
                left, left_value, right, right_value, why)] += 1
        for line, count in tallied.most_common():
            print("   {:3d}  {}".format(count, line))
        print("   Neither value can overrule the other. Fix the questionnaire, not the pool.")

    print("\n{}/{} personas carry at least one contradiction".format(affected, len(files)))
    for name, count in tally.most_common():
        print("   {:4d}  {}".format(count, name))

    if args.fix:
        args.out.mkdir(parents=True, exist_ok=True)
        # Non-persona files (manifest, measurements) are part of the pool's
        # identity; a repaired pool that lost them would not load.
        for extra in args.pool.iterdir():
            if extra.is_file() and not extra.name.startswith("persona_"):
                shutil.copy2(extra, args.out / extra.name)
        for path, persona in repaired_docs:
            (args.out / path.name).write_text(
                yaml.safe_dump(persona, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
        print("\nwrote {} personas to {}".format(len(repaired_docs), args.out))
        print("removed values are kept in grounding as assignment_type=removed_incoherent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
