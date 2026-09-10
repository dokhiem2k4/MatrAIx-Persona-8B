"""A task can state its own summary without polluting the persona's prompt.

instruction.md is the briefing the persona reads, and it goes into the prompt
verbatim. A summary aimed at a human -- what this task covers, what system it
scores against -- has nowhere else to live, so it gets a field in task.toml.
"""

import tomllib
from pathlib import Path

from backend.service.task_detail_service import get_task_detail

REPO_ROOT = Path(__file__).resolve().parents[4]
TASK = "application/tasks/chat_vita-tasklist"


def test_the_authored_summary_wins_over_the_persona_briefing():
    detail = get_task_detail(TASK, repo_root=REPO_ROOT)
    summary = tomllib.loads(
        (REPO_ROOT / TASK / "task.toml").read_text(encoding="utf-8")
    )["metadata"]["summary"]
    assert detail["description"] == summary.strip()
    # The briefing's opening line must not be what a human reads on the card.
    assert not detail["description"].startswith("Bạn được giao")


def test_the_summary_says_what_it_covers_and_what_it_runs_against():
    """Both questions a person asks before spending money on a run."""
    detail = get_task_detail(TASK, repo_root=REPO_ROOT)
    assert "14/22" in detail["description"]
    assert "136.110.11.55" in detail["description"]


def test_a_task_without_a_summary_still_falls_back_to_the_briefing():
    detail = get_task_detail(
        "application/tasks/chat_0709-vita-drive-golden-error-recovery",
        repo_root=REPO_ROOT,
    )
    assert detail["description"].strip()


def test_the_summary_never_reaches_the_persona():
    """It is metadata, not part of the task content bundle."""
    from playground.task_content_bundle import load_task_content_bundle_for_task_path

    bundle = load_task_content_bundle_for_task_path(TASK, repo_root=REPO_ROOT)
    assert "14/22" not in bundle.instruction_markdown
    assert "136.110.11.55" not in bundle.instruction_markdown
