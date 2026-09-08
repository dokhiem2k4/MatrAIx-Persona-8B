"""Record the persona x case pairs a run used, so a later run can repeat them.

The point is before/after comparison. Re-running a task after the assistant is
fixed only measures the fix if the second run faces the *same* people asking the
*same* things; a fresh sample changes the stimulus and the difference in scores
then says nothing.

Case ids alone are not enough. ``cases.jsonl`` and the persona files are
editable, so a replay months later can quietly ask a different question under
the same id. Every persona and case is therefore stored with a content hash, and
a replay reports drift instead of silently comparing two different experiments.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

MANIFEST_VERSION = 1

# Copied onto every case entry so the manifest reads as a coverage list on its
# own -- which intents and failure modes this run actually touched -- without
# needing cases.jsonl open beside it.
CASE_INDEX_FIELDS = (
    "parent_intent_code",
    "subintent_code",
    "subintent_label_vi",
    "error_type",
    "case_type",
    "input_constraint",
)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def digest_case(case: dict[str, Any]) -> str:
    """Hash a case by its content, insensitive to key order in the file."""
    return _sha256(json.dumps(case, sort_keys=True, ensure_ascii=False))


def digest_persona(path: Path) -> str:
    """Hash a persona file byte for byte."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cases(task_path: str) -> dict[str, dict[str, Any]]:
    """Every case in a task, keyed by id."""
    path = REPO_ROOT / task_path / "input" / "cases.jsonl"
    cases: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            case = json.loads(line)
            cases[str(case["case_id"])] = case
    return cases


def describe_persona(persona_path: str) -> dict[str, Any]:
    """Identity and content hash of one persona file.

    Reads the two identifying lines textually rather than parsing 6,500 lines of
    YAML: this runs once per persona per run and nothing here needs the traits.
    """
    absolute = REPO_ROOT / persona_path
    entry: dict[str, Any] = {
        "persona_path": persona_path,
        "persona_id": "",
        "display_name": "",
        "content_sha256": "",
    }
    if not absolute.is_file():
        entry["missing"] = True
        return entry
    entry["content_sha256"] = digest_persona(absolute)
    for line in absolute.read_text(encoding="utf-8").splitlines():
        if line.startswith("persona_id:"):
            entry["persona_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("display_name:"):
            entry["display_name"] = line.split(":", 1)[1].strip()
        if entry["persona_id"] and entry["display_name"]:
            break
    return entry


def build_manifest(
    *,
    run_name: str,
    task_path: str,
    model_name: str,
    persona_paths: list[str],
    case_ids: list[str],
    pairs: list[tuple[str, str]],
    max_turns: int | None = None,
    sut_base_url: str = "",
) -> dict[str, Any]:
    """Everything needed to run this exact experiment again."""
    all_cases = load_cases(task_path)
    case_entries = []
    for case_id in case_ids:
        case = all_cases.get(case_id)
        if case is None:
            case_entries.append({"case_id": case_id, "missing": True})
            continue
        entry: dict[str, Any] = {"case_id": case_id}
        for field in CASE_INDEX_FIELDS:
            entry[field] = case.get(field, "")
        entry["expected_decision"] = str((case.get("expected") or {}).get("decision") or "")
        entry["content_sha256"] = digest_case(case)
        case_entries.append(entry)

    return {
        "manifest_version": MANIFEST_VERSION,
        "run_name": run_name,
        "created_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "task_path": task_path,
        "model_name": model_name,
        "max_turns": max_turns,
        "sut_base_url": sut_base_url,
        "trial_count": len(pairs),
        "personas": [describe_persona(path) for path in persona_paths],
        "cases": case_entries,
        # The replay list. Order is preserved because it is the interleaving
        # that decides what a run stopped early actually covered.
        "pairs": [
            {"persona_path": persona_path, "case_id": case_id}
            for persona_path, case_id in pairs
        ],
    }


def write_manifest(manifest: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path


def manifest_path_for(run_name: str) -> Path:
    return REPO_ROOT / "data" / run_name / "{}-manifest.json".format(run_name)


def check_drift(manifest: dict[str, Any]) -> list[str]:
    """Ways the repo has changed since the manifest was written.

    Returned as sentences, not a boolean: a replay with two changed cases is
    still worth running, it just needs those two excluded from the comparison.
    """
    problems: list[str] = []
    task_path = str(manifest.get("task_path") or "")

    for entry in manifest.get("personas") or ():
        persona_path = str(entry.get("persona_path") or "")
        absolute = REPO_ROOT / persona_path
        if not absolute.is_file():
            problems.append("persona file is gone: {}".format(persona_path))
            continue
        recorded = str(entry.get("content_sha256") or "")
        if recorded and digest_persona(absolute) != recorded:
            problems.append(
                "persona changed since the run: {} ({})".format(
                    persona_path, entry.get("display_name") or entry.get("persona_id") or "?"
                )
            )

    try:
        current = load_cases(task_path)
    except OSError:
        problems.append("cannot read cases.jsonl for task {}".format(task_path))
        return problems

    for entry in manifest.get("cases") or ():
        case_id = str(entry.get("case_id") or "")
        case = current.get(case_id)
        if case is None:
            problems.append("case is gone from the dataset: {}".format(case_id))
            continue
        recorded = str(entry.get("content_sha256") or "")
        if recorded and digest_case(case) != recorded:
            problems.append("case changed since the run: {}".format(case_id))
    return problems


def replay_pairs(manifest: dict[str, Any]) -> list[tuple[str, str]]:
    """The persona x case pairs to re-run, in their original order."""
    return [
        (str(pair.get("persona_path") or ""), str(pair.get("case_id") or ""))
        for pair in manifest.get("pairs") or ()
    ]


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    version = manifest.get("manifest_version")
    if version != MANIFEST_VERSION:
        raise SystemExit(
            "manifest version {}, this code writes {}: {}".format(
                version, MANIFEST_VERSION, path
            )
        )
    if not manifest.get("pairs"):
        raise SystemExit("manifest has no pairs to replay: {}".format(path))
    return manifest
