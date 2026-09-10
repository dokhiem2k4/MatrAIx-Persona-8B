#!/usr/bin/env python3
"""Find field pairs a persona holds that no real respondent ever held.

``validate_persona_rules.py`` checks six contradictions someone wrote down.
That catches what a person thought to look for; vn-drv-001 shipped with an
enthusiasm for the car assistant it was simultaneously opposed to, a "rarely
used" assistant it delegated everything to, and neither has a rule.

This asks the 81 respondents instead. For every pair of fields the survey
measures, it builds the joint they actually produced, then reports the
combinations a persona holds that the joint has never seen.

Absence at n=81 is weak evidence and is treated as such. A combination is only
reported when independence predicts we should have seen it: with
``expected = n * p(a) * p(b)`` at or above ``--min-expected`` (default 3), a
Poisson model puts the chance of observing none below 5%. Rarer absences are
counted and not listed -- at this sample size they are silence, not evidence.

Nothing here is a rule. A flag says "no respondent did this and enough of them
could have"; whether that is a contradiction or an unusual person is a judgement
someone has to make, and the whole point of a survey is to contain unusual
people. Promote a flag to ``validate_persona_rules.py`` only when the pair is a
contradiction by definition.

    uv run python scripts/audit_persona_conflicts.py \\
        --pool persona/datasets/vn-drivers-rows --responses <export.csv>
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "persona/curation/existing_data/scripts"))

import yaml  # noqa: E402

from crosswalks.vn_drivers import CROSSWALK, screen_rows  # noqa: E402

from matraix.persona_pool import persona_paths  # noqa: E402

#: A pair is only judged when both fields were answered by at least this many
#: respondents. Below it the joint is too thin to say anything about anything.
MIN_SUPPORT = 40

#: Expected count under independence at or above which a zero is worth saying
#: out loud. P(0 | Poisson(3)) is about 5%.
MIN_EXPECTED = 3.0


def respondent_table(path: Path) -> list[dict[str, Any]]:
    import csv

    rows = screen_rows(list(csv.DictReader(path.open(encoding="utf-8-sig"))))
    table = []
    for row in rows:
        values: dict[str, Any] = {}
        for dim_id, spec in CROSSWALK.items():
            try:
                value = spec["compute"](row)
            except Exception:
                value = None
            if value is not None:
                values[dim_id] = value
        table.append(values)
    return table


def joint_support(
    table: list[dict[str, Any]], field_a: str, field_b: str
) -> tuple[collections.Counter, collections.Counter, collections.Counter, int]:
    """Observed pair counts and the two marginals, over rows answering both."""
    pairs: collections.Counter = collections.Counter()
    left: collections.Counter = collections.Counter()
    right: collections.Counter = collections.Counter()
    n = 0
    for row in table:
        a, b = row.get(field_a), row.get(field_b)
        if a is None or b is None:
            continue
        pairs[(a, b)] += 1
        left[a] += 1
        right[b] += 1
        n += 1
    return pairs, left, right, n


def audit(
    pool: Path,
    table: list[dict[str, Any]],
    *,
    min_support: int = MIN_SUPPORT,
    min_expected: float = MIN_EXPECTED,
) -> tuple[list[dict], dict]:
    fields = sorted(
        f for f in CROSSWALK
        if sum(1 for r in table if r.get(f) is not None) >= min_support
    )

    joints = {}
    for field_a, field_b in itertools.combinations(fields, 2):
        pairs, left, right, n = joint_support(table, field_a, field_b)
        if n >= min_support:
            joints[(field_a, field_b)] = (pairs, left, right, n)

    findings: list[dict] = []
    quiet = 0
    for path in persona_paths(pool):
        persona = yaml.safe_load(path.read_text(encoding="utf-8"))
        dims = persona.get("dimensions") or {}
        grounding = persona.get("grounding") or {}
        for (field_a, field_b), (pairs, left, right, n) in joints.items():
            a, b = dims.get(field_a), dims.get(field_b)
            if a is None or b is None or (a, b) in pairs:
                continue
            if a not in left or b not in right:
                # A value no respondent gave: the audit has nothing to say.
                continue
            expected = n * (left[a] / n) * (right[b] / n)
            if expected < min_expected:
                quiet += 1
                continue
            findings.append(
                {
                    "persona_id": persona.get("persona_id"),
                    "pair": [field_a, field_b],
                    "values": [a, b],
                    "expected": round(expected, 1),
                    "observed": 0,
                    "support": n,
                    "assignment": [
                        (grounding.get(field_a) or {}).get("assignment_type"),
                        (grounding.get(field_b) or {}).get("assignment_type"),
                    ],
                }
            )

    findings.sort(key=lambda f: -f["expected"])
    return findings, {
        "fields_judged": len(fields),
        "pairs_judged": len(joints),
        "below_min_expected": quiet,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--responses", type=Path, required=True)
    ap.add_argument("--min-support", type=int, default=MIN_SUPPORT)
    ap.add_argument("--min-expected", type=float, default=MIN_EXPECTED)
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()

    table = respondent_table(args.responses)
    findings, stats = audit(
        args.pool,
        table,
        min_support=args.min_support,
        min_expected=args.min_expected,
    )

    print(
        f"{len(table)} respondents | {stats['fields_judged']} fields | "
        f"{stats['pairs_judged']} pairs judged"
    )
    print(
        f"{stats['below_min_expected']} absences too rare to judge at n="
        f"{len(table)} (expected < {args.min_expected})\n"
    )

    by_pair: collections.Counter = collections.Counter()
    for f in findings:
        by_pair[tuple(f["pair"])] += 1

    print(f"{len(findings)} flagged combination(s), by pair:")
    for (field_a, field_b), count in by_pair.most_common():
        sample = next(f for f in findings if f["pair"] == [field_a, field_b])
        print(
            f"  {count:3d}x  {field_a} + {field_b}\n"
            f"        e.g. {sample['values'][0]!r} + {sample['values'][1]!r}  "
            f"(expected {sample['expected']}, observed 0 of {sample['support']}; "
            f"assignment {sample['assignment'][0]}/{sample['assignment'][1]})"
        )

    personas = {f["persona_id"] for f in findings}
    print(f"\n{len(personas)} persona(s) hold at least one flagged combination.")
    print(
        "A flag is not a verdict: it says no respondent did this and enough of\n"
        "them could have. Promote one to validate_persona_rules.py only when it\n"
        "is a contradiction by definition."
    )

    if args.json_out:
        args.json_out.write_text(
            json.dumps({"stats": stats, "findings": findings},
                       ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
