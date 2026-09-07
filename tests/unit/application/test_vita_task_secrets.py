"""Guard: no committed task file may carry the deployment secret itself."""

import re
from pathlib import Path

TASKS = sorted(
    (Path(__file__).resolve().parents[3] / "application/tasks").glob("chat_0709-*")
)
# The header value must stay a placeholder; the real value lives in .env.local,
# which .gitignore keeps out of the repository.
PLACEHOLDER = re.compile(r"\$\{[A-Z_][A-Z0-9_]*\}")


def test_every_task_declares_the_auth_header():
    assert TASKS, "no chat_0709-* tasks found"
    for task in TASKS:
        text = (task / "input/chatbot.yaml").read_text(encoding="utf-8")
        assert "x-app-password:" in text, task.name


def test_the_password_header_is_a_placeholder_not_a_literal():
    for task in TASKS:
        for line in (task / "input/chatbot.yaml").read_text(encoding="utf-8").splitlines():
            if "x-app-password:" in line:
                value = line.split(":", 1)[1].strip()
                assert PLACEHOLDER.fullmatch(value), (task.name, value)


def test_no_task_file_contains_a_literal_secret():
    for task in TASKS:
        for path in task.rglob("*"):
            if not path.is_file() or path.suffix not in {".yaml", ".yml", ".json", ".md", ".toml"}:
                continue
            if path.name == "cases.jsonl":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert "test123" not in text, "literal password in {}".format(path)
            assert "sk-or-v1" not in text, "literal API key in {}".format(path)


def test_vehicle_session_header_is_per_trial():
    """A shared vehicle session would let one trial see another's mutations."""
    for task in TASKS:
        text = (task / "input/chatbot.yaml").read_text(encoding="utf-8")
        assert "x-vehicle-session: ${TRIAL_ID}" in text, task.name
