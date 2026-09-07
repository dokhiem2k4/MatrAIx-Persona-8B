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
        "persona/datasets/vn-drivers-forum/persona_vn-drv-001.yaml", labels, values, {}
    )
    assert "Nhóm tuổi" in got
    assert "Kiên nhẫn" in got


def test_an_unreadable_persona_says_so_instead_of_going_blank():
    """A blank cell would read as 'this person has no traits'."""
    got = describe_persona("persona/datasets/gone/persona_x.yaml", {}, {}, {})
    assert got.startswith("(không đọc được hồ sơ persona:")


def test_a_missing_path_is_reported_too():
    assert describe_persona("", {}, {}, {}) == "(trial ghi không có persona_path)"
