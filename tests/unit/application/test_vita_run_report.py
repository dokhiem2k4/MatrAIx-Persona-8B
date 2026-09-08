"""The tool-call report and the HTML page are what a person actually reads.

A list of tool names says the assistant touched the car. It does not say it
routed the driver 1,500 km to the wrong city -- that is in the property changes,
so those get printed and get a test.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
for slug in (
    "chat_0709-vita-drive-golden-error-recovery",
    "chat_0709-vita-drive-singleturn-mode-ab",
    "chat_0709-vita-drive-multiturn-coverage",
):
    sys.path.insert(0, str(REPO_ROOT / "application/tasks" / slug / "tests"))

import build_vita_run_report as report_module  # noqa: E402
import case_scoring  # noqa: E402
import mode_ab_scoring  # noqa: E402
import multiturn_scoring  # noqa: E402

MODULES = (case_scoring, mode_ab_scoring, multiturn_scoring)

EXPOSURE = [
    {
        "key": "toolResults",
        "value": [
            {
                "success": True,
                "tool": "open_google_maps_route",
                "changes": [
                    {"property": "NAVIGATION_DISTANCE_KM", "oldValue": 0, "newValue": 1507.8},
                    {"property": "NAVIGATION_ROUTE_MODE", "oldValue": "driving", "newValue": "driving"},
                ],
            }
        ],
    }
]

OBSERVATION = {
    "turn_count": 2,
    "turns": [
        {"user_message": "dẫn đường đi", "assistant_message": "vâng",
         "structured_exposure": EXPOSURE, "duration_seconds": 1.5},
        {"user_message": "xa không", "assistant_message": "1508 km",
         "structured_exposure": [], "duration_seconds": 4.25},
    ],
}


def test_tool_report_prints_what_the_call_changed_not_just_its_name():
    for module in MODULES:
        text = module.tool_call_report(OBSERVATION)
        assert "open_google_maps_route" in text, module.__name__
        assert "1507.8" in text, module.__name__
        assert "NAVIGATION_DISTANCE_KM" in text, module.__name__


def test_tool_report_omits_properties_the_call_did_not_move():
    """The deployment lists every field a tool touched, moved or not."""
    for module in MODULES:
        assert "NAVIGATION_ROUTE_MODE" not in module.tool_call_report(OBSERVATION), module.__name__


def test_tool_report_says_so_when_no_tool_ran():
    for module in MODULES:
        text = module.tool_call_report({"turns": [{"structured_exposure": []}]})
        assert "không gọi công cụ nào" in text, module.__name__


def test_tool_report_falls_back_to_the_trial_level_exposure():
    """Trials recorded before per-turn exposure existed must stay readable."""
    legacy = {"turn_count": 1, "turns": [{"user_message": "a", "assistant_message": "b"}],
              "structured_exposure": EXPOSURE}
    for module in MODULES:
        assert "open_google_maps_route" in module.tool_call_report(legacy), module.__name__


def test_latency_totals_the_wait_and_names_the_worst_turn():
    for module in MODULES:
        assert module.total_latency_seconds(OBSERVATION) == 5.75, module.__name__
        assert module.slowest_turn_seconds(OBSERVATION) == 4.25, module.__name__


def test_latency_is_none_rather_than_zero_when_nothing_was_timed():
    """Zero would read as an instant reply; None reads as 'not measured'."""
    blank = {"turns": [{"user_message": "a", "assistant_message": "b"}]}
    for module in MODULES:
        assert module.total_latency_seconds(blank) is None, module.__name__
        assert module.slowest_turn_seconds(blank) is None, module.__name__


RECORD = {
    "trial_id": "t1",
    "case_id": "vg_0230",
    "intent_code": "journey_navigation_places",
    "subintent_name": "Lập và thay đổi tuyến",
    "persona_name": "Bùi Minh Châu",
    "outcome_status": "unresolved",
    "overall_rating": 6,
    "opening_message": "dẫn tôi đến Landmark 81",
    "outcome_reason": "Đáng lẽ Vita phải hỏi lại.",
    "tool_call_report": "Lượt 1: gọi 1 công cụ",
    "response_latency_seconds": 5.75,
    "messages": [
        {"role": "customer", "content": "dẫn tôi đến Landmark 81"},
        {"role": "support", "content": "đã dẫn đường"},
    ],
}


def test_the_page_carries_the_conversation_and_the_verdict():
    page = report_module.build_page([RECORD], "run-a", "run-a-results.jsonl")
    for text in ("dẫn tôi đến Landmark 81", "đã dẫn đường", "Đáng lẽ Vita phải hỏi lại.",
                 "Lượt 1: gọi 1 công cụ", "Bùi Minh Châu", "vg_0230"):
        assert text in page, text
    # The status filter matches on the code; the reader sees Vietnamese.
    assert 'data-outcome="unresolved"' in page
    assert "Không đạt" in page


def test_the_page_escapes_content_rather_than_executing_it():
    """Transcripts are model output; a page that runs them is a page that lies."""
    hostile = dict(RECORD)
    hostile["messages"] = [{"role": "customer", "content": "<script>alert(1)</script>"}]
    hostile["outcome_reason"] = "<img src=x onerror=alert(1)>"
    page = report_module.build_page([hostile], "run-a", "src.jsonl")
    body = page.split("<div class=\"wrap\">", 1)[1].split("</div><script>", 1)[0]
    # The page contains no <script> or <img> of its own, so either appearing in
    # the body means content was written through as markup. The angle brackets
    # are what matter -- "onerror=alert(1)" sitting inside an escaped attribute
    # value is inert text.
    assert "<script" not in body
    assert "<img" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
    assert "&lt;img src=x onerror=alert(1)&gt;" in body


def test_the_page_is_self_contained():
    """It gets opened from a file manager, often with no network."""
    page = report_module.build_page([RECORD], "run-a", "src.jsonl")
    assert "http://" not in page and "https://" not in page
    assert "<style>" in page and "<script>" in page


def test_loading_a_run_folder_with_no_results_fails_loudly(tmp_path: Path):
    import pytest

    with pytest.raises(SystemExit):
        report_module.load_records(tmp_path)


def test_a_written_page_round_trips_from_a_jsonl(tmp_path: Path):
    run = tmp_path / "run-b"
    run.mkdir()
    (run / "run-b-results.jsonl").write_text(
        json.dumps(RECORD, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    records, source = report_module.load_records(run)
    assert source == "run-b-results.jsonl"
    assert records == [RECORD]


def test_the_page_says_the_two_scales_measure_different_things():
    """A pass at 3/10 reads as a bug until the page says what each label is."""
    page = report_module.build_page([RECORD], "run-a", "src.jsonl")
    assert "Đạt / Không đạt" in page
    assert "người lái 6/10" in page


def test_disagreements_count_faults_the_driver_did_not_notice():
    records = [
        {"outcome_status": "unresolved", "overall_rating": 9},   # sai, không bị phàn nàn
        {"outcome_status": "unresolved", "overall_rating": 7},   # sai, không bị phàn nàn
        {"outcome_status": "unresolved", "overall_rating": 6},   # sai và bị chấm thấp -- không tính
        {"outcome_status": "resolved", "overall_rating": 3},     # đúng mà vẫn bị chê
        {"outcome_status": "resolved", "overall_rating": 8},     # nhất trí -- không tính
        {"outcome_status": "resolved", "overall_rating": ""},    # không chấm -- không tính
    ]
    assert report_module.disagreements(records) == (2, 1)


def test_a_run_where_both_scales_agree_shows_no_disagreement_tiles():
    page = report_module.build_page(
        [{**RECORD, "outcome_status": "resolved", "overall_rating": 9}], "run-a", "s.jsonl"
    )
    assert "Sai mà không bị phàn nàn" not in page
    assert "Đúng mà vẫn bị chê" not in page
