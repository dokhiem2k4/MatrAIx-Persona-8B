"""The exporter must carry both stimulus mechanisms and the verifier's scores."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from export_vita_multiturn_results import (  # noqa: E402
    COLUMNS,
    stimulus_from_trial,
    verifier_facets,
)


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_pipeline_seed_is_still_read(tmp_path):
    got = stimulus_from_trial(
        tmp_path,
        {"seed": {"rowId": "r1", "intentCode": "my_car", "subintentCode": "diagnostics",
                  "sourcePersonaId": "vn-drv-001", "vehicleState": "driving",
                  "assistantMode": "quiet", "firstInput": "chẩn đoán xe"}},
    )
    assert got["row_id"] == "r1"
    assert got["case_id"] == ""
    assert got["subintent_code"] == "diagnostics"


def test_case_run_is_read_when_there_is_no_seed(tmp_path):
    _write(tmp_path / "artifacts/app/output/case_run.json",
           {"case": {"case_id": "vg_0137", "parent_intent_code": "journey_navigation_places",
                     "subintent_code": "destination_poi", "subintent_label_vi": "Tìm điểm đến/POI",
                     "error_type": "missing_information", "user_input": "Dẫn tôi đến đó",
                     "state": {"vehicle_state": "driving", "assistant_profile_id": "cheeky"}}})
    got = stimulus_from_trial(tmp_path, {})
    assert got["case_id"] == "vg_0137"
    assert got["subintent_code"] == "destination_poi"
    assert got["scenario"] == "missing_information"
    assert got["seed_first_input"] == "Dẫn tôi đến đó"


def test_case_run_reports_the_real_profile_not_the_dead_mode(tmp_path):
    _write(tmp_path / "artifacts/app/output/case_run.json",
           {"case": {"state": {"vehicle_state": "parking", "assistant_profile_id": "rustic"}}})
    assert stimulus_from_trial(tmp_path, {})["assistant_mode"] == "rustic"


def test_missing_stimulus_yields_blanks_not_a_crash(tmp_path):
    got = stimulus_from_trial(tmp_path, {})
    assert got["case_id"] == "" and got["subintent_code"] == ""


def test_verifier_facets_are_flattened_across_contexts(tmp_path):
    _write(tmp_path / "verifier/structured_output.json",
           {"contexts": [
               {"contextType": "error_recovery", "facets": [
                   {"key": "decision_match", "value": "match"},
                   {"key": "case_integrity", "value": "ok"}]},
               {"contextType": "user_feedback", "facets": [
                   {"key": "overall_experience_rating", "value": 8}]}]})
    got = verifier_facets(tmp_path)
    assert got["decision_match"] == "match"
    assert got["case_integrity"] == "ok"
    assert got["overall_experience_rating"] == 8


def test_no_verifier_output_is_not_an_error(tmp_path):
    assert verifier_facets(tmp_path) == {}


def test_persona_profile_stays_a_column():
    """An id alone does not explain why a rating came out the way it did."""
    assert "persona_profile" in COLUMNS
    assert "case_id" in COLUMNS


from export_vita_multiturn_results import describe_persona, load_labels  # noqa: E402


def test_a_real_persona_renders_its_traits():
    labels, values = load_labels()
    got = describe_persona(
        "persona/datasets/vn-drivers/persona_row-000.yaml", labels, values, {}
    )
    assert "Nhóm tuổi" in got
    assert "Kiên nhẫn" in got


def test_an_unreadable_persona_says_so_instead_of_going_blank():
    """A blank cell would read as 'this person has no traits'."""
    got = describe_persona("persona/datasets/gone/persona_x.yaml", {}, {}, {})
    assert got.startswith("(không đọc được hồ sơ persona:")


def test_a_missing_path_is_reported_too():
    assert describe_persona("", {}, {}, {}) == "(trial ghi không có persona_path)"


from export_vita_multiturn_results import STIMULI_COLUMNS, stimuli_row  # noqa: E402


def test_stimuli_row_puts_the_dataset_wording_beside_what_was_said():
    """Judging a paraphrase needs both halves in the same row."""
    got = stimuli_row({
        "case_id": "vg_0068",
        "seed_first_input": "Dẫn tôi đến bệnh viện",
        "opening_message": "Vita ơi, dẫn tôi đến bệnh viện gần nhất đi.",
        "case_integrity": "not_applicable",
    })
    assert got["seed_input"] == "Dẫn tôi đến bệnh viện"
    assert got["first_input"] == "Vita ơi, dẫn tôi đến bệnh viện gần nhất đi."
    assert got["case_integrity"] == "not_applicable"


def test_stimuli_row_marks_provenance_by_mechanism():
    assert stimuli_row({"case_id": "vg_0001"})["source"] == "golden"
    assert stimuli_row({"case_id": ""})["source"] == "pipeline"


def test_stimuli_columns_carry_the_scoring_context():
    for key in ("expected_decision", "observed_decision", "input_constraint", "persona_profile"):
        assert key in STIMULI_COLUMNS


def test_launcher_sets_the_task_path_variable():
    """Without it the runtime ignores chatbot.yaml and calls /v1/messages."""
    script = (
        Path(__file__).resolve().parents[3] / "scripts/run_vita_case_job.sh"
    ).read_text(encoding="utf-8")
    assert "MATRIX_CHATBOT_TASK_PATH" in script
    assert "export_vita_multiturn_results.py" in script
    assert "--run-dir" in script


def test_launcher_refuses_to_reuse_a_run_folder_before_spending():
    """A clash found at export time means the money is already gone."""
    script = (
        Path(__file__).resolve().parents[3] / "scripts/run_vita_case_job.sh"
    ).read_text(encoding="utf-8")
    guard = script.index('run folder exists')
    run = script.index("uv run matraix run")
    assert guard < run


def test_launcher_creates_the_run_folder_before_running():
    """An in-flight run should be visible on disk, not appear only at the end."""
    script = (Path(__file__).resolve().parents[3] / "scripts/run_vita_case_job.sh").read_text(
        encoding="utf-8"
    )
    assert script.index('mkdir -p "${DATA_DIR}"') < script.index("uv run matraix run")


def test_launcher_removes_the_folder_when_the_run_produced_nothing():
    """A run that dies early must not leave a folder blocking its own name."""
    script = (Path(__file__).resolve().parents[3] / "scripts/run_vita_case_job.sh").read_text(
        encoding="utf-8"
    )
    assert "trap cleanup_empty_run_dir EXIT" in script
    assert "rmdir" in script


def test_exporter_has_no_columns_the_feedback_file_never_fills():
    """needNotes/preferenceNotes do not exist; those columns were always blank."""
    assert "need_notes" not in COLUMNS
    assert "preference_notes" not in COLUMNS
    for key in ("rating_reason", "clarifying_notes", "need_satisfaction"):
        assert key in COLUMNS
