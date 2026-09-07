from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from multiturn_scoring import build_evaluation_payload

OUTPUT_DIR = Path(
    os.environ.get("HARBOR_OUTPUT_DIR")
    or os.environ.get("MATRIX_OUTPUT_DIR")
    or "/app/output"
)
CASE_RUN_PATH = OUTPUT_DIR / "case_run.json"
FEEDBACK_PATH = OUTPUT_DIR / "user_feedback.json"
MIN_TURNS = 2


def fail(message: str) -> None:
    print("FAIL: {}".format(message), file=sys.stderr)
    raise SystemExit(1)


def _verifier_dir() -> Path:
    explicit = os.environ.get("HARBOR_VERIFIER_DIR")
    if explicit:
        path = Path(explicit)
        path.mkdir(parents=True, exist_ok=True)
        return path
    container_default = Path("/logs/verifier")
    try:
        container_default.mkdir(parents=True, exist_ok=True)
        return container_default
    except OSError:
        pass
    raise RuntimeError(
        "HARBOR_VERIFIER_DIR is required when running outside a Harbor trial container."
    )


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail("{} is not valid JSON: {}".format(path, exc))
    if not isinstance(value, dict):
        fail("{} must contain a JSON object".format(path))
    return value


def main() -> int:
    if not CASE_RUN_PATH.is_file():
        fail("{} is missing; the trial did not run with an assigned case".format(CASE_RUN_PATH))
    case_run = load_json(CASE_RUN_PATH)
    feedback = load_json(FEEDBACK_PATH) if FEEDBACK_PATH.is_file() else None

    payload = build_evaluation_payload(case_run, feedback)
    (_verifier_dir() / "structured_output.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    facets = {
        f["key"]: f["value"]
        for c in payload["contexts"]
        if c["contextType"] == "multiturn_coverage"
        for f in c["facets"]
    }
    # No ground truth: the reward can only mean "a real multi-turn conversation
    # happened", never "the assistant was right".
    if facets["turn_count"] < MIN_TURNS:
        fail(
            "case {} only reached {} turn(s); a coverage trial needs at least {}".format(
                facets["case_id"], facets["turn_count"], MIN_TURNS
            )
        )
    if facets["assistant_reply_count"] < MIN_TURNS:
        fail(
            "case {} got {} assistant reply/replies across {} turns".format(
                facets["case_id"], facets["assistant_reply_count"], facets["turn_count"]
            )
        )
    print(
        "PASS: case {} ({}) ran {} turns, topic overlap {}".format(
            facets["case_id"], facets["subintent_code"], facets["turn_count"],
            facets["lexical_topic_overlap"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
