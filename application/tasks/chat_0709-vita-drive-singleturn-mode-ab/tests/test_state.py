from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mode_ab_scoring import build_evaluation_payload

OUTPUT_DIR = Path(
    os.environ.get("HARBOR_OUTPUT_DIR")
    or os.environ.get("MATRIX_OUTPUT_DIR")
    or "/app/output"
)
CASE_RUN_PATH = OUTPUT_DIR / "case_run.json"
FEEDBACK_PATH = OUTPUT_DIR / "user_feedback.json"


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
        if c["contextType"] == "assistant_mode"
        for f in c["facets"]
    }
    # There is no ground truth here, so the reward can only mean "this trial
    # produced usable data", never "the assistant was right".
    if facets["replied"] != "yes":
        fail("case {} produced no assistant reply".format(facets["case_id"]))
    for key in ("assistant_profile_id", "vehicle_state"):
        if not facets.get(key):
            fail("case {} is missing experiment factor {}".format(facets["case_id"], key))
    # Fail loudly rather than contribute a cell that silently ran the default
    # profile: a grid full of those would report "the profiles are the same".
    if facets.get("profile_applied") == "no":
        fail(
            "case {} asked for profile {!r} but the deployment served {!r}; "
            "this trial does not measure the factor".format(
                facets["case_id"],
                str(facets.get("assistant_profile_id")),
                str(facets.get("served_profile")),
            )
        )
    print(
        "PASS: case {} ({} / {}) replied with {} chars".format(
            facets["case_id"], facets["assistant_mode"], facets["vehicle_state"],
            facets["reply_char_count"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
