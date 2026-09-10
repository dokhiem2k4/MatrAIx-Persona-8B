"""A run manifest is what makes a before/after comparison mean anything.

Re-running a task after a fix only measures the fix if the second run faces the
same people asking the same things. The manifest pins that down, and the drift
check is what stops a replay from silently comparing two different experiments.
"""

import json
from pathlib import Path

import pytest

from application.scripts import vita_run_manifest as manifest_module
from application.scripts.vita_case_jobs import (
    build_case_agent_entries,
    build_pair_agent_entries,
    pairs_from_agents,
)

TASK = "application/tasks/chat_0709-vita-drive-golden-error-recovery"
PERSONA = "persona/datasets/vn-drivers/persona_row-000.yaml"


def build(**overrides):
    kwargs = dict(
        run_name="run-a",
        task_path=TASK,
        model_name="openrouter/deepseek/deepseek-v4-flash",
        persona_paths=[PERSONA],
        case_ids=["vg_0001", "vg_0002"],
        pairs=[(PERSONA, "vg_0001"), (PERSONA, "vg_0002")],
    )
    kwargs.update(overrides)
    return manifest_module.build_manifest(**kwargs)


def test_manifest_names_the_personas_and_the_intents_of_the_run():
    m = build()
    assert m["personas"][0]["persona_id"] == "row-000"
    assert m["personas"][0]["display_name"]
    # The intent of each case is on the manifest itself, so it reads as a
    # coverage list without cases.jsonl open beside it.
    assert all(case["parent_intent_code"] for case in m["cases"])
    assert all(case["subintent_code"] for case in m["cases"])


def test_replay_rebuilds_the_same_trials_in_the_same_order():
    """Order is the interleaving; a reordered replay covers something else."""
    pairs = [(PERSONA, "vg_0002"), (PERSONA, "vg_0001")]
    m = build(pairs=pairs)
    replayed = build_pair_agent_entries(manifest_module.replay_pairs(m), "model-x")
    assert pairs_from_agents(replayed) == pairs


def test_recipe_agents_round_trip_through_the_manifest():
    agents = build_case_agent_entries([PERSONA], ["vg_0001", "vg_0002"], "model-x")
    m = build(pairs=pairs_from_agents(agents))
    rebuilt = build_pair_agent_entries(manifest_module.replay_pairs(m), "model-x")
    assert rebuilt == agents


def test_a_clean_repo_reports_no_drift():
    assert manifest_module.check_drift(build()) == []


def test_drift_is_reported_when_a_case_changed():
    m = build()
    m["cases"][0]["content_sha256"] = "0" * 64
    problems = manifest_module.check_drift(m)
    assert any("vg_0001" in problem for problem in problems)


def test_drift_is_reported_when_a_persona_changed_or_vanished():
    m = build()
    m["personas"][0]["content_sha256"] = "0" * 64
    assert any("persona changed" in problem for problem in manifest_module.check_drift(m))

    gone = build()
    gone["personas"][0]["persona_path"] = "persona/datasets/vn-drivers/nope.yaml"
    assert any("persona file is gone" in problem for problem in manifest_module.check_drift(gone))


def test_drift_is_reported_when_a_case_left_the_dataset():
    m = build(case_ids=["vg_0001"], pairs=[(PERSONA, "vg_0001")])
    m["cases"][0]["case_id"] = "vg_9999"
    assert any("gone from the dataset" in p for p in manifest_module.check_drift(m))


def test_loading_refuses_a_manifest_from_another_format_version(tmp_path: Path):
    path = tmp_path / "m.json"
    m = build()
    m["manifest_version"] = 999
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(SystemExit):
        manifest_module.load_manifest(path)


def test_loading_refuses_a_manifest_with_nothing_to_replay(tmp_path: Path):
    path = tmp_path / "m.json"
    m = build()
    m["pairs"] = []
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(SystemExit):
        manifest_module.load_manifest(path)
