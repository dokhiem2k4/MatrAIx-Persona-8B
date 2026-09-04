#!/usr/bin/env python3
"""Turn a finished chatbot job into one dataset: a conversation per persona.

A chat trial produces three artefacts that only make sense together -- the
transcript, the persona's self-reported rating, and the persona that produced
both. Harbor keeps them in separate files under a directory per trial, so this
joins them into one row per conversation.

The rating travels with its reasoning. A number on its own is unfalsifiable;
`reason` and `needNotes` cite the turns that produced it, which is what makes a
score auditable rather than something to take on faith.

Usage:
    uv run python scripts/export_chat_dataset.py jobs/vn-drv-chat-agent-v3
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LABELS_VI = REPO_ROOT / "persona/schema/labels/dimensions.labels.vi.json"

RESPONDENT_KEYS = (
    "age_bracket", "gender_identity", "vn_locality", "domain", "life_stage",
)
SCOREABLE = {"observed", "direct", "forum_measured"}

#: Harbor writes the customer/support pair; the rest of the stack reads
#: user/assistant. Normalise on the way out so a consumer sees one vocabulary.
ROLE_MAP = {"customer": "user", "support": "assistant"}


def load_labels() -> tuple[dict, dict]:
    if not LABELS_VI.is_file():
        return {}, {}
    pack = json.loads(LABELS_VI.read_text(encoding="utf-8")).get("dimensions", {})
    return (
        {k: v.get("label") for k, v in pack.items() if v.get("label")},
        {k: (v.get("values") or {}) for k, v in pack.items()},
    )


def collect(job_dir: Path) -> dict:
    trials = sorted(p for p in job_dir.glob("chat_*") if p.is_dir())
    if not trials:
        raise SystemExit("no trial directories under {}".format(job_dir))

    dim_vi, val_vi = load_labels()
    rows, failures = [], []
    task_path = None
    tokens_in = tokens_out = 0
    cost = 0.0

    for trial in trials:
        result = json.loads((trial / "result.json").read_text(encoding="utf-8"))
        if task_path is None:
            rel = ((result.get("config") or {}).get("task") or {}).get("path")
            if rel:
                task_path = REPO_ROOT / rel

        agent = result.get("agent_result") or {}
        tokens_in += agent.get("n_input_tokens") or 0
        tokens_out += agent.get("n_output_tokens") or 0
        cost += agent.get("cost_usd") or 0.0

        if result.get("exception_info"):
            failures.append("{}: {}".format(
                trial.name, (result["exception_info"].get("exception_type") or "error")))
            continue

        out = trial / "artifacts" / "app" / "output"
        transcript_file = out / "transcript.json"
        if not transcript_file.is_file():
            failures.append("{}: no transcript".format(trial.name))
            continue
        transcript = json.loads(transcript_file.read_text(encoding="utf-8"))

        feedback = {}
        fb = out / "user_feedback.json"
        if fb.is_file():
            feedback = json.loads(fb.read_text(encoding="utf-8"))

        persona_file = trial / "artifacts" / "app" / "input" / "persona.yaml"
        persona = yaml.safe_load(persona_file.read_text(encoding="utf-8")) or {}
        dims = persona.get("dimensions") or {}
        grounding = persona.get("grounding") or {}
        measured = [k for k, g in grounding.items() if g.get("assignment_type") in SCOREABLE]

        messages = [
            {
                "turn": i // 2 + 1,
                "role": ROLE_MAP.get(m.get("role"), m.get("role")),
                "content": m.get("content"),
            }
            for i, m in enumerate(transcript.get("messages") or [])
        ]

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
                        "valueVi": (val_vi.get(k) or {}).get(str(dims[k]), dims[k]),
                        "labelVi": dim_vi.get(k),
                    }
                    for k in RESPONDENT_KEYS if dims.get(k)
                },
            },
            "conversation": {
                "turns": sum(1 for m in messages if m["role"] == "user"),
                "messages": messages,
            },
            "rating": feedback,
        })

    ratings = [r["rating"].get("overallExperienceRating") for r in rows
               if isinstance(r["rating"].get("overallExperienceRating"), (int, float))]
    return {
        "formatVersion": "1.0",
        "job": job_dir.name,
        "task": str(task_path.relative_to(REPO_ROOT)) if task_path else None,
        "conversationCount": len(rows),
        "howToRead": {
            "conversation": "Real exchange with the deployed Vita app. Roles normalised to "
                            "user/assistant.",
            "rating": "The persona's own assessment after the conversation. `reason` and the "
                      "*Notes fields cite the turns behind the score -- a number without them "
                      "cannot be checked.",
            "respondent": "`measuredDimensions` of `totalDimensions` says how much of this "
                          "persona is measurement rather than sampled from the synthesis graph.",
            "caveat": "Simulated respondents. A rating reflects a persona built from a "
                      "30-response driver survey and WVS Wave 7 Vietnam, not a driver who used "
                      "the car.",
        },
        "run": {
            "trials": len(trials),
            "failures": failures,
            "inputTokens": tokens_in,
            "outputTokens": tokens_out,
            "costUsd": round(cost, 6),
        },
        "ratingDistribution": dict(collections.Counter(ratings)),
        "conversations": rows,
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
    print("conversations {}".format(doc["conversationCount"]))
    print("ratings       {}".format(doc["ratingDistribution"]))
    print("tokens        {} in / {} out".format(r["inputTokens"], r["outputTokens"]))
    print("cost          ${:.4f}".format(r["costUsd"]))
    if r["failures"]:
        print("FAILURES      {}".format(r["failures"]))
    print("WROTE {}  ({:.2f} MB)".format(out, out.stat().st_size / 1e6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
