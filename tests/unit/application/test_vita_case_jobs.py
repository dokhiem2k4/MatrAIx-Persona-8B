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
