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
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LABELS_VI = REPO_ROOT / "persona/schema/labels/dimensions.labels.vi.json"

#: Rendered into ``persona_profile`` in this order. Chosen from the ~24
#: dimensions a real respondent actually answered -- the rest of the 1,291 are
#: sampled from the synthesis graph and would dress a guess up as a fact.
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

COLUMNS = [
    "trial_id",
    "row_id",
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


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load_labels() -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """Vietnamese display names for dimensions and their enum values.

    The pack is a display-only overlay: canonical ids and values stay English
    everywhere data is stored or scored, so this script holds no Vietnamese
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

    A rating is only interpretable next to the person who gave it: "2/10" from
    someone with low patience and high skepticism is a different signal than
    the same 2 from a patient, trusting driver. Only dimensions the respondent
    actually answered are rendered -- a sampled value would read as a fact
    about a person when it is a draw from a graph.
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
        if not result or not transcript or not feedback:
            skipped.append(trial.name)
            continue
        seed = result.get("seed") or {}
        persona = read_json(trial / "persona_meta.json") or {}
        messages = transcript.get("messages") or []
        opening = next(
            (m.get("content", "") for m in messages if m.get("role") == "customer"), ""
        )
        row = {
            "trial_id": trial.name.rsplit("__", 1)[-1],
            "row_id": seed.get("rowId", ""),
            "intent_code": seed.get("intentCode", ""),
            "subintent_code": seed.get("subintentCode", ""),
            "subintent_name": seed.get("subintentName", ""),
            "persona_id": seed.get("sourcePersonaId", ""),
            "persona_name": persona.get("display_name", ""),
            "persona_profile": build_persona_profile(
                persona.get("persona_path"),
                labels=labels,
                values=values,
                cache=profile_cache,
            ),
            "vehicle_state": seed.get("vehicleState", ""),
            "assistant_mode": seed.get("assistantMode", ""),
            "scenario": seed.get("scenario", ""),
            "seed_first_input": seed.get("firstInput", ""),
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
    parser.add_argument("-o", "--out", type=Path, required=True, help="path without suffix")
    args = parser.parse_args()

    rows, skipped, records = collect(args.job)
    if not rows:
        raise SystemExit("no complete trials under {}".format(args.job))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = args.out.with_suffix(".csv")
    # utf-8-sig, not utf-8: the rows are Vietnamese, and Excel decodes a
    # BOM-less CSV with the machine's ANSI codepage -- "Tôi" arrives as
    # "TÃ´i". The BOM is how Excel is told the file is UTF-8.
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

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
