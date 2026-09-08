"""Build job-recipe agent entries for case-parametrised Vita trials.

Kept separate from ``generate_application_job.py`` because that script imports
``_repo_imports`` at module scope, so it is only importable when run as a script.
"""

from __future__ import annotations

from typing import Any

# Chatbot tasks run the user-sim agent, not persona-claude-code. The latter
# launches the real Claude Code CLI inside the container, which only accepts
# Anthropic models and its own login -- an OpenRouter model id makes it exit
# with "unrecognized_model" and "Not logged in". Mapping fixed at
# harbor_job_service.py:51.
AGENT_NAME = "persona-user-sim"


def build_case_agent_entries(
    persona_paths: list[str], case_ids: list[str], model_name: str
) -> list[dict[str, Any]]:
    """Build one ``agents[]`` entry per persona x case pair.

    Personas are interleaved, so a run stopped early holds roughly the same
    number of trials for each of them. Ordering by persona instead would finish
    the first person's whole sweep before the second one started, and a run cut
    short would compare nobody.
    """
    return [
        {
            "name": AGENT_NAME,
            "model_name": model_name,
            "kwargs": {"persona_path": persona_path, "case_id": case_id},
        }
        for case_id in case_ids
        for persona_path in persona_paths
    ]


def build_pair_agent_entries(
    pairs: list[tuple[str, str]], model_name: str
) -> list[dict[str, Any]]:
    """Build one entry per already-decided persona x case pair.

    Used by a replay, where the pairs come from an earlier run's manifest. The
    order is copied verbatim rather than regenerated: it is the interleaving
    that decides what a run stopped early covered, so a replay that reordered
    would not compare like with like.
    """
    return [
        {
            "name": AGENT_NAME,
            "model_name": model_name,
            "kwargs": {"persona_path": persona_path, "case_id": case_id},
        }
        for persona_path, case_id in pairs
    ]


def pairs_from_agents(agents: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Recover the persona x case pairs from a built recipe, in recipe order."""
    return [
        (
            str((entry.get("kwargs") or {}).get("persona_path") or ""),
            str((entry.get("kwargs") or {}).get("case_id") or ""),
        )
        for entry in agents
    ]
