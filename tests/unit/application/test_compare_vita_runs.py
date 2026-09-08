"""The comparison report exists to surface regressions, so regressions get a test.

An average that improved can hide a case that broke, and the case that broke is
the reason to read the report before shipping a fix.
"""

import csv
import io
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import compare_vita_runs as compare_module  # noqa: E402

COLUMNS = [
    "case_id", "persona_id", "persona_name", "intent_code", "subintent_name",
    "scenario", "expected_decision", "outcome_status", "observed_decision",
    "observed_tools", "overall_rating", "outcome_reason",
]


def write_run(directory: Path, name: str, rows: list[dict], pairs=None) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "{}-results.csv".format(name)
    with io.open(path, "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, extrasaction="ignore", restval="")
        writer.writeheader()
        writer.writerows(rows)
    if pairs is not None:
        (directory / "{}-manifest.json".format(name)).write_text(
            json.dumps({"task_path": "t", "pairs": pairs}), encoding="utf-8"
        )
    return directory


def row(case_id: str, status: str, **extra) -> dict:
    base = {
        "case_id": case_id,
        "persona_id": "p1",
        "persona_name": "Người lái",
        "intent_code": "journey_navigation_places",
        "subintent_name": "Tìm điểm đến",
        "outcome_status": status,
    }
    base.update(extra)
    return base


PAIRS = [{"persona_path": "p.yaml", "case_id": c} for c in ("c1", "c2", "c3")]


def test_a_regression_is_named_even_when_the_average_improved(tmp_path: Path):
    before = write_run(tmp_path / "before", "before", [
        row("c1", "unresolved"), row("c2", "unresolved"), row("c3", "resolved"),
    ], pairs=PAIRS)
    after = write_run(tmp_path / "after", "after", [
        row("c1", "resolved"), row("c2", "resolved"), row("c3", "unresolved"),
    ], pairs=PAIRS)

    records, notes = compare_module.compare(before, after)
    verdicts = {r["case_id"]: r["verdict"] for r in records}
    assert verdicts == {"c1": "fixed", "c2": "fixed", "c3": "regressed"}
    assert notes == []


def test_partially_resolved_ranks_between_the_two_verdicts():
    assert compare_module.verdict("unresolved", "partially_resolved") == "fixed"
    assert compare_module.verdict("resolved", "partially_resolved") == "regressed"
    assert compare_module.verdict("unresolved", "unresolved") == "still_failing"
    assert compare_module.verdict("resolved", "resolved") == "still_passing"


def test_a_different_pair_list_is_called_out_not_silently_compared(tmp_path: Path):
    """Two runs of different samples are not a before/after of the same thing."""
    before = write_run(tmp_path / "before", "before", [row("c1", "resolved")], pairs=PAIRS)
    after = write_run(tmp_path / "after", "after", [row("c1", "resolved")], pairs=PAIRS[:1])
    _, notes = compare_module.compare(before, after)
    assert any("KHÔNG cùng danh sách" in note for note in notes)


def test_a_missing_manifest_is_called_out(tmp_path: Path):
    before = write_run(tmp_path / "before", "before", [row("c1", "resolved")])
    after = write_run(tmp_path / "after", "after", [row("c1", "resolved")])
    _, notes = compare_module.compare(before, after)
    assert any("thiếu manifest" in note for note in notes)


def test_pairs_only_in_one_run_are_reported_not_dropped(tmp_path: Path):
    before = write_run(tmp_path / "before", "before", [
        row("c1", "resolved"), row("c2", "resolved"),
    ], pairs=PAIRS)
    after = write_run(tmp_path / "after", "after", [row("c1", "resolved")], pairs=PAIRS)
    records, notes = compare_module.compare(before, after)
    assert len(records) == 1
    assert any("chỉ có ở lượt trước" in note for note in notes)
