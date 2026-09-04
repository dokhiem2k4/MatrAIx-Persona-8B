#!/usr/bin/env python3
"""Turn a finished survey job into one dataset: a row per persona, per question.

Harbor scatters a run across one directory per trial, each holding the persona
it used, the answers it produced and its own token accounting. That shape is
right for a job runner and wrong for reading results, so this gathers a job
into a single document keyed by question, with the respondent attached.

Answers are joined back to the questionnaire, so a stored value like "weekly"
appears next to the question it answered and the label a human would read.
An answer whose value is not in the question's choice list is kept and flagged
rather than dropped -- a model inventing an option is a finding about the run,
not noise to hide.

Each respondent carries the persona provenance with them: how many of their
dimensions were measured and from which source. Without it a reader cannot
tell that these respondents are 24 measured answers wrapped in ~1,267
generated ones.

Usage:
    uv run python scripts/export_survey_dataset.py jobs/vn-drv-full-experience
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LABELS_VI = REPO_ROOT / "persona/schema/labels/dimensions.labels.vi.json"

#: Persona fields worth carrying into a survey row.
RESPONDENT_KEYS = (
    "age_bracket", "gender_identity", "vn_locality", "region",
    "domain", "life_stage",
)

SCOREABLE = {"observed", "direct", "forum_measured"}


def load_labels() -> tuple[dict, dict]:
    if not LABELS_VI.is_file():
        return {}, {}
    pack = json.loads(LABELS_VI.read_text(encoding="utf-8")).get("dimensions", {})
    return (
        {k: v.get("label") for k, v in pack.items() if v.get("label")},
        {k: (v.get("values") or {}) for k, v in pack.items()},
    )


def load_questionnaire(task_path: Path) -> dict:
    path = task_path / "input" / "questionnaire.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def choice_label(question: dict, value):
    """Return (human label or list of labels, in_range).

    A multi_choice answer is a list of option ids, so it is resolved
    element-wise; comparing the whole list against single ids marks every
    valid multi-select answer as out of range.
    """
    choices = question.get("choices") or question.get("options") or []
    if not choices:
        lo, hi = question.get("min"), question.get("max")
        if isinstance(value, (int, float)) and lo is not None and hi is not None:
            return None, lo <= value <= hi
        return None, True

    def one(v):
        for c in choices:
            if isinstance(c, dict) and str(c.get("id")) == str(v):
                return c.get("label") or c.get("text"), True
            if not isinstance(c, dict) and str(c) == str(v):
                return str(c), True
        return None, False

    if isinstance(value, (list, tuple)):
        labels, oks = zip(*(one(v) for v in value)) if value else ((), ())
        return list(labels), all(oks)
    return one(value)


def collect(job_dir: Path) -> dict:
    trials = sorted(p for p in job_dir.glob("survey_*") if p.is_dir())
    if not trials:
        raise SystemExit("no trial directories under {}".format(job_dir))

    dim_label_vi, val_label_vi = load_labels()
    rows: list[dict] = []
    task_path = None
    instrument = None
    tokens_in = tokens_out = 0
    cost = 0.0
    failures: list[str] = []

    for trial in trials:
        result = json.loads((trial / "result.json").read_text(encoding="utf-8"))
        if task_path is None:
            # Harbor writes a single `task`, not a `tasks` list, on the trial.
            rel = ((result.get("config") or {}).get("task") or {}).get("path")
            if rel:
                task_path = REPO_ROOT / rel

        agent = result.get("agent_result") or {}
        tokens_in += agent.get("n_input_tokens") or 0
        tokens_out += agent.get("n_output_tokens") or 0
        cost += agent.get("cost_usd") or 0.0

        out = trial / "artifacts" / "app" / "output" / "survey_result.json"
        if not out.is_file():
            failures.append("{}: no survey_result.json".format(trial.name))
            continue
        payload = json.loads(out.read_text(encoding="utf-8"))
        instrument = instrument or payload.get("instrument")

        persona_file = trial / "artifacts" / "app" / "input" / "persona.yaml"
        persona = yaml.safe_load(persona_file.read_text(encoding="utf-8")) or {}
        dims = persona.get("dimensions") or {}
        grounding = persona.get("grounding") or {}
        measured = [k for k, g in grounding.items() if g.get("assignment_type") in SCOREABLE]

        rows.append({
            "trial": trial.name,
            "respondent": {
                "personaId": persona.get("persona_id"),
                "displayName": persona.get("display_name"),
                "sources": persona.get("sources") or {},
                "measuredDimensions": len(measured),
                "totalDimensions": len(dims),
                "profile": {
                    k: {
                        "value": dims[k],
                        "valueVi": (val_label_vi.get(k) or {}).get(str(dims[k]), dims[k]),
                        "labelVi": dim_label_vi.get(k),
                        "measured": (grounding.get(k) or {}).get("assignment_type") in SCOREABLE,
                    }
                    for k in RESPONDENT_KEYS if dims.get(k)
                },
            },
            "answers": payload.get("answers") or [],
            "usage": payload.get("usage"),
        })

    # Without the questionnaire every answer joins to an empty question, and
    # the off-choice check silently passes everything. A dataset that looks
    # clean because nothing was checked is worse than one that fails loudly.
    if task_path is None:
        raise SystemExit("could not resolve the task path from any trial config")
    questionnaire = load_questionnaire(task_path)
    questions = {q["id"]: q for q in (questionnaire.get("questions") or [])}
    if not questions:
        raise SystemExit("no questions loaded from {}".format(task_path))
    answered = {a.get("questionId") for row in rows for a in row["answers"]}
    unknown = sorted(answered - set(questions))
    if unknown:
        raise SystemExit("answers reference unknown questions: {}".format(unknown))

    # Join answers to their question, and tally the distribution per question.
    out_of_range = 0
    distribution: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for row in rows:
        joined = []
        for ans in row["answers"]:
            qid = ans.get("questionId")
            q = questions.get(qid) or {}
            label, in_range = choice_label(q, ans.get("value"))
            if not in_range:
                out_of_range += 1
            raw = ans.get("value")
            for part in (raw if isinstance(raw, (list, tuple)) else [raw]):
                distribution[qid][str(part)] += 1
            joined.append({
                "questionId": qid,
                "prompt": q.get("prompt"),
                "type": q.get("type"),
                "value": ans.get("value"),
                "valueLabel": label,
                "inRange": in_range,
                "rationale": ans.get("rationale") or None,
                "confidence": ans.get("confidence"),
            })
        row["answers"] = joined

    return {
        "formatVersion": "1.0",
        "job": job_dir.name,
        "task": str(task_path.relative_to(REPO_ROOT)) if task_path else None,
        "instrument": instrument,
        "respondentCount": len(rows),
        "questionCount": len(questions),
        "howToRead": {
            "respondents": "One per persona. `sources` and `measuredDimensions` say how much of "
                           "each respondent is measurement: roughly 24 dimensions of ~1,291, the "
                           "rest sampled from the synthesis graph.",
            "answers": "Joined to the questionnaire. `value` is what the model returned; "
                       "`valueLabel` is the choice text; `inRange` is false when the value is not "
                       "an offered choice.",
            "caveat": "These are simulated respondents. An answer reflects a persona whose "
                      "measured layer came from a 30-response driver survey and WVS Wave 7 "
                      "Vietnam, not a person who was asked this question.",
        },
        "run": {
            "trials": len(trials),
            "failures": failures,
            "inputTokens": tokens_in,
            "outputTokens": tokens_out,
            "costUsd": round(cost, 6),
            "answersOutsideChoiceList": out_of_range,
        },
        "questionDistribution": {q: dict(c) for q, c in sorted(distribution.items())},
        "respondents": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("job", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    job_dir = args.job if args.job.is_absolute() else REPO_ROOT / args.job
    doc = collect(job_dir)
    out = args.out or (REPO_ROOT / "reports" / "{}-dataset.json".format(job_dir.name))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    r = doc["run"]
    print("respondents  {}".format(doc["respondentCount"]))
    print("questions    {}".format(doc["questionCount"]))
    print("tokens       {} in / {} out".format(r["inputTokens"], r["outputTokens"]))
    print("cost         ${:.4f}".format(r["costUsd"]))
    print("off-choice   {}".format(r["answersOutsideChoiceList"]))
    if r["failures"]:
        print("FAILURES     {}".format(r["failures"]))
    print("WROTE {}  ({:.2f} MB)".format(out, out.stat().st_size / 1e6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
