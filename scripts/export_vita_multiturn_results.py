#!/usr/bin/env python3
"""Flatten a stage-2 job into one row per conversation.

A finished job leaves three JSON files per trial in its own directory. Reading
228 of those by hand is not analysis, so this joins each conversation to the
stimulus that produced it and the rating it earned, one row per trial.

Two outputs, because they answer different questions:
  <out>.csv   one row per conversation -- scores, grouped by intent/persona
  <out>.jsonl one object per conversation, transcript included -- read the talk

Usage:
    uv run python scripts/export_vita_multiturn_results.py jobs/vita-full-3p9i -o data/vita-results
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

# Shared with the stage-1 exporter: both workbooks describe the same people, so
# a reader comparing a stimulus to the rating it earned sees one profile line,
# not two that drifted apart.
from persona_profile import build_persona_profile, load_labels  # noqa: E402

COLUMNS = [
    "trial_id",
    "row_id",
    "case_id",
    "intent_code",
    "subintent_code",
    "subintent_name",
    "persona_id",
    "persona_name",
    "persona_profile",
    "vehicle_state",
    "assistant_mode",
    "scenario",
    "seed_first_input",
    "opening_message",
    "turn_count",
    "need_satisfaction",
    "need_notes",
    "preference_satisfaction",
    "preference_notes",
    "overall_rating",
    "rating_reason",
    "asked_clarification",
    "clarifying_notes",
]


def describe_persona(
    persona_path: str | None,
    labels: dict[str, str],
    values: dict[str, dict[str, str]],
    cache: dict[str, str],
) -> str:
    """The respondent's traits, or why they could not be read.

    A blank cell here is ambiguous: it could mean the persona has no traits, or
    that the file moved. Saying which keeps a reader from concluding the first
    when the truth is the second -- jobs run from another worktree store an
    absolute path into a persona pool this checkout may not have.
    """
    profile = build_persona_profile(
        persona_path, labels=labels, values=values, cache=cache
    )
    if profile:
        return profile
    if not persona_path:
        return "(trial ghi không có persona_path)"
    return "(không đọc được hồ sơ persona: {})".format(persona_path)


def stimulus_from_trial(trial: Path, result: dict[str, Any]) -> dict[str, Any]:
    """Normalise the stimulus, whichever mechanism produced it.

    Two mechanisms exist side by side after the branches merged: the pipeline's
    ``seed`` rides in application_result.json, while case-bound tasks write
    ``case_run.json``. A reader should not have to care which one a job used.
    """
    seed = result.get("seed") or {}
    if seed:
        return {
            "row_id": seed.get("rowId", ""),
            "case_id": "",
            "intent_code": seed.get("intentCode", ""),
            "subintent_code": seed.get("subintentCode", ""),
            "subintent_name": seed.get("subintentName", ""),
            "persona_id": seed.get("sourcePersonaId", ""),
            "vehicle_state": seed.get("vehicleState", ""),
            "assistant_mode": seed.get("assistantMode", ""),
            "scenario": seed.get("scenario", ""),
            "seed_first_input": seed.get("firstInput", ""),
        }
    run = read_json(trial / "artifacts" / "app" / "output" / "case_run.json") or {}
    case = run.get("case") or {}
    state = case.get("state") or {}
    return {
        "row_id": "",
        "case_id": case.get("case_id", ""),
        "intent_code": case.get("parent_intent_code", ""),
        "subintent_code": case.get("subintent_code", ""),
        "subintent_name": case.get("subintent_label_vi", ""),
        "persona_id": "",
        "vehicle_state": state.get("vehicle_state", "") or "",
        # The deployment's real personality axis; the workbook's dead
        # ASSISTANT_MODE column is not carried forward.
        "assistant_mode": state.get("assistant_profile_id", "") or "",
        "scenario": case.get("error_type", ""),
        "seed_first_input": case.get("user_input", ""),
    }


def verifier_facets(trial: Path) -> dict[str, Any]:
    """Flatten the verifier's facets so scoring lands beside the rating.

    Facet keys differ per task, so they become columns discovered from the data
    rather than a fixed list that would silently drop a new task's scores.
    """
    payload = read_json(trial / "verifier" / "structured_output.json") or {}
    facets: dict[str, Any] = {}
    for context in payload.get("contexts") or ():
        if not isinstance(context, dict):
            continue
        for facet in context.get("facets") or ():
            if isinstance(facet, dict) and facet.get("key"):
                facets[str(facet["key"])] = facet.get("value")
    return facets


STIMULI_COLUMNS = [
    "case_id",
    "intent_code",
    "subintent_code",
    "subintent_name",
    "scenario",
    "seed_input",
    "first_input",
    "input_constraint",
    "case_integrity",
    "expected_decision",
    "observed_decision",
    "vehicle_state",
    "assistant_profile_id",
    "source",
    "persona_id",
    "persona_name",
    "persona_profile",
    "model",
]


def stimuli_row(row: dict[str, Any]) -> dict[str, Any]:
    """One row per trial, seen from the stimulus side.

    ``seed_input`` is the dataset's own wording; ``first_input`` is what the
    persona actually said. Reading them side by side is the only way to judge
    whether a paraphrase stayed faithful -- and ``case_integrity`` says whether
    the harness thought so too.
    """
    return {
        "case_id": row.get("case_id", ""),
        "intent_code": row.get("intent_code", ""),
        "subintent_code": row.get("subintent_code", ""),
        "subintent_name": row.get("subintent_name", ""),
        "scenario": row.get("scenario", ""),
        "seed_input": row.get("seed_first_input", ""),
        "first_input": row.get("opening_message", ""),
        "input_constraint": row.get("input_constraint", ""),
        "case_integrity": row.get("case_integrity", ""),
        "expected_decision": row.get("expected_decision", ""),
        "observed_decision": row.get("observed_decision", ""),
        "vehicle_state": row.get("vehicle_state", ""),
        "assistant_profile_id": row.get("assistant_mode", ""),
        "source": "golden" if row.get("case_id") else "pipeline",
        "persona_id": row.get("persona_id", ""),
        "persona_name": row.get("persona_name", ""),
        "persona_profile": row.get("persona_profile", ""),
        "model": row.get("model", ""),
    }


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def collect(job_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    skipped: list[str] = []
    labels, values = load_labels()
    profile_cache: dict[str, str] = {}
    for trial in sorted(p for p in job_dir.iterdir() if p.is_dir()):
        out = trial / "artifacts" / "app" / "output"
        result = read_json(out / "application_result.json")
        transcript = read_json(out / "transcript.json")
        feedback = read_json(out / "user_feedback.json")
        # A trial that died mid-flight leaves partial artifacts. Counting it as
        # a zero would quietly drag every average down, so drop it and say so.
        # A case-bound task scores from the verifier, so it can legitimately
        # finish without user_feedback.json. Only the first two are required.
        if not result or not transcript:
            skipped.append(trial.name)
            continue
        feedback = feedback or {}
        stimulus = stimulus_from_trial(trial, result)
        persona = read_json(trial / "persona_meta.json") or {}
        messages = transcript.get("messages") or []
        opening = next(
            (m.get("content", "") for m in messages if m.get("role") == "customer"), ""
        )
        row = {
            "trial_id": trial.name.rsplit("__", 1)[-1],
            "row_id": stimulus["row_id"],
            "case_id": stimulus["case_id"],
            "intent_code": stimulus["intent_code"],
            "subintent_code": stimulus["subintent_code"],
            "subintent_name": stimulus["subintent_name"],
            "persona_id": stimulus["persona_id"] or persona.get("persona_id", ""),
            "persona_name": persona.get("display_name", ""),
            "persona_profile": describe_persona(
                persona.get("persona_path"), labels, values, profile_cache
            ),
            "vehicle_state": stimulus["vehicle_state"],
            "assistant_mode": stimulus["assistant_mode"],
            "scenario": stimulus["scenario"],
            "seed_first_input": stimulus["seed_first_input"],
            "opening_message": opening,
            "turn_count": result.get("turnCount", len(messages) // 2),
            "need_satisfaction": feedback.get("needConstraintSatisfaction", ""),
            "need_notes": feedback.get("needNotes", ""),
            "preference_satisfaction": feedback.get("personalPreferenceSatisfaction", ""),
            "preference_notes": feedback.get("preferenceNotes", ""),
            "overall_rating": feedback.get("overallExperienceRating", ""),
            "rating_reason": feedback.get("reason", ""),
            "asked_clarification": feedback.get("askedUsefulClarificationQuestions", ""),
            "clarifying_notes": feedback.get("clarifyingNotes", ""),
        }
        row.update(verifier_facets(trial))
        rows.append(row)
        records.append({**row, "messages": messages})
    return rows, skipped, records


def summarise(rows: list[dict[str, Any]]) -> None:
    ratings = [int(r["overall_rating"]) for r in rows if str(r["overall_rating"]).isdigit()]
    if not ratings:
        print("\nno numeric ratings found")
        return
    print("\nrating: n={} mean={:.2f} min={} max={}".format(
        len(ratings), mean(ratings), min(ratings), max(ratings)
    ))
    spread = Counter(ratings)
    print("  spread: " + "  ".join(
        "{}:{}".format(score, spread[score]) for score in sorted(spread)
    ))

    by_intent: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        if str(r["overall_rating"]).isdigit():
            by_intent[r["intent_code"]].append(int(r["overall_rating"]))
    print("\n{:34s} {:>3} {:>7}".format("intent", "n", "mean"))
    for code, scores in sorted(by_intent.items(), key=lambda kv: mean(kv[1])):
        print("{:34s} {:>3} {:>7.2f}".format(code, len(scores), mean(scores)))

    by_persona: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        if str(r["overall_rating"]).isdigit():
            by_persona[r["persona_name"] or r["persona_id"]].append(int(r["overall_rating"]))
    print("\n{:34s} {:>3} {:>7}".format("persona", "n", "mean"))
    for name, scores in sorted(by_persona.items(), key=lambda kv: mean(kv[1])):
        print("{:34s} {:>3} {:>7.2f}".format(name, len(scores), mean(scores)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-o", "--out", type=Path, help="path without suffix")
    group.add_argument(
        "--run-dir",
        help=(
            "run name; writes data/<name>/<name>-results.csv, -results.jsonl and "
            "-stimuli.csv. Refuses to overwrite an existing run."
        ),
    )
    args = parser.parse_args()

    if args.run_dir:
        # One folder per run, and never reuse one. A second run writing over the
        # first would destroy results that cost real money and cannot be
        # reproduced -- the assistant under test is not deterministic.
        run_dir = REPO_ROOT / "data" / args.run_dir
        if run_dir.exists():
            raise SystemExit(
                "run folder already exists: {} -- pick another name or move it "
                "aside; refusing to overwrite earlier results".format(run_dir)
            )
        run_dir.mkdir(parents=True)
        args.out = run_dir / "{}-results".format(args.run_dir)

    rows, skipped, records = collect(args.job)
    if not rows:
        raise SystemExit("no complete trials under {}".format(args.job))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = args.out.with_suffix(".csv")
    # utf-8-sig, not utf-8: the rows are Vietnamese, and Excel decodes a
    # BOM-less CSV with the machine's ANSI codepage -- "Tôi" arrives as
    # "TÃ´i". The BOM is how Excel is told the file is UTF-8.
    # Verifier facets differ per task, so append whatever the rows actually
    # carry. A fixed list would drop a new task's scores without a word, and
    # extrasaction="ignore" makes that silence total.
    extra = sorted({key for row in rows for key in row} - set(COLUMNS))
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=COLUMNS + extra, extrasaction="ignore", restval=""
        )
        writer.writeheader()
        writer.writerows(rows)

    stimuli_path = args.out.parent / (
        args.out.name.replace("-results", "") + "-stimuli.csv"
    )
    with stimuli_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=STIMULI_COLUMNS, extrasaction="ignore", restval=""
        )
        writer.writeheader()
        writer.writerows(stimuli_row(row) for row in rows)

    jsonl_path = args.out.with_suffix(".jsonl")
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("wrote {}  ({} conversations)".format(csv_path, len(rows)))
    print("wrote {}  (transcripts included)".format(jsonl_path))
    if skipped:
        print("\nSKIPPED {} incomplete trial(s): {}".format(
            len(skipped), ", ".join(skipped[:6]) + (" ..." if len(skipped) > 6 else "")
        ))
    summarise(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
