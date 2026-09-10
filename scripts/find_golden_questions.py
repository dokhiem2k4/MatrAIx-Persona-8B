#!/usr/bin/env python3
"""Which questions carry the pool, and how much of it the sampler throws away.

Two readings, from the same 81 screened respondents.

**Coverage.** The crosswalk turns a survey row into dimension values, and it
covers most of the prompt tier. Every one of those values is a joint: one
person answered all of them, so the combination is real by construction and no
conditioning is needed to keep it coherent. The pipeline currently draws each
2026 field from a conditional distribution instead, because the Google Forms
export carries no respondent id to attach a row to a persona -- but nothing
stops a persona from *being* a row.

**Golden questions.** Market segmentation's standard answer to "we cannot ask
forty questions": cluster on everything, then find the smallest set of
questions that reproduces the assignment, using a discriminant model. The same
method applies here with the targets already named -- for each prompt-tier
field, which other answers predict it, and how few are enough.

The typing tool is a cell-majority classifier scored leave-one-out: pick the
questions selected so far, look at respondents who answered them the same way,
take the majority value, and back off to the global majority when the cell is
empty. It is the shape the industry ships in a spreadsheet, and at n=81 a
heavier model would fit noise.

    uv run python scripts/find_golden_questions.py --responses <export.csv>
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "persona/curation/existing_data/scripts"))

from crosswalks.vn_drivers import CROSSWALK, screen_rows  # noqa: E402

from matraix.persona_tiers import PROMPT_FIELDS  # noqa: E402

#: How many questions a typing tool may use before it stops being one.
MAX_GOLDEN = 4


def read_rows(path: Path) -> list[dict[str, Any]]:
    return list(csv.DictReader(path.open(encoding="utf-8-sig")))


def screened(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The driver screen, owned by the crosswalk that reads these answers."""
    return screen_rows(rows)


def to_dimensions(row: dict[str, Any]) -> dict[str, Any]:
    """One respondent as dimension values, via the same crosswalk the pool uses."""
    out: dict[str, Any] = {}
    for dim_id, spec in CROSSWALK.items():
        try:
            value = spec["compute"](row)
        except Exception:  # a malformed answer is a missing answer, not a crash
            value = None
        if value is not None:
            out[dim_id] = value
    return out


def cell_majority_loo(
    table: list[dict[str, Any]], predictors: tuple[str, ...], target: str
) -> float:
    """Leave-one-out accuracy of a cell-majority typing tool."""
    usable = [r for r in table if r.get(target) is not None]
    if not usable:
        return 0.0
    correct = 0
    for index, held_out in enumerate(usable):
        rest = usable[:index] + usable[index + 1 :]
        key = tuple(held_out.get(p) for p in predictors)
        cell = [r[target] for r in rest if tuple(r.get(p) for p in predictors) == key]
        pool = cell or [r[target] for r in rest]
        if not pool:
            continue
        if collections.Counter(pool).most_common(1)[0][0] == held_out[target]:
            correct += 1
    return correct / len(usable)


def baseline(table: list[dict[str, Any]], target: str) -> float:
    """Accuracy of always answering the pool's most common value."""
    values = [r[target] for r in table if r.get(target) is not None]
    if not values:
        return 0.0
    return collections.Counter(values).most_common(1)[0][1] / len(values)


def greedy_golden(
    table: list[dict[str, Any]],
    target: str,
    candidates: list[str],
    *,
    max_questions: int = MAX_GOLDEN,
) -> list[tuple[str, float]]:
    """Forward-select the questions that most improve the typing tool."""
    chosen: list[str] = []
    trail: list[tuple[str, float]] = []
    best = baseline(table, target)
    for _ in range(max_questions):
        scored = [
            (cell_majority_loo(table, tuple(chosen + [c]), target), c)
            for c in candidates
            if c not in chosen and c != target
        ]
        if not scored:
            break
        score, field = max(scored)
        if score <= best + 1e-9:
            break
        chosen.append(field)
        trail.append((field, score))
        best = score
    return trail


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--responses", type=Path, required=True)
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--max-questions", type=int, default=MAX_GOLDEN)
    args = ap.parse_args()

    rows = screened(read_rows(args.responses))
    table = [to_dimensions(r) for r in rows]
    print(f"{len(rows)} screened respondents\n")

    prompt_fields = [f for f in PROMPT_FIELDS]
    measured = [f for f in prompt_fields if any(r.get(f) is not None for r in table)]
    coverage = {
        f: sum(1 for r in table if r.get(f) is not None) for f in measured
    }

    print("COVERAGE -- prompt-tier fields the survey measures directly")
    print(f"  {len(measured)} of {len(prompt_fields)} prompt-tier fields\n")
    for field in sorted(coverage, key=lambda f: -coverage[f]):
        print(f"  {field:28s} {coverage[field]:3d}/{len(table)} respondents")
    unmeasured = [f for f in prompt_fields if f not in measured]
    print(f"\n  not asked ({len(unmeasured)}): {', '.join(unmeasured)}")

    complete = sum(1 for r in table if all(r.get(f) is not None for f in measured))
    print(
        f"\n  respondents answering ALL {len(measured)} measured fields: "
        f"{complete}/{len(table)}"
    )
    print(
        "  Each such respondent is a coherent joint over those fields -- a\n"
        "  persona that needs no conditioning to be a person who could exist."
    )

    print("\n\nGOLDEN QUESTIONS -- fewest answers that predict each field")
    print(f"{'target':28s} {'base':>6s} {'tool':>6s} {'gain':>6s}  questions")
    results = {}
    for target in sorted(measured):
        base_acc = baseline(table, target)
        trail = greedy_golden(
            table, target, measured, max_questions=args.max_questions
        )
        best = trail[-1][1] if trail else base_acc
        results[target] = {
            "baseline": base_acc,
            "typing_tool": best,
            "questions": [f for f, _ in trail],
        }
        picks = " > ".join(f for f, _ in trail) or "(none beat the baseline)"
        print(
            f"{target:28s} {base_acc:6.0%} {best:6.0%} {best - base_acc:+6.0%}  {picks}"
        )

    votes: collections.Counter = collections.Counter()
    for r in results.values():
        for rank, field in enumerate(r["questions"]):
            votes[field] += len(r["questions"]) - rank
    print("\nquestions carrying the most information about the rest:")
    for field, weight in votes.most_common(8):
        print(f"  {weight:3d}  {field}")

    if args.json_out:
        args.json_out.write_text(
            json.dumps(
                {
                    "respondents": len(table),
                    "coverage": coverage,
                    "unmeasured_prompt_fields": unmeasured,
                    "complete_respondents": complete,
                    "golden_questions": results,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
