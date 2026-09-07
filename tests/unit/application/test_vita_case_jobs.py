from application.scripts.vita_case_jobs import build_case_agent_entries


def test_produces_the_full_cross_product():
    entries = build_case_agent_entries(["p/a.yaml", "p/b.yaml"], ["vg_0001", "vg_0002"], "m")
    assert len(entries) == 4


def test_each_entry_carries_persona_and_case():
    entries = build_case_agent_entries(["p/a.yaml"], ["vg_0001"], "anthropic/claude-haiku-4-5")
    assert entries[0]["model_name"] == "anthropic/claude-haiku-4-5"
    assert entries[0]["kwargs"] == {"persona_path": "p/a.yaml", "case_id": "vg_0001"}


def test_case_varies_fastest_so_a_truncated_run_still_spans_personas():
    entries = build_case_agent_entries(["p/a.yaml", "p/b.yaml"], ["vg_0001", "vg_0002"], "m")
    assert [e["kwargs"]["persona_path"] for e in entries] == [
        "p/a.yaml",
        "p/a.yaml",
        "p/b.yaml",
        "p/b.yaml",
    ]
    assert [e["kwargs"]["case_id"] for e in entries] == [
        "vg_0001",
        "vg_0002",
        "vg_0001",
        "vg_0002",
    ]


def test_empty_inputs_produce_no_entries():
    assert build_case_agent_entries([], ["vg_0001"], "m") == []
    assert build_case_agent_entries(["p/a.yaml"], [], "m") == []


from application.scripts.generate_vita_case_job import build_recipe, load_case_ids  # noqa: E402


def test_smoke_selection_covers_every_error_type():
    import json
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[3]
    cases_path = repo_root / "application/tasks/chat_0709-vita-drive-golden-error-recovery/input/cases.jsonl"
    error_type_by_id = {}
    with cases_path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                case = json.loads(line)
                error_type_by_id[case["case_id"]] = case["error_type"]

    picked = load_case_ids(per_error_type=2)
    assert len(picked) == 20
    assert len({error_type_by_id[case_id] for case_id in picked}) == 10


def test_all_cases_selection_returns_the_whole_dataset():
    assert len(load_case_ids(per_error_type=None)) == 364


def test_recipe_shape_matches_the_job_contract():
    recipe = build_recipe(
        job_name="j",
        model_name="m",
        persona_paths=["persona/datasets/matraix-persona-dev-sample/persona_0042.yaml"],
        case_ids=["vg_0001", "vg_0002"],
    )
    assert recipe["job_name"] == "j"
    assert recipe["tasks"] == [{"path": "application/tasks/chat_0709-vita-drive-golden-error-recovery"}]
    assert len(recipe["agents"]) == 2
    assert recipe["agents"][0]["kwargs"]["case_id"] == "vg_0001"


from application.scripts.generate_vita_case_job import (  # noqa: E402
    credential_env_for_model,
    resolve_model_name,
)


def test_credential_env_is_derived_from_the_model_prefix():
    assert credential_env_for_model("openrouter/anthropic/claude-haiku-4.5") == "OPENROUTER_API_KEY"
    assert credential_env_for_model("anthropic/claude-haiku-4-5") == "ANTHROPIC_API_KEY"
    assert credential_env_for_model("openai/gpt-4o-mini") == "OPENAI_API_KEY"
    assert credential_env_for_model("dashscope/qwen3.6-plus") == "DASHSCOPE_API_KEY"


def test_unknown_provider_has_no_known_credential_env():
    assert credential_env_for_model("some-local-model") is None


def test_model_name_falls_back_to_the_configured_persona_model():
    assert resolve_model_name(None, {"MATRIX_PERSONA_MODEL": "openrouter/x/y"}) == "openrouter/x/y"


def test_explicit_model_name_wins_over_the_environment():
    assert resolve_model_name("openrouter/a/b", {"MATRIX_PERSONA_MODEL": "openrouter/x/y"}) == "openrouter/a/b"


def test_missing_model_name_everywhere_raises():
    import pytest

    with pytest.raises(SystemExit):
        resolve_model_name(None, {})
