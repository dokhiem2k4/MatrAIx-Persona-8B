"""Build job-recipe agent entries for case-parametrised Vita trials.

Kept separate from ``generate_application_job.py`` because that script imports
``_repo_imports`` at module scope, so it is only importable when run as a script.
"""

from __future__ import annotations

from typing import Any

AGENT_NAME = "persona-claude-code"


def build_case_agent_entries(
    persona_paths: list[str], case_ids: list[str], model_name: str
) -> list[dict[str, Any]]:
    """Build one ``agents[]`` entry per persona x case pair.

    Case varies fastest so that stopping a run early still covers every persona.
    """
    return [
        {
            "name": AGENT_NAME,
            "model_name": model_name,
            "kwargs": {"persona_path": persona_path, "case_id": case_id},
        }
        for persona_path in persona_paths
        for case_id in case_ids
    ]
