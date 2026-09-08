"""Bind one dataset case to one trial.

A task opts in by shipping ``input/cases.jsonl``. The job recipe picks the case
through ``agents[].kwargs.case_id``. Tasks without that file keep the previous
free-goal behaviour untouched.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from playground.task_content_bundle import input_dir_for_task_path

_PLACEHOLDER_PREFIX = "${case."
_PLACEHOLDER_SUFFIX = "}"

_CONSTRAINT_LINES = {
    "omit_detail": (
        "- This request is deliberately incomplete: you do NOT add the missing "
        "detail, no matter how unnatural that feels. Keep it just as vague."
    ),
    "preserve_invalid_value": (
        "- This request contains a wrong value on purpose: you do NOT correct it. "
        "Say the wrong value as it stands and let the assistant deal with it."
    ),
}


def load_cases(task_path: str, *, repo_root: Path) -> dict[str, dict[str, Any]]:
    """Return ``{case_id: case}`` for a task, or ``{}`` when it ships no cases."""
    input_dir = input_dir_for_task_path(task_path, repo_root=repo_root)
    if input_dir is None:
        return {}
    path = input_dir / "cases.jsonl"
    if not path.is_file():
        return {}
    cases: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        record = json.loads(text)
        case_id = str(record.get("case_id") or "").strip()
        if case_id:
            cases[case_id] = record
    return cases


def _lookup(case: dict[str, Any], dotted: str) -> Any:
    current: Any = case
    for part in dotted.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def resolve_session_body(
    session_body: dict[str, Any], case: dict[str, Any] | None
) -> dict[str, Any]:
    """Resolve ``${case.<path>}`` placeholders, dropping keys that resolve empty.

    Keys whose value is not a placeholder are passed through untouched, so a
    task can mix constants with case-driven values.
    """
    resolved: dict[str, Any] = {}
    for key, value in (session_body or {}).items():
        if not isinstance(value, str) or not value.startswith(_PLACEHOLDER_PREFIX):
            resolved[key] = value
            continue
        if not value.endswith(_PLACEHOLDER_SUFFIX):
            continue
        dotted = value[len(_PLACEHOLDER_PREFIX) : -len(_PLACEHOLDER_SUFFIX)]
        found = _lookup(case or {}, dotted)
        if found in (None, ""):
            continue
        resolved[key] = found
    return resolved


def _kwargs_case_id(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    agent = payload.get("agent")
    if not isinstance(agent, dict):
        return ""
    kwargs = agent.get("kwargs")
    if not isinstance(kwargs, dict):
        return ""
    return str(kwargs.get("case_id") or "").strip()


def case_id_from_trial(trial_dir: Path | None, env: Mapping[str, str]) -> str:
    """Recover the assigned ``case_id`` for this trial.

    ``agents[].kwargs`` is the binding channel, and it lands in the trial
    directory the same way ``persona_path`` does. The environment variable wins
    so a local harness run can pin a case without writing a config file.
    """
    from_env = str((env or {}).get("MATRIX_CHATBOT_CASE_ID") or "").strip()
    if from_env:
        return from_env
    if trial_dir is None:
        return ""
    for name, unwrap in (
        ("config.json", lambda payload: payload),
        ("result.json", lambda payload: payload.get("config")),
    ):
        path = Path(trial_dir) / name
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        case_id = _kwargs_case_id(unwrap(payload) if isinstance(payload, dict) else None)
        if case_id:
            return case_id
    return ""


def build_case_brief(case: dict[str, Any]) -> str:
    """Describe the assigned goal to the persona without revealing the answer.

    The brief never mentions ``expected``: telling the persona which decision is
    expected would let it steer the assistant toward that decision.
    """
    lines = [
        "You have one specific thing you want from the in-car assistant right now.",
        "",
        "What you want to say, in substance: {!r}".format(case.get("user_input", "")),
        "",
        "How to say it:",
        "- Say it in your own words, in the tone this persona would really use.",
        "- Keep it to one or two sentences, the way someone speaks while driving.",
        "- Never mention that this is a test, and never name any error category.",
    ]
    constraint = _CONSTRAINT_LINES.get(str(case.get("input_constraint") or ""))
    if constraint:
        lines.append(constraint)
    return "\n".join(lines)


def build_case_run_artifact(
    case: dict[str, Any] | None, turns: Any
) -> dict[str, Any] | None:
    """Pair the assigned case with what the first turn actually produced.

    The verifier reads this instead of ``transcript.json`` because the transcript
    fallback in ``chat_eval.fetch_conversation_artifact`` keeps only ``role`` and
    ``content``, dropping every structured field.
    """
    if not case:
        return None
    ordered = list(turns or ())
    first = ordered[0] if ordered else None
    return {
        "case_id": case.get("case_id", ""),
        "case": case,
        "observation": {
            "first_user_message": getattr(first, "user_message", "") if first else "",
            "first_assistant_message": getattr(first, "assistant_message", "") if first else "",
            "structured_exposure": [
                dict(item) for item in (getattr(first, "structured_exposure", []) or ())
            ]
            if first
            else [],
            "turn_count": len(ordered),
            "duration_seconds": getattr(first, "duration_seconds", None) if first else None,
            # Multi-turn tasks need every turn, not just the anchor turn --
            # including what each turn ran and how long it took. Keeping the
            # exposure only on the anchor turn meant a six-turn trial reported
            # the tools of turn one and nothing about the other five.
            "turns": [
                {
                    "turn_index": getattr(turn, "turn_index", index),
                    "user_message": getattr(turn, "user_message", ""),
                    "assistant_message": getattr(turn, "assistant_message", ""),
                    "structured_exposure": [
                        dict(item)
                        for item in (getattr(turn, "structured_exposure", []) or ())
                    ],
                    "duration_seconds": getattr(turn, "duration_seconds", None),
                }
                for index, turn in enumerate(ordered)
            ],
        },
    }
