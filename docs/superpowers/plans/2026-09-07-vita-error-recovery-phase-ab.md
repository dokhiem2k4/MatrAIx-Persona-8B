# Vita Error Recovery — Kế hoạch triển khai giai đoạn A và B

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dựng nền dùng chung (gán case cho trial, bơm state vào request) và task `chat_vita-drive-error-recovery` chấm 364 golden case, chạy được smoke run đối chiếu persona 8B với một model mạnh hơn.

**Architecture:** Trial = 1 persona × 1 case. Case đến từ `input/cases.jsonl`, gán qua `agents[].kwargs.case_id` trong job recipe — kênh đã có sẵn và đã được persist theo trial. Persona nhận case brief qua goal context mới `assigned_case`; state của case được bơm vào request qua `sessionBody` overlay. Runner phát artifact `case_run.json` gộp case + quan sát để verifier tự chứa.

**Tech Stack:** Python 3, pytest, `uv`, openpyxl (chỉ ở converter offline), PyYAML, dataclasses.

**Spec:** `docs/superpowers/specs/2026-09-07-vita-three-task-program-design.md`

## Global Constraints

- **Định danh trong code luôn tiếng Anh.** Tiếng Việt chỉ được xuất hiện như chuỗi hiển thị (`subintent_label_vi`, `response_intent`, nội dung `instruction.md`). Không đặt tên biến, key JSON, hay tên file bằng tiếng Việt.
- **Không đổi hành vi của 13 task chat hiện có.** Mọi nhánh mới phải có điều kiện kích hoạt; task không có `input/cases.jsonl` phải đi đúng đường cũ.
- Chạy test bằng `uv run pytest`. `testpaths = ["tests"]`, `python_files = ["test_*.py"]`.
- Package `playground` nằm ở `packages/playground/src/playground/`; test của package nằm ở `packages/playground/src/playground/tests/`.
- Repo **chưa cài** pandas/openpyxl. Converter chạy bằng `uv run --with openpyxl`.
- Ba bộ xlsx nằm ngoài repo tại `/home/khiemdm/Downloads/`.
- Commit sau mỗi task. Không commit file xlsx nguồn vào repo.

---

## Bản đồ file

**Tạo mới**

| File | Trách nhiệm |
|---|---|
| `application/scripts/vita_intent_taxonomy.py` | Bảng map 60 nhãn subintent tiếng Việt → mã tiếng Anh + parent intent |
| `application/scripts/convert_vita_golden_dataset.py` | Đọc xlsx bộ 1 → `cases.jsonl` + `intent_taxonomy.json` |
| `tests/unit/application/test_vita_intent_taxonomy.py` | Test bảng map |
| `tests/unit/application/test_convert_vita_golden_dataset.py` | Test logic chuyển đổi từng dòng |
| `packages/playground/src/playground/case_binding.py` | Đọc `cases.jsonl`, resolve `${case.*}`, dựng case brief |
| `packages/playground/src/playground/tests/test_case_binding.py` | Test module trên |
| `application/tasks/chat_vita-drive-error-recovery/**` | Task folder đầy đủ |

**Sửa**

| File | Chỗ sửa |
|---|---|
| `packages/playground/src/playground/chatbot_task_config.py:57,179` | Thêm `session_body` vào `ChatbotProtocolConfig` |
| `packages/playground/src/playground/harbor/chat_eval.py:279,317,481` | Overlay `session_body`; phát `case_run.json` |
| `packages/playground/src/playground/user_sim/kickoff.py:42` | Thêm goal context `assigned_case` |
| `packages/playground/src/playground/user_sim/runner.py:176,303` | Rẽ nhánh chọn goal context |
| `packages/playground/src/playground/tests/test_goal_contexts.py:6` | Cập nhật assertion tập id |
| `application/scripts/generate_application_job.py` | Sinh recipe persona × case |

---

# GIAI ĐOẠN A — Nền dùng chung

## Task A1: Bảng taxonomy 60 cặp

**Files:**
- Create: `application/scripts/vita_intent_taxonomy.py`
- Test: `tests/unit/application/test_vita_intent_taxonomy.py`

**Interfaces:**
- Produces: `SUBINTENT_BY_LABEL_VI: dict[str, tuple[str, str]]` (nhãn VI → `(subintent_code, parent_intent_code)`), `UnknownSubintentError(KeyError)`, `subintent_entry(label_vi: str) -> tuple[str, str]`

46 cặp lấy từ bộ 3 (`subintent_name` → `subintent_code`, `intent_code`). 14 cặp còn lại đặt tay, gom vào hai parent intent mới `services_commerce` và `fallback_handling` vì chúng không thuộc 9 parent có sẵn.

- [ ] **Step 1: Viết test thất bại**

```python
# tests/unit/application/test_vita_intent_taxonomy.py
import pytest

from application.scripts.vita_intent_taxonomy import (
    SUBINTENT_BY_LABEL_VI,
    UnknownSubintentError,
    subintent_entry,
)


def test_covers_exactly_sixty_labels():
    assert len(SUBINTENT_BY_LABEL_VI) == 60


def test_codes_are_unique():
    codes = [code for code, _ in SUBINTENT_BY_LABEL_VI.values()]
    assert len(set(codes)) == 60


def test_codes_are_ascii_snake_case():
    for code, parent in SUBINTENT_BY_LABEL_VI.values():
        for value in (code, parent):
            assert value.isascii(), value
            assert value == value.lower(), value
            assert " " not in value, value


def test_known_pair_from_demo_dataset():
    assert subintent_entry("Tìm điểm đến/POI") == ("destination_poi", "journey_navigation_places")


def test_manually_added_pair():
    assert subintent_entry("Unsupported intent") == ("unsupported_intent", "fallback_handling")


def test_label_is_trimmed_before_lookup():
    assert subintent_entry("  Điều hòa  ") == ("climate", "cabin_vehicle_control")


def test_unknown_label_raises():
    with pytest.raises(UnknownSubintentError):
        subintent_entry("Không tồn tại")
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `uv run pytest tests/unit/application/test_vita_intent_taxonomy.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'application.scripts.vita_intent_taxonomy'`

- [ ] **Step 3: Viết bảng map**

```python
# application/scripts/vita_intent_taxonomy.py
"""Map Vietnamese subintent display labels to English identifiers.

The 46 pairs below the ``# --- from Vita Demo dataset ---`` marker come from the
``Dataset - Vita Demo`` workbook (``subintent_name`` -> ``subintent_code``,
``intent_code``). The remaining 14 exist only in the golden dataset and are
assigned here; they fall into two parent intents that the demo dataset does not
use: ``services_commerce`` and ``fallback_handling``.
"""

from __future__ import annotations


class UnknownSubintentError(KeyError):
    """Raised when a subintent label has no English identifier."""


SUBINTENT_BY_LABEL_VI: dict[str, tuple[str, str]] = {
    # --- from Vita Demo dataset ---
    "Bảo dưỡng/dịch vụ": ("maintenance_service", "my_car"),
    "Chẩn đoán": ("diagnostics", "my_car"),
    "Cài đặt hệ thống và ứng dụng": ("system_app_settings", "vita_profile_settings"),
    "Các thương hiệu thành viên Vingroup": ("vingroup_member_brands", "vinfast_vingroup_brands"),
    "Cửa/kính/cốp": ("doors_windows_trunk", "cabin_vehicle_control"),
    "Ghế và tiện nghi": ("seat_comfort", "cabin_vehicle_control"),
    "Giao thông và thời gian dự kiến đến nơi (ETA)": ("traffic_eta", "journey_navigation_places"),
    "Giá bán, chính sách và chương trình VinFast": ("vinfast_sales_policies", "vinfast_vingroup_brands"),
    "Giải thích cảnh báo": ("warning_explanation", "my_car"),
    "Gọi điện": ("calling", "communication_media"),
    "Hệ thống bán hàng và dịch vụ VinFast": ("vinfast_service_network", "vinfast_vingroup_brands"),
    "Hỏi đáp": ("general_qa", "general_qa_conversation"),
    "Hỏi đáp có nguồn kiểm chứng": ("verified_fact_qa", "general_qa_conversation"),
    "Hồ sơ và tài khoản người dùng": ("user_profile_account", "vita_profile_settings"),
    "Khả năng và cách sử dụng ViTa": ("vita_capabilities_usage", "vita_profile_settings"),
    "Kết nối thiết bị và dịch vụ": ("device_service_connectivity", "vita_profile_settings"),
    "Lập tuyến EV": ("ev_routing", "energy_charging"),
    "Lập và thay đổi tuyến": ("route_management", "journey_navigation_places"),
    "Nguồn/danh sách phát": ("source_queue", "communication_media"),
    "Nhắc theo thời gian, vị trí, hành trình hoặc trạng thái xe": ("contextual_reminder", "calendar_tasks"),
    "Nhắn tin": ("messaging", "communication_media"),
    "Phạm vi di chuyển": ("range_sufficiency", "energy_charging"),
    "Quyền truy cập, quyền riêng tư và dữ liệu": ("permissions_privacy_data", "vita_profile_settings"),
    "Thiết lập xe được hỗ trợ": ("supported_vehicle_settings", "cabin_vehicle_control"),
    "Thông tin Tập đoàn Vingroup": ("vingroup_corporate_information", "vinfast_vingroup_brands"),
    "Thông tin xe": ("vehicle_information", "my_car"),
    "Thông tin địa phương/du lịch": ("local_travel_information", "journey_navigation_places"),
    "Thương hiệu và sản phẩm VinFast": ("vinfast_brand_products", "vinfast_vingroup_brands"),
    "Thời tiết/tin tức": ("weather_news", "general_qa_conversation"),
    "Tra cứu": ("calendar_query", "calendar_tasks"),
    "Tra cứu Web": ("web_search", "general_qa_conversation"),
    "Trò chuyện và giải trí": ("conversation_entertainment", "general_qa_conversation"),
    "Trạng thái sạc": ("charging_status", "energy_charging"),
    "Trạng thái xe": ("vehicle_status", "my_car"),
    "Tìm nội dung": ("content_discovery", "communication_media"),
    "Tìm trạm sạc": ("charger_search", "energy_charging"),
    "Tìm điểm đến/POI": ("destination_poi", "journey_navigation_places"),
    "Tùy chọn tương tác với ViTa": ("vita_preferences", "vita_profile_settings"),
    "Tạo/sửa/hủy lịch": ("calendar_create_update_cancel", "calendar_tasks"),
    "Việc cần làm": ("task_management", "calendar_tasks"),
    "Xác định liên hệ": ("contact_resolution", "communication_media"),
    "Âm lượng/vùng âm thanh": ("volume_audio_zone", "communication_media"),
    "Điều hòa": ("climate", "cabin_vehicle_control"),
    "Điều khiển phát": ("playback_control", "communication_media"),
    "Đèn/gương/gạt mưa": ("lights_mirrors_wipers", "cabin_vehicle_control"),
    "Đỗ xe/đến nơi": ("parking_arrival", "journey_navigation_places"),
    # --- golden-only labels, identifiers assigned here ---
    "Mua sắm/thanh toán": ("shopping_payment", "services_commerce"),
    "Đặt chỗ/nhà hàng": ("restaurant_reservation", "services_commerce"),
    "Đặt dịch vụ xe": ("ride_service_booking", "services_commerce"),
    "Đặt món ăn": ("food_ordering", "services_commerce"),
    "Đặt vé/khách sạn": ("ticket_hotel_booking", "services_commerce"),
    "Hỏi sâu nối tiếp": ("followup_deep_dive", "general_qa_conversation"),
    "Hỗ trợ ra quyết định": ("decision_support", "general_qa_conversation"),
    "So sánh và gợi ý lựa chọn": ("comparison_recommendation", "general_qa_conversation"),
    "Tư vấn chuyên sâu": ("expert_consultation", "general_qa_conversation"),
    "Câu vô nghĩa/nhiễu nhận dạng": ("unintelligible_input", "fallback_handling"),
    "Cần thêm thông tin": ("needs_more_information", "fallback_handling"),
    "Yêu cầu mơ hồ/thiếu thông tin": ("ambiguous_request", "fallback_handling"),
    "Unsupported intent": ("unsupported_intent", "fallback_handling"),
    "Too many requests": ("rate_limited", "fallback_handling"),
}


def subintent_entry(label_vi: str) -> tuple[str, str]:
    """Return ``(subintent_code, parent_intent_code)`` for a Vietnamese label."""
    key = (label_vi or "").strip()
    try:
        return SUBINTENT_BY_LABEL_VI[key]
    except KeyError:
        raise UnknownSubintentError(
            "no English identifier for subintent label {!r}; add it to "
            "SUBINTENT_BY_LABEL_VI".format(key)
        ) from None
```

- [ ] **Step 4: Tạo `__init__.py` cho thư mục test nếu chưa có, rồi chạy test**

```bash
mkdir -p tests/unit/application && touch tests/unit/application/__init__.py
uv run pytest tests/unit/application/test_vita_intent_taxonomy.py -v
```
Expected: PASS, 7 test.

- [ ] **Step 5: Commit**

```bash
git add application/scripts/vita_intent_taxonomy.py tests/unit/application/
git commit -m "feat(vita): bảng map 60 nhãn subintent tiếng Việt sang mã tiếng Anh"
```

---

## Task A2: Logic chuyển đổi từng dòng golden

**Files:**
- Create: `application/scripts/convert_vita_golden_dataset.py`
- Test: `tests/unit/application/test_convert_vita_golden_dataset.py`

**Interfaces:**
- Consumes: `subintent_entry` từ Task A1
- Produces: `ERROR_TYPE_CODES: dict[str, str]`, `DECISIONS: frozenset[str]`, `derive_input_constraint(param_validity: str) -> str`, `build_case_record(row: dict, index: int) -> dict`, `ConversionError(ValueError)`

`build_case_record` là hàm thuần, nhận một dict đúng như header xlsx và trả về bản ghi case. Tách khỏi phần đọc file để test được mà không cần xlsx.

- [ ] **Step 1: Viết test thất bại**

```python
# tests/unit/application/test_convert_vita_golden_dataset.py
import pytest

from application.scripts.convert_vita_golden_dataset import (
    ConversionError,
    build_case_record,
    derive_input_constraint,
)

HAPPY_ROW = {
    "case_type": "happy",
    "group": "Không lỗi",
    "error_type": "Happy case",
    "subintent": "Điều hòa",
    "data_availability": None,
    "vehicle_sensor": None,
    "network_connectivity": None,
    "service_state": None,
    "vehicle_state": None,
    "user_input": "Chỉnh nhiệt độ điều hòa 23 độ",
    "param_validity": "ok",
    "expected_decision": "execute",
    "expected_assistant_response": "Dạ, em đã chỉnh nhiệt độ điều hòa lên 23 độ ạ",
    "expected_tool_calls": '[{"module": "climate", "key": "set_temperature", "params": {"temperature": 23}}]',
    "expected_final_state": "nhiệt độ điều hòa đã được set về 23°C",
    "expected_response_intent": "xác nhận đã chỉnh nhiệt độ lên 23 độ",
}

OFFLINE_ROW = {
    **HAPPY_ROW,
    "case_type": "unhappy",
    "group": "Connectivity",
    "error_type": "No Internet",
    "subintent": "Tìm điểm đến/POI",
    "network_connectivity": "offline",
    "user_input": "Tìm cây xăng gần nhất",
    "expected_decision": "defer_retry",
    "expected_tool_calls": "[]",
}


def test_input_constraint_mapping():
    assert derive_input_constraint("ok") == "none"
    assert derive_input_constraint("missing") == "omit_detail"
    assert derive_input_constraint("invalid") == "preserve_invalid_value"


def test_unknown_param_validity_raises():
    with pytest.raises(ConversionError):
        derive_input_constraint("weird")


def test_case_id_is_zero_padded_and_stable():
    assert build_case_record(HAPPY_ROW, 0)["case_id"] == "vg_0001"
    assert build_case_record(HAPPY_ROW, 363)["case_id"] == "vg_0364"


def test_happy_row_maps_identifiers_to_english():
    record = build_case_record(HAPPY_ROW, 0)
    assert record["subintent_code"] == "climate"
    assert record["parent_intent_code"] == "cabin_vehicle_control"
    assert record["error_type"] == "happy_case"
    assert record["group"] == "no_error"
    assert record["input_constraint"] == "none"


def test_vietnamese_kept_only_as_display_strings():
    record = build_case_record(HAPPY_ROW, 0)
    assert record["subintent_label_vi"] == "Điều hòa"
    assert record["user_input"] == "Chỉnh nhiệt độ điều hòa 23 độ"
    assert record["expected"]["response_intent"] == "xác nhận đã chỉnh nhiệt độ lên 23 độ"


def test_tool_calls_parsed_into_objects():
    record = build_case_record(HAPPY_ROW, 0)
    assert record["expected"]["tool_calls"] == [
        {"module": "climate", "key": "set_temperature", "params": {"temperature": 23}}
    ]


def test_empty_state_values_become_none():
    record = build_case_record(HAPPY_ROW, 0)
    assert record["state"] == {
        "data_availability": None,
        "vehicle_sensor": None,
        "network_connectivity": None,
        "service_state": None,
        "vehicle_state": None,
    }


def test_state_is_carried_through():
    record = build_case_record(OFFLINE_ROW, 5)
    assert record["state"]["network_connectivity"] == "offline"
    assert record["expected"]["tool_calls"] == []
    assert record["expected"]["decision"] == "defer_retry"


def test_unknown_decision_raises():
    with pytest.raises(ConversionError):
        build_case_record({**HAPPY_ROW, "expected_decision": "escalate"}, 0)


def test_malformed_tool_calls_raises():
    with pytest.raises(ConversionError):
        build_case_record({**HAPPY_ROW, "expected_tool_calls": "{not json"}, 0)


def test_unknown_subintent_raises():
    with pytest.raises(ConversionError):
        build_case_record({**HAPPY_ROW, "subintent": "Chưa có nhãn này"}, 0)
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `uv run pytest tests/unit/application/test_convert_vita_golden_dataset.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Viết logic chuyển đổi**

```python
# application/scripts/convert_vita_golden_dataset.py
"""Convert the Vita golden single-turn workbook into ``cases.jsonl``.

Run offline; the source workbook is not committed to the repository:

    uv run --with openpyxl python application/scripts/convert_vita_golden_dataset.py \\
        --source "/home/khiemdm/Downloads/golden_singleturn_cover intent_happy&fallback.xlsx" \\
        --out-dir application/tasks/chat_vita-drive-error-recovery/input
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from application.scripts.vita_intent_taxonomy import (
    SUBINTENT_BY_LABEL_VI,
    UnknownSubintentError,
    subintent_entry,
)


class ConversionError(ValueError):
    """Raised when a source row cannot be converted safely."""


DECISIONS = frozenset(
    {"execute", "clarify_or_offer", "defer_retry", "guide_precondition", "refuse_not_supported"}
)

ERROR_TYPE_CODES = {
    "Happy case": "happy_case",
    "Missing Information": "missing_information",
    "Invalid Input": "invalid_input",
    "No Internet": "no_internet",
    "External API Failure": "external_api_failure",
    "400 Bad Request": "bad_request",
    "Resource Not Found": "resource_not_found",
    "Vehicle State Unavailable": "vehicle_state_unavailable",
    "Ambiguous Destination": "ambiguous_destination",
    "Unsafe Command": "unsafe_command",
}

GROUP_CODES = {
    "Không lỗi": "no_error",
    "Understanding": "understanding",
    "Input / Validation": "input_validation",
    "Connectivity": "connectivity",
    "External Service": "external_service",
    "System / API": "system_api",
    "Entity / Resource": "entity_resource",
    "Vehicle State": "vehicle_state",
    "Navigation": "navigation",
    "Safety": "safety",
}

INPUT_CONSTRAINTS = {
    "ok": "none",
    "missing": "omit_detail",
    "invalid": "preserve_invalid_value",
}

STATE_KEYS = (
    "data_availability",
    "vehicle_sensor",
    "network_connectivity",
    "service_state",
    "vehicle_state",
)


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _optional(value: Any) -> str | None:
    text = _text(value)
    return text or None


def derive_input_constraint(param_validity: str) -> str:
    """Map ``param_validity`` to the constraint placed on the persona."""
    key = _text(param_validity)
    try:
        return INPUT_CONSTRAINTS[key]
    except KeyError:
        raise ConversionError("unknown param_validity {!r}".format(key)) from None


def _lookup(table: dict[str, str], value: Any, label: str) -> str:
    key = _text(value)
    try:
        return table[key]
    except KeyError:
        raise ConversionError("unknown {} {!r}".format(label, key)) from None


def _parse_tool_calls(raw: Any) -> list[dict[str, Any]]:
    text = _text(raw) or "[]"
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConversionError("expected_tool_calls is not valid JSON: {}".format(exc)) from None
    if not isinstance(parsed, list):
        raise ConversionError("expected_tool_calls must be a JSON array")
    for entry in parsed:
        if not isinstance(entry, dict):
            raise ConversionError("every tool call must be a JSON object")
        if not _text(entry.get("module")) or not _text(entry.get("key")):
            raise ConversionError("every tool call needs a non-empty module and key")
    return parsed


def build_case_record(row: dict[str, Any], index: int) -> dict[str, Any]:
    """Turn one workbook row into a ``cases.jsonl`` record."""
    try:
        subintent_code, parent_intent_code = subintent_entry(_text(row.get("subintent")))
    except UnknownSubintentError as exc:
        raise ConversionError(str(exc)) from None

    decision = _text(row.get("expected_decision"))
    if decision not in DECISIONS:
        raise ConversionError("unknown expected_decision {!r}".format(decision))

    user_input = _text(row.get("user_input"))
    if not user_input:
        raise ConversionError("user_input must not be empty")

    return {
        "case_id": "vg_{:04d}".format(index + 1),
        "case_type": _lookup({"happy": "happy", "unhappy": "unhappy"}, row.get("case_type"), "case_type"),
        "group": _lookup(GROUP_CODES, row.get("group"), "group"),
        "error_type": _lookup(ERROR_TYPE_CODES, row.get("error_type"), "error_type"),
        "subintent_code": subintent_code,
        "parent_intent_code": parent_intent_code,
        "subintent_label_vi": _text(row.get("subintent")),
        "user_input": user_input,
        "param_validity": _text(row.get("param_validity")),
        "input_constraint": derive_input_constraint(row.get("param_validity")),
        "state": {key: _optional(row.get(key)) for key in STATE_KEYS},
        "expected": {
            "decision": decision,
            "tool_calls": _parse_tool_calls(row.get("expected_tool_calls")),
            "response_intent": _text(row.get("expected_response_intent")),
            "final_state": _text(row.get("expected_final_state")),
            "assistant_response": _text(row.get("expected_assistant_response")),
        },
    }


def _read_rows(source: Path) -> list[dict[str, Any]]:
    import openpyxl

    workbook = openpyxl.load_workbook(source, data_only=True, read_only=True)
    sheet = workbook.worksheets[0]
    rows = list(sheet.iter_rows(values_only=True))
    workbook.close()
    if not rows:
        raise ConversionError("workbook has no rows")
    header = [_text(cell) for cell in rows[0]]
    return [dict(zip(header, row)) for row in rows[1:] if any(cell is not None for cell in row)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    records = [build_case_record(row, index) for index, row in enumerate(_read_rows(args.source))]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    cases_path = args.out_dir / "cases.jsonl"
    cases_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )

    taxonomy = {
        code: {"parent_intent_code": parent, "label_vi": label}
        for label, (code, parent) in sorted(SUBINTENT_BY_LABEL_VI.items(), key=lambda item: item[1][0])
    }
    (args.out_dir / "intent_taxonomy.json").write_text(
        json.dumps(taxonomy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("wrote {} cases to {}".format(len(records), cases_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Chạy test**

Run: `uv run pytest tests/unit/application/test_convert_vita_golden_dataset.py -v`
Expected: PASS, 11 test.

- [ ] **Step 5: Commit**

```bash
git add application/scripts/convert_vita_golden_dataset.py tests/unit/application/test_convert_vita_golden_dataset.py
git commit -m "feat(vita): logic chuyển golden xlsx sang bản ghi case"
```

---

## Task A3: Sinh `cases.jsonl` thật và kiểm tra toàn cục

**Files:**
- Create: `application/tasks/chat_vita-drive-error-recovery/input/cases.jsonl`
- Create: `application/tasks/chat_vita-drive-error-recovery/input/intent_taxonomy.json`
- Test: `tests/unit/application/test_vita_cases_dataset.py`

**Interfaces:**
- Consumes: `main()` từ Task A2
- Produces: `input/cases.jsonl` — 364 dòng, mỗi dòng một JSON object

- [ ] **Step 1: Chạy converter**

```bash
mkdir -p application/tasks/chat_vita-drive-error-recovery/input
uv run --with openpyxl python application/scripts/convert_vita_golden_dataset.py \
  --source "/home/khiemdm/Downloads/golden_singleturn_cover intent_happy&fallback.xlsx" \
  --out-dir application/tasks/chat_vita-drive-error-recovery/input
```
Expected: `wrote 364 cases to application/tasks/chat_vita-drive-error-recovery/input/cases.jsonl`

Nếu báo `ConversionError`, đó là nhãn ngoài bảng map — bổ sung vào `SUBINTENT_BY_LABEL_VI` (và sửa `test_covers_exactly_sixty_labels`) chứ không nới lỏng kiểm tra.

- [ ] **Step 2: Viết test khoá các con số của spec**

```python
# tests/unit/application/test_vita_cases_dataset.py
import collections
import json
from pathlib import Path

CASES_PATH = (
    Path(__file__).resolve().parents[3]
    / "application/tasks/chat_vita-drive-error-recovery/input/cases.jsonl"
)
DECISIONS = {
    "execute",
    "clarify_or_offer",
    "defer_retry",
    "guide_precondition",
    "refuse_not_supported",
}


def _cases():
    with CASES_PATH.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_row_count_matches_spec():
    assert len(_cases()) == 364


def test_case_ids_are_unique():
    ids = [case["case_id"] for case in _cases()]
    assert len(set(ids)) == 364


def test_case_type_distribution_matches_spec():
    counts = collections.Counter(case["case_type"] for case in _cases())
    assert counts == {"unhappy": 304, "happy": 60}


def test_decision_distribution_matches_spec():
    counts = collections.Counter(case["expected"]["decision"] for case in _cases())
    assert counts == {
        "clarify_or_offer": 155,
        "defer_retry": 115,
        "execute": 63,
        "guide_precondition": 21,
        "refuse_not_supported": 10,
    }


def test_input_constraint_distribution_matches_spec():
    counts = collections.Counter(case["input_constraint"] for case in _cases())
    assert counts == {"none": 212, "preserve_invalid_value": 80, "omit_detail": 72}


def test_cases_needing_state_injection_matches_spec():
    needing = [
        case
        for case in _cases()
        if any(value is not None for value in case["state"].values())
    ]
    assert len(needing) == 158


def test_every_decision_is_known():
    assert {case["expected"]["decision"] for case in _cases()} <= DECISIONS


def test_unhappy_cases_expect_no_tool_calls():
    for case in _cases():
        if case["case_type"] == "unhappy":
            assert case["expected"]["tool_calls"] == [], case["case_id"]


def test_identifiers_are_ascii():
    for case in _cases():
        for key in ("case_id", "case_type", "group", "error_type", "subintent_code"):
            assert case[key].isascii(), (case["case_id"], key)


def test_every_subintent_code_is_in_the_taxonomy_file():
    taxonomy = json.loads((CASES_PATH.parent / "intent_taxonomy.json").read_text(encoding="utf-8"))
    for case in _cases():
        assert case["subintent_code"] in taxonomy, case["case_id"]
        assert taxonomy[case["subintent_code"]]["parent_intent_code"] == case["parent_intent_code"]
```

- [ ] **Step 3: Chạy test**

Run: `uv run pytest tests/unit/application/test_vita_cases_dataset.py -v`
Expected: PASS, 10 test.

Nếu `test_unhappy_cases_expect_no_tool_calls` thất bại thì dataset có dòng unhappy kèm tool call — dừng lại, ghi lại `case_id`, hỏi người sở hữu dataset. Không sửa test để né.

- [ ] **Step 4: Commit**

```bash
git add application/tasks/chat_vita-drive-error-recovery/input/ tests/unit/application/test_vita_cases_dataset.py
git commit -m "feat(vita): sinh 364 case golden vào cases.jsonl"
```

---

## Task A4: `sessionBody` trong `chatbot.yaml`

**Files:**
- Modify: `packages/playground/src/playground/chatbot_task_config.py:57` và `:179`
- Test: `application/playground/backend/tests/test_chatbot_task_config.py`

**Interfaces:**
- Produces: `ChatbotProtocolConfig.session_body: dict[str, Any]`, mặc định `{}`

- [ ] **Step 1: Viết test thất bại**

```python
# thêm vào cuối application/playground/backend/tests/test_chatbot_task_config.py
def test_session_body_is_parsed(tmp_path) -> None:
    task_dir = tmp_path / "application" / "tasks" / "chat_vita-drive-error-recovery" / "input"
    task_dir.mkdir(parents=True)
    (task_dir / "chatbot.yaml").write_text(
        "\n".join(
            [
                "transport: external_http",
                "protocol:",
                "  sendMessage:",
                "    staticBody:",
                "      drivingContext: driving",
                "    sessionBody:",
                "      networkConnectivity: ${case.state.network_connectivity}",
                "      serviceState: ${case.state.service_state}",
            ]
        ),
        encoding="utf-8",
    )
    config = load_chatbot_task_config_for_task_path(
        "application/tasks/chat_vita-drive-error-recovery", repo_root=tmp_path
    )
    assert config is not None
    assert config.protocol.static_body == {"drivingContext": "driving"}
    assert config.protocol.session_body == {
        "networkConnectivity": "${case.state.network_connectivity}",
        "serviceState": "${case.state.service_state}",
    }


def test_session_body_defaults_to_empty(tmp_path) -> None:
    task_dir = tmp_path / "application" / "tasks" / "chat_legacy" / "input"
    task_dir.mkdir(parents=True)
    (task_dir / "chatbot.yaml").write_text(
        "transport: external_http\nprotocol:\n  sendMessage:\n    path: /api/chat\n",
        encoding="utf-8",
    )
    config = load_chatbot_task_config_for_task_path(
        "application/tasks/chat_legacy", repo_root=tmp_path
    )
    assert config is not None
    assert config.protocol.session_body == {}
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `uv run pytest application/playground/backend/tests/test_chatbot_task_config.py -v -k session_body`
Expected: FAIL — `AttributeError: 'ChatbotProtocolConfig' object has no attribute 'session_body'`

- [ ] **Step 3: Thêm field và parse**

Ở `chatbot_task_config.py`, trong `ChatbotProtocolConfig` ngay sau dòng `static_body`:

```python
    static_body: dict[str, Any] = field(default_factory=dict)
    session_body: dict[str, Any] = field(default_factory=dict)
```

Trong `_load_from_payload`, ngay sau `static_body=_as_mapping(send.get("staticBody")),`:

```python
            static_body=_as_mapping(send.get("staticBody")),
            session_body=_as_mapping(send.get("sessionBody")),
```

- [ ] **Step 4: Chạy test**

Run: `uv run pytest application/playground/backend/tests/test_chatbot_task_config.py -v`
Expected: PASS, mọi test cũ vẫn xanh.

- [ ] **Step 5: Commit**

```bash
git add packages/playground/src/playground/chatbot_task_config.py application/playground/backend/tests/test_chatbot_task_config.py
git commit -m "feat(playground): chatbot.yaml nhận khối sessionBody"
```

---

## Task A5: Module `case_binding`

**Files:**
- Create: `packages/playground/src/playground/case_binding.py`
- Test: `packages/playground/src/playground/tests/test_case_binding.py`

**Interfaces:**
- Produces:
  - `load_cases(task_path: str, *, repo_root: Path) -> dict[str, dict]` — rỗng khi không có `cases.jsonl`
  - `resolve_session_body(session_body: dict, case: dict | None) -> dict` — bỏ key có giá trị `None`
  - `build_case_brief(case: dict) -> str` — đoạn văn giao việc cho persona
  - `case_id_from_trial(trial_dir: Path | None, env: Mapping[str, str]) -> str` — lấy `case_id` theo thứ tự `MATRIX_CHATBOT_CASE_ID` → `config.json` → `result.json`

- [ ] **Step 1: Viết test thất bại**

```python
# packages/playground/src/playground/tests/test_case_binding.py
import json
from pathlib import Path

from playground.case_binding import (
    build_case_brief,
    case_id_from_trial,
    load_cases,
    resolve_session_body,
)

CASE_OMIT = {
    "case_id": "vg_0137",
    "subintent_code": "destination_poi",
    "subintent_label_vi": "Tìm điểm đến/POI",
    "user_input": "Dẫn tôi đến đó",
    "input_constraint": "omit_detail",
    "state": {"network_connectivity": None, "service_state": None},
    "expected": {"decision": "clarify_or_offer"},
}
CASE_PRESERVE = {**CASE_OMIT, "case_id": "vg_0200", "input_constraint": "preserve_invalid_value",
                 "user_input": "Vingroup thành lập năm 1850 à?"}
CASE_FREE = {**CASE_OMIT, "case_id": "vg_0001", "input_constraint": "none",
             "user_input": "Chỉnh nhiệt độ điều hòa 23 độ"}

SESSION_BODY = {
    "networkConnectivity": "${case.state.network_connectivity}",
    "serviceState": "${case.state.service_state}",
    "constant": "keep-me",
}


def test_resolve_drops_none_values():
    assert resolve_session_body(SESSION_BODY, CASE_OMIT) == {"constant": "keep-me"}


def test_resolve_fills_present_values():
    case = {**CASE_OMIT, "state": {"network_connectivity": "offline", "service_state": None}}
    assert resolve_session_body(SESSION_BODY, case) == {
        "networkConnectivity": "offline",
        "constant": "keep-me",
    }


def test_resolve_without_case_drops_every_placeholder():
    assert resolve_session_body(SESSION_BODY, None) == {"constant": "keep-me"}


def test_resolve_unknown_path_drops_key():
    assert resolve_session_body({"x": "${case.state.nope}"}, CASE_OMIT) == {}


def test_load_cases_returns_empty_when_file_absent(tmp_path):
    assert load_cases("application/tasks/chat_none", repo_root=tmp_path) == {}


def test_load_cases_indexes_by_case_id(tmp_path):
    input_dir = tmp_path / "application" / "tasks" / "chat_x" / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "cases.jsonl").write_text(
        json.dumps(CASE_OMIT, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    cases = load_cases("application/tasks/chat_x", repo_root=tmp_path)
    assert set(cases) == {"vg_0137"}
    assert cases["vg_0137"]["subintent_code"] == "destination_poi"


def test_brief_contains_the_user_input_verbatim():
    assert "Dẫn tôi đến đó" in build_case_brief(CASE_OMIT)


def test_brief_never_leaks_the_expected_decision():
    for case in (CASE_OMIT, CASE_PRESERVE, CASE_FREE):
        assert "clarify_or_offer" not in build_case_brief(case)


def test_omit_brief_forbids_adding_detail():
    brief = build_case_brief(CASE_OMIT)
    assert "do NOT add" in brief
    assert "do NOT correct" not in brief


def test_preserve_brief_forbids_correcting():
    brief = build_case_brief(CASE_PRESERVE)
    assert "do NOT correct" in brief
    assert "do NOT add" not in brief


def test_free_brief_allows_rephrasing_without_extra_constraint():
    brief = build_case_brief(CASE_FREE)
    assert "do NOT add" not in brief
    assert "do NOT correct" not in brief
    assert "own words" in brief


def test_case_id_prefers_the_environment_variable(tmp_path):
    assert case_id_from_trial(tmp_path, {"MATRIX_CHATBOT_CASE_ID": "vg_0009"}) == "vg_0009"


def test_case_id_falls_back_to_trial_config(tmp_path):
    (tmp_path / "config.json").write_text(
        json.dumps({"agent": {"kwargs": {"persona_path": "p.yaml", "case_id": "vg_0137"}}}),
        encoding="utf-8",
    )
    assert case_id_from_trial(tmp_path, {}) == "vg_0137"


def test_case_id_falls_back_to_result_json(tmp_path):
    (tmp_path / "result.json").write_text(
        json.dumps({"config": {"agent": {"kwargs": {"case_id": "vg_0200"}}}}),
        encoding="utf-8",
    )
    assert case_id_from_trial(tmp_path, {}) == "vg_0200"


def test_case_id_is_empty_for_a_legacy_trial(tmp_path):
    assert case_id_from_trial(tmp_path, {}) == ""


def test_case_id_is_empty_without_a_trial_dir():
    assert case_id_from_trial(None, {}) == ""
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `uv run pytest packages/playground/src/playground/tests/test_case_binding.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'playground.case_binding'`

- [ ] **Step 3: Viết module**

```python
# packages/playground/src/playground/case_binding.py
"""Bind one dataset case to one trial.

A task opts in by shipping ``input/cases.jsonl``. The job recipe picks the case
through ``agents[].kwargs.case_id``. Tasks without that file keep the previous
free-goal behaviour untouched.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from playground.task_content_bundle import input_dir_for_task_path

_PLACEHOLDER_PREFIX = "${case."
_PLACEHOLDER_SUFFIX = "}"

_CONSTRAINT_LINES = {
    "omit_detail": (
        "- This request is deliberately incomplete: you do NOT add the missing "
        "detail, no matter how unnatural that feels. Keep it just as vague."
    ),
    "preserve_invalid_value": (
        "- This request contains a wrong value on purpose: you do NOT correct it. "
        "Say the wrong value as it stands and let the assistant deal with it."
    ),
}


def load_cases(task_path: str, *, repo_root: Path) -> dict[str, dict[str, Any]]:
    """Return ``{case_id: case}`` for a task, or ``{}`` when it ships no cases."""
    input_dir = input_dir_for_task_path(task_path, repo_root=repo_root)
    if input_dir is None:
        return {}
    path = input_dir / "cases.jsonl"
    if not path.is_file():
        return {}
    cases: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        record = json.loads(text)
        case_id = str(record.get("case_id") or "").strip()
        if case_id:
            cases[case_id] = record
    return cases


def _lookup(case: dict[str, Any], dotted: str) -> Any:
    current: Any = case
    for part in dotted.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def resolve_session_body(
    session_body: dict[str, Any], case: dict[str, Any] | None
) -> dict[str, Any]:
    """Resolve ``${case.<path>}`` placeholders, dropping keys that resolve empty.

    Keys whose value is not a placeholder are passed through untouched, so a
    task can mix constants with case-driven values.
    """
    resolved: dict[str, Any] = {}
    for key, value in (session_body or {}).items():
        if not isinstance(value, str) or not value.startswith(_PLACEHOLDER_PREFIX):
            resolved[key] = value
            continue
        if not value.endswith(_PLACEHOLDER_SUFFIX):
            continue
        dotted = value[len(_PLACEHOLDER_PREFIX) : -len(_PLACEHOLDER_SUFFIX)]
        found = _lookup(case or {}, dotted)
        if found in (None, ""):
            continue
        resolved[key] = found
    return resolved


def _kwargs_case_id(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    agent = payload.get("agent")
    if not isinstance(agent, dict):
        return ""
    kwargs = agent.get("kwargs")
    if not isinstance(kwargs, dict):
        return ""
    return str(kwargs.get("case_id") or "").strip()


def case_id_from_trial(trial_dir: Path | None, env: Mapping[str, str]) -> str:
    """Recover the assigned ``case_id`` for this trial.

    ``agents[].kwargs`` is the binding channel, and it lands in the trial
    directory the same way ``persona_path`` does. The environment variable wins
    so a local harness run can pin a case without writing a config file.
    """
    from_env = str((env or {}).get("MATRIX_CHATBOT_CASE_ID") or "").strip()
    if from_env:
        return from_env
    if trial_dir is None:
        return ""
    for name, unwrap in (("config.json", lambda p: p), ("result.json", lambda p: p.get("config"))):
        path = Path(trial_dir) / name
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        case_id = _kwargs_case_id(unwrap(payload) if isinstance(payload, dict) else None)
        if case_id:
            return case_id
    return ""


def build_case_brief(case: dict[str, Any]) -> str:
    """Describe the assigned goal to the persona without revealing the answer.

    The brief never mentions ``expected``: telling the persona which decision is
    expected would let it steer the assistant toward that decision.
    """
    lines = [
        "You have one specific thing you want from the in-car assistant right now.",
        "",
        "What you want to say, in substance: {!r}".format(case.get("user_input", "")),
        "",
        "How to say it:",
        "- Say it in your own words, in the tone this persona would really use.",
        "- Keep it to one or two sentences, the way someone speaks while driving.",
        "- Never mention that this is a test, and never name any error category.",
    ]
    constraint = _CONSTRAINT_LINES.get(str(case.get("input_constraint") or ""))
    if constraint:
        lines.append(constraint)
    return "\n".join(lines)
```

- [ ] **Step 4: Chạy test**

Run: `uv run pytest packages/playground/src/playground/tests/test_case_binding.py -v`
Expected: PASS, 16 test.

- [ ] **Step 5: Commit**

```bash
git add packages/playground/src/playground/case_binding.py packages/playground/src/playground/tests/test_case_binding.py
git commit -m "feat(playground): module gán case cho trial"
```

---

## Task A6: Goal context `assigned_case`

**Files:**
- Modify: `packages/playground/src/playground/user_sim/kickoff.py:42`
- Modify: `packages/playground/src/playground/tests/test_goal_contexts.py:6`

**Interfaces:**
- Consumes: không
- Produces: `get_goal_context("assigned_case").template` — chứa `{domain}`, `{sut_description}`, `{persona_context}`, `{case_brief}`

- [ ] **Step 1: Cập nhật test hiện có và thêm test mới**

Sửa `test_registry_has_seeded_contexts` trong `packages/playground/src/playground/tests/test_goal_contexts.py`:

```python
def test_registry_has_seeded_contexts():
    ids = {gc.id for gc in load_goal_contexts()}
    assert ids == {"scenario_default", "assigned_case"}
```

Thêm vào cuối file:

```python
def test_assigned_case_template_consumes_required_fields():
    t = get_goal_context("assigned_case").template
    for key in ("{domain}", "{sut_description}", "{persona_context}", "{case_brief}"):
        assert key in t


def test_assigned_case_does_not_ask_persona_to_invent_a_goal():
    t = get_goal_context("assigned_case").template
    assert "First decide what realistic goal" not in t


def test_scenario_default_has_no_case_slot():
    assert "{case_brief}" not in get_goal_context("scenario_default").template
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `uv run pytest packages/playground/src/playground/tests/test_goal_contexts.py -v`
Expected: FAIL — `KeyError: 'assigned_case'` và assertion tập id sai.

- [ ] **Step 3: Thêm goal context**

Trong `kickoff.py`, sau hằng `_SCENARIO_DEFAULT`:

```python
_ASSIGNED_CASE = """You are a real user of this interactive chatbot application.

Application context: {domain}

{sut_description}

Who you are:
{persona_context}

{case_brief}

Then behave like a genuine human user for the rest of the conversation:
- React to what the assistant says. If it asks you something, answer naturally.
- Keep messages short and conversational (1-3 sentences)."""
```

Và thêm vào `_REGISTRY`:

```python
    "assigned_case": GoalContext(
        id="assigned_case",
        label="Assigned dataset case",
        description="The persona voices one assigned dataset case in its own words.",
        template=_ASSIGNED_CASE,
    ),
```

- [ ] **Step 4: Chạy test**

Run: `uv run pytest packages/playground/src/playground/tests/test_goal_contexts.py -v`
Expected: PASS, 7 test.

- [ ] **Step 5: Commit**

```bash
git add packages/playground/src/playground/user_sim/kickoff.py packages/playground/src/playground/tests/test_goal_contexts.py
git commit -m "feat(playground): goal context assigned_case giao sẵn case cho persona"
```

---

## Task A7: Overlay `sessionBody` vào request

**Files:**
- Modify: `packages/playground/src/playground/harbor/chat_eval.py:279` và `:317`
- Test: `application/playground/backend/tests/test_harbor_chat_eval.py`

**Interfaces:**
- Consumes: `resolve_session_body` (Task A5), `ChatbotProtocolConfig.session_body` (Task A4)
- Produces: `HarborSidecarChatSession.assigned_case: dict | None` — gán sau khi khởi tạo; `None` giữ nguyên hành vi cũ

- [ ] **Step 1: Viết test thất bại**

```python
# thêm vào application/playground/backend/tests/test_harbor_chat_eval.py
from playground.case_binding import resolve_session_body


def _body(static_body, session_body, case):
    return {**dict(static_body), **resolve_session_body(session_body, case)}


def test_body_unchanged_when_no_session_body():
    assert _body({"drivingContext": "driving"}, {}, None) == {"drivingContext": "driving"}


def test_body_unchanged_for_case_without_state():
    case = {"state": {"network_connectivity": None, "service_state": None}}
    body = _body(
        {"drivingContext": "driving"},
        {
            "networkConnectivity": "${case.state.network_connectivity}",
            "serviceState": "${case.state.service_state}",
        },
        case,
    )
    assert body == {"drivingContext": "driving"}


def test_body_carries_state_when_case_has_it():
    case = {"state": {"network_connectivity": "offline", "service_state": None}}
    body = _body(
        {"drivingContext": "driving"},
        {
            "networkConnectivity": "${case.state.network_connectivity}",
            "serviceState": "${case.state.service_state}",
        },
        case,
    )
    assert body == {"drivingContext": "driving", "networkConnectivity": "offline"}


def test_session_body_overrides_static_body_on_key_clash():
    case = {"state": {"vehicle_state": "driving"}}
    body = _body(
        {"drivingContext": "parking"},
        {"drivingContext": "${case.state.vehicle_state}"},
        case,
    )
    assert body == {"drivingContext": "driving"}
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `uv run pytest application/playground/backend/tests/test_harbor_chat_eval.py -v -k body`
Expected: FAIL — `ImportError: cannot import name 'resolve_session_body'` nếu Task A5 chưa xong; nếu A5 xong rồi thì test này xanh ngay và đóng vai lưới an toàn cho Step 3.

- [ ] **Step 3: Nối overlay vào session**

Trong `chat_eval.py`, thêm import ở đầu file:

```python
from playground.case_binding import resolve_session_body
```

Trong `HarborSidecarChatSession.__init__`, sau `self.turns: List[Dict[str, Any]] = []`:

```python
        self.assigned_case: Optional[Dict[str, Any]] = None
```

Trong `run_turn_sync`, đổi dòng dựng body:

```python
        body: Dict[str, Any] = dict(protocol.static_body)
        body.update(resolve_session_body(protocol.session_body, self.assigned_case))
```

Trong `run_capability_sync`, đổi tương tự:

```python
        body: Dict[str, Any] = dict(self.runtime.protocol.static_body)
        body.update(
            resolve_session_body(self.runtime.protocol.session_body, self.assigned_case)
        )
```

- [ ] **Step 4: Chạy test hồi quy đầy đủ**

```bash
uv run pytest application/playground/backend/tests/test_harbor_chat_eval.py -v
uv run pytest application/playground/backend/tests/test_chatbot_tasks.py -v
uv run pytest packages/playground/src/playground/tests/ -v
```
Expected: PASS toàn bộ. `session_body` mặc định `{}` nên 13 task chat hiện có gửi body y hệt trước.

- [ ] **Step 5: Commit**

```bash
git add packages/playground/src/playground/harbor/chat_eval.py application/playground/backend/tests/test_harbor_chat_eval.py
git commit -m "feat(playground): bơm state của case vào request qua sessionBody"
```

---

## Task A8: Rẽ nhánh trong runner và phát `case_run.json`

**Files:**
- Modify: `packages/playground/src/playground/user_sim/runner.py:176` và `:303`
- Modify: `packages/playground/src/playground/harbor/chat_eval.py:481`
- Test: `packages/playground/src/playground/tests/test_case_run_artifact.py`

**Interfaces:**
- Consumes: `load_cases`, `build_case_brief` (Task A5); `get_goal_context("assigned_case")` (Task A6)
- Produces: `build_case_run_artifact(case: dict | None, turns: list) -> dict | None` trong `case_binding.py`; artifact `case_run.json` trong output dir

Lý do phải có artifact riêng: `transcript.json` do `fetch_conversation_artifact()` sinh ra, và nhánh dự phòng của hàm đó chỉ giữ `role` + `content` — `structuredExposure` bị rơi. Verifier không đọc được `decision` từ đó.

- [ ] **Step 1: Viết test thất bại**

```python
# packages/playground/src/playground/tests/test_case_run_artifact.py
from playground.case_binding import build_case_run_artifact
from playground.types import PlaygroundTurn

CASE = {"case_id": "vg_0137", "user_input": "Dẫn tôi đến đó", "input_constraint": "omit_detail"}

TURNS = [
    PlaygroundTurn(
        turn_index=0,
        user_message="Dẫn giúp em tới chỗ đó với",
        assistant_message="Em chưa rõ anh chị muốn đến đâu ạ.",
        structured_exposure=[{"key": "decision", "value": "clarify_or_offer"}],
    ),
    PlaygroundTurn(
        turn_index=1,
        user_message="Aeon Long Biên nhé",
        assistant_message="Dạ em dẫn đường ngay ạ.",
        structured_exposure=[{"key": "decision", "value": "execute"}],
    ),
]


def test_returns_none_without_a_case():
    assert build_case_run_artifact(None, TURNS) is None


def test_carries_the_whole_case():
    artifact = build_case_run_artifact(CASE, TURNS)
    assert artifact["case_id"] == "vg_0137"
    assert artifact["case"] == CASE


def test_observation_anchors_on_the_first_turn():
    observation = build_case_run_artifact(CASE, TURNS)["observation"]
    assert observation["first_user_message"] == "Dẫn giúp em tới chỗ đó với"
    assert observation["first_assistant_message"] == "Em chưa rõ anh chị muốn đến đâu ạ."
    assert observation["structured_exposure"] == [{"key": "decision", "value": "clarify_or_offer"}]
    assert observation["turn_count"] == 2


def test_empty_transcript_yields_empty_observation():
    observation = build_case_run_artifact(CASE, [])["observation"]
    assert observation["first_assistant_message"] == ""
    assert observation["structured_exposure"] == []
    assert observation["turn_count"] == 0
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `uv run pytest packages/playground/src/playground/tests/test_case_run_artifact.py -v`
Expected: FAIL — `ImportError: cannot import name 'build_case_run_artifact'`

- [ ] **Step 3: Thêm hàm dựng artifact**

Thêm vào cuối `packages/playground/src/playground/case_binding.py`:

```python
def build_case_run_artifact(
    case: dict[str, Any] | None, turns: Any
) -> dict[str, Any] | None:
    """Pair the assigned case with what the first turn actually produced.

    The verifier reads this instead of ``transcript.json`` because the transcript
    fallback in ``chat_eval.fetch_conversation_artifact`` keeps only ``role`` and
    ``content``, dropping every structured field.
    """
    if not case:
        return None
    ordered = list(turns or ())
    first = ordered[0] if ordered else None
    return {
        "case_id": case.get("case_id", ""),
        "case": case,
        "observation": {
            "first_user_message": getattr(first, "user_message", "") if first else "",
            "first_assistant_message": getattr(first, "assistant_message", "") if first else "",
            "structured_exposure": [
                dict(item) for item in (getattr(first, "structured_exposure", []) or ())
            ]
            if first
            else [],
            "turn_count": len(ordered),
        },
    }
```

- [ ] **Step 4: Chạy test**

Run: `uv run pytest packages/playground/src/playground/tests/test_case_run_artifact.py -v`
Expected: PASS, 4 test.

- [ ] **Step 5: Nối vào runner**

`PlaygroundConfig` (`types.py:57`) **không** có chỗ chứa kwargs tuỳ ý, và không
cần thêm: `case_id` lấy từ trial dir bằng `case_id_from_trial` của Task A5.

Thêm tham số `trial_dir: Optional[Path] = None` vào **cả hai** hàm
`run_playground` và `run_playground_async`, rồi thay dòng
`goal_context = get_goal_context("scenario_default")` bằng:

```python
    assigned_case = None
    if task_path and repo_root is not None:
        case_id = case_id_from_trial(trial_dir, os.environ)
        if case_id:
            assigned_case = load_cases(task_path, repo_root=repo_root).get(case_id)
            if assigned_case is None:
                raise ValueError(
                    "trial requests case {!r} but {} ships no such case".format(case_id, task_path)
                )
    goal_context = get_goal_context("assigned_case" if assigned_case else "scenario_default")
```

Ném lỗi khi `case_id` có mà case không tồn tại là cố ý: một trial im lặng rơi về
`scenario_default` sẽ tạo ra dữ liệu trông hợp lệ nhưng không đo cái cần đo.

Chỗ render prompt hiện gọi `prompt_bundle(..., task_prompt=goal_context.description)`.
Đổi thành truyền thêm case brief:

```python
    task_prompt = goal_context.description
    if assigned_case is not None:
        task_prompt = goal_context.template.format(
            domain=config.domain,
            sut_description=sut_description,
            persona_context=persona.to_prompt_context(),
            case_brief=build_case_brief(assigned_case),
        )
```

Nếu `Persona` không có `to_prompt_context()`, dùng đúng hàm mà
`prompt_bundle` đang dùng để dựng `{persona_context}` — mở
`packages/playground/src/playground/user_sim/prompts.py` và tái sử dụng, không
tự viết hàm mới.

Cuối cùng, trước vòng lặp lượt, gán case cho session để overlay của Task A7 có
dữ liệu: `session.assigned_case = assigned_case`. Ở `run_playground_async` thì
`session` là tham số đầu tiên của hàm, gán ngay sau khi tính `assigned_case`.

Thêm import ở đầu `runner.py`:

```python
import os
from playground.case_binding import build_case_brief, case_id_from_trial, load_cases
```

Và ở `chat_eval.py:604`, truyền `trial_dir=trial_dir` vào `run_harbor_chat_eval`.

- [ ] **Step 6: Phát artifact**

Trong `chat_eval.py`, hàm `harbor_output_artifacts_from_result`, thêm tham số
`assigned_case: Dict[str, Any] | None = None` và trước `return`:

```python
    artifacts = {
        "transcript.json": transcript_payload,
        "application_result.json": application_result_payload,
        "user_feedback.json": result.questionnaire.artifact_dict(),
    }
    case_run = build_case_run_artifact(assigned_case, result.transcript)
    if case_run is not None:
        artifacts["case_run.json"] = case_run
    return artifacts
```

- [ ] **Step 7: Chạy toàn bộ test hồi quy**

```bash
uv run pytest packages/playground/src/playground/tests/ -v
uv run pytest application/playground/backend/tests/ -v
```
Expected: PASS toàn bộ.

- [ ] **Step 8: Commit**

```bash
git add packages/playground/src/playground/
git commit -m "feat(playground): runner chọn goal context theo case và phát case_run.json"
```

---

# GIAI ĐOẠN B — Task `chat_vita-drive-error-recovery`

## Task B1: Task folder

**Files:**
- Create: `application/tasks/chat_vita-drive-error-recovery/{task.toml,instruction.md,reporting.json,persona_strategy.json,README.md}`
- Create: `application/tasks/chat_vita-drive-error-recovery/input/{context.md,chatbot.yaml,self_report_schema.yaml}`
- Create: `application/tasks/chat_vita-drive-error-recovery/tests/verifier_env.sh`

**Interfaces:**
- Consumes: `input/cases.jsonl` (Task A3)
- Produces: task path `application/tasks/chat_vita-drive-error-recovery` thoả hợp đồng CI

- [ ] **Step 1: Sao chép khung từ task chat gần nhất**

```bash
cp application/tasks/chat_vita-drive-assistant/tests/verifier_env.sh \
   application/tasks/chat_vita-drive-error-recovery/tests/verifier_env.sh
cp application/tasks/chat_vita-drive-assistant/input/self_report_schema.yaml \
   application/tasks/chat_vita-drive-error-recovery/input/self_report_schema.yaml
```

- [ ] **Step 2: Viết `task.toml`**

```toml
version = "1.0"
artifacts = [ "/app/output",]

[task]
name = "application/vita-drive-error-recovery"

[metadata]
difficulty = "hard"
type = "chatbot"
domain = "automotive-ai"
tags = [ "in-cabin assistant", "error handling", "fallback", "golden dataset", "single turn",]

[verifier]
timeout_sec = 300.0

[agent]
timeout_sec = 600.0

[environment]
definition = "application/shared-chat-persona"
cpus = 1
memory_mb = 2048
storage_mb = 10240
gpus = 0
```

- [ ] **Step 3: Viết `input/chatbot.yaml`**

```yaml
transport: external_http
runtimeDefaults:
  applicationId: vita_drive_assistant
  applicationContext: in_cabin_driving
  domain: automotive_ai
  maxTurns: 2
capabilities:
  - text_chat
connection:
  baseUrlEnv: VITA_ASSISTANT_API_URL
  baseUrl: http://127.0.0.1:3001
  healthPath: /health
protocol:
  sendMessage:
    method: POST
    path: /api/chat
    sessionIdField: sessionId
    messageField: message
    titleField: ""
    botTypeField: ""
    staticBody:
      drivingContext: driving
    sessionBody:
      dataAvailability: ${case.state.data_availability}
      vehicleSensor: ${case.state.vehicle_sensor}
      networkConnectivity: ${case.state.network_connectivity}
      serviceState: ${case.state.service_state}
      vehicleState: ${case.state.vehicle_state}
  response:
    sessionIdField: sessionId
    replyField: assistantText
structuredExposure:
  fields:
    - key: decision
      label: Assistant decision
      selector: decision
    - key: toolCalls
      label: Tool calls
      selector: toolCalls
      format: json
artifacts:
  transcript: transcript.json
  applicationResult: application_result.json
  feedback: user_feedback.json
```

`selector` là dot-path thường, không phải JSONPath — `lookup_path()` ở `structured_exposure.py:8` chỉ tách chuỗi theo dấu chấm.

- [ ] **Step 4: Viết `persona_strategy.json`**

```json
{
  "schemaVersion": "1.0",
  "sources": [],
  "dimensionFilters": {
    "age_bracket": ["25-34", "35-44", "45-54"]
  },
  "sampling": {
    "mode": "random",
    "sampleSize": 5
  }
}
```

Không lọc theo dimension `intent` của persona: nó mang giá trị như `"Get task done"`, không liên quan gì tới `subintent_code` của dataset, và lọc theo nó sẽ thu hẹp pool mà không phục vụ mục tiêu nào.

- [ ] **Step 5: Viết `instruction.md` và `input/context.md`**

Cả hai file **không được liệt kê nhóm lỗi**. Mục tiêu cụ thể đến từ case brief;
nêu tên nhóm lỗi ở đây sẽ mớm cho persona và làm hỏng phép đo.

`instruction.md`:

```markdown
# Trợ lý Xe Thông Minh Vita (In-Cabin Voice Assistant - VinFast VF9)

Bạn đang ngồi trong xe điện VinFast VF9 và nói chuyện với trợ lý trên xe (Vita).

1. **Bạn đã có sẵn một việc cụ thể muốn nhờ Vita.** Việc đó được giao riêng cho
   lượt này. Hãy nói ra bằng đúng giọng và thói quen ngôn ngữ của persona, ngắn
   gọn như người đang lái xe nói thật.
2. **Giữ nguyên nội dung việc được giao.** Không thêm chi tiết mà việc đó không
   có, không tự sửa những gì nghe có vẻ sai. Cách nói là của bạn, nội dung là
   của việc được giao.
3. **Phản ứng tự nhiên với câu trả lời của Vita.** Nếu Vita hỏi lại, cứ trả lời
   như người dùng thật.
4. **Đánh giá trải nghiệm** sau khi kết thúc: Vita có hiểu đúng ý bạn không, có
   làm được việc bạn nhờ không, và cách nói của nó có dễ chịu khi đang lái xe không.

Không bao giờ nhắc tới việc đây là một bài kiểm tra.
```

`input/context.md`:

```markdown
# Vita Drive Assistant

Vita là trợ lý giọng nói tích hợp sẵn trên xe điện VinFast. Nó nhận lệnh bằng
tiếng Việt và có thể:

- **Điều khiển xe**: điều hòa, ghế, cửa/kính/cốp, đèn, gương, gạt mưa
- **Dẫn đường**: tìm điểm đến, lập và đổi tuyến, tra tình hình giao thông và ETA, tìm chỗ đỗ
- **Pin và sạc**: trạng thái sạc, quãng đường còn đi được, tìm trạm sạc, lập tuyến có điểm sạc
- **Giải trí và liên lạc**: phát nhạc, chọn nguồn phát, âm lượng, gọi điện, nhắn tin
- **Lịch và việc cần làm**: tạo/sửa/huỷ lịch, nhắc theo thời gian hoặc vị trí
- **Thông tin**: tra cứu web, thời tiết, tin tức, thông tin xe và thông tin VinFast/Vingroup

Vita chạy trong xe nên có lúc mạng yếu hoặc dịch vụ bên ngoài không phản hồi.
Cảm biến trên xe cũng có lúc không đọc được. Đó là chuyện bình thường của một
trợ lý trên xe.
```

Đoạn cuối `context.md` cố ý chỉ nói ở mức "chuyện bình thường" mà không kể tên
nhóm lỗi nào, để persona không suy ra được lượt này đang thử tình huống gì.

- [ ] **Step 6: Viết `reporting.json`**

```json
{
  "schemaVersion": "1.0",
  "contextRules": [
    {
      "match": { "contextType": "error_recovery" },
      "distributions": [
        { "id": "error_recovery.match_by_error_type", "facetKey": "error_type", "title": "Nhóm lỗi" },
        { "id": "error_recovery.match_by_subintent", "facetKey": "subintent_code", "title": "Subintent" },
        { "id": "error_recovery.decision_match", "facetKey": "decision_match", "title": "Khớp quyết định" },
        { "id": "error_recovery.case_integrity", "facetKey": "case_integrity", "title": "Toàn vẹn case" },
        { "id": "error_recovery.decision_source", "facetKey": "decision_source", "title": "Nguồn quyết định" }
      ]
    },
    {
      "match": { "contextType": "user_feedback" },
      "distributions": [
        { "id": "user_feedback.rating_by_segment", "facetKey": "overall_experience_rating", "title": "Overall experience rating" }
      ]
    }
  ]
}
```

- [ ] **Step 7: Chạy test hợp đồng CI**

Run: `uv run pytest tests/environment/test_application_task_contracts.py -v -k error_recovery`
Expected: PASS. Test này quét mọi thư mục task nên nó là lưới an toàn thật, không phải hình thức.

- [ ] **Step 8: Commit**

```bash
git add application/tasks/chat_vita-drive-error-recovery/
git commit -m "feat(vita): khung task chat_vita-drive-error-recovery"
```

---

## Task B2: Verifier — kiểm tra toàn vẹn case

**Files:**
- Create: `application/tasks/chat_vita-drive-error-recovery/tests/case_scoring.py`
- Test: `tests/unit/application/test_vita_case_scoring.py`

**Interfaces:**
- Produces: `classify_case_integrity(case: dict, first_user_message: str) -> str` trả `ok` / `violated` / `not_applicable`

Phiên bản đầu dùng heuristic từ vựng, cố tình đơn giản và dễ soi. Nó **không** thay được LLM-judge, nhưng bắt được dạng vi phạm phổ biến nhất — persona thêm danh từ riêng hoặc con số mà case gốc không có.

- [ ] **Step 1: Viết test thất bại**

```python
# tests/unit/application/test_vita_case_scoring.py
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[3]
        / "application/tasks/chat_vita-drive-error-recovery/tests"
    ),
)

from case_scoring import classify_case_integrity  # noqa: E402

OMIT = {"input_constraint": "omit_detail", "user_input": "Dẫn tôi đến đó"}
PRESERVE = {"input_constraint": "preserve_invalid_value", "user_input": "Vingroup thành lập năm 1850 à?"}
FREE = {"input_constraint": "none", "user_input": "Chỉnh nhiệt độ điều hòa 23 độ"}


def test_free_case_is_not_applicable():
    assert classify_case_integrity(FREE, "Cho anh 23 độ nhé") == "not_applicable"


def test_omit_case_stays_ok_when_still_vague():
    assert classify_case_integrity(OMIT, "Dẫn giúp em tới chỗ đó với") == "ok"


def test_omit_case_violated_when_persona_names_a_place():
    assert classify_case_integrity(OMIT, "Dẫn em tới Aeon Long Biên với") == "violated"


def test_omit_case_violated_when_persona_adds_a_number():
    assert classify_case_integrity({"input_constraint": "omit_detail", "user_input": "Chỉnh nhiệt độ"},
                                   "Chỉnh nhiệt độ lên 23 độ nhé") == "violated"


def test_preserve_case_ok_when_wrong_number_kept():
    assert classify_case_integrity(PRESERVE, "Vingroup lập năm 1850 đúng không anh?") == "ok"


def test_preserve_case_violated_when_wrong_number_dropped():
    assert classify_case_integrity(PRESERVE, "Vingroup thành lập năm nào nhỉ?") == "violated"


def test_empty_message_is_violated_for_constrained_cases():
    assert classify_case_integrity(OMIT, "") == "violated"
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `uv run pytest tests/unit/application/test_vita_case_scoring.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'case_scoring'`

- [ ] **Step 3: Viết module chấm**

```python
# application/tasks/chat_vita-drive-error-recovery/tests/case_scoring.py
"""Score one assigned case against what the persona and the assistant did."""

from __future__ import annotations

import re
from typing import Any

_NUMBER = re.compile(r"\d+")
# A capitalised word that is not the first word of a sentence reads as a proper
# noun in Vietnamese, which is how a persona usually leaks a withheld place name.
_PROPER_NOUN = re.compile(r"(?<!^)(?<![.!?]\s)\b[A-ZÀ-Ỹ][a-zà-ỹ]{2,}")


def classify_case_integrity(case: dict[str, Any], first_user_message: str) -> str:
    """Return ``ok`` / ``violated`` / ``not_applicable`` for the input constraint.

    ``not_applicable`` means the case placed no constraint on the persona, so the
    trial can never be invalidated on these grounds.
    """
    constraint = str(case.get("input_constraint") or "none")
    if constraint == "none":
        return "not_applicable"

    said = (first_user_message or "").strip()
    if not said:
        return "violated"

    original = str(case.get("user_input") or "")

    if constraint == "omit_detail":
        added_numbers = set(_NUMBER.findall(said)) - set(_NUMBER.findall(original))
        added_nouns = set(_PROPER_NOUN.findall(said)) - set(_PROPER_NOUN.findall(original))
        return "violated" if (added_numbers or added_nouns) else "ok"

    if constraint == "preserve_invalid_value":
        required = set(_NUMBER.findall(original))
        return "ok" if required <= set(_NUMBER.findall(said)) else "violated"

    return "not_applicable"
```

- [ ] **Step 4: Chạy test**

Run: `uv run pytest tests/unit/application/test_vita_case_scoring.py -v`
Expected: PASS, 7 test.

- [ ] **Step 5: Commit**

```bash
git add application/tasks/chat_vita-drive-error-recovery/tests/case_scoring.py tests/unit/application/test_vita_case_scoring.py
git commit -m "feat(vita): kiểm tra toàn vẹn ràng buộc đầu vào của case"
```

---

## Task B3: Verifier — khớp quyết định và tool call

**Files:**
- Modify: `application/tasks/chat_vita-drive-error-recovery/tests/case_scoring.py`
- Create: `application/tasks/chat_vita-drive-error-recovery/tests/test_state.py`
- Create: `application/tasks/chat_vita-drive-error-recovery/tests/test.sh`
- Test: `tests/unit/application/test_vita_case_scoring.py` (mở rộng)

**Interfaces:**
- Consumes: `classify_case_integrity` (Task B2)
- Produces: `observed_decision(exposure: list) -> tuple[str, str]` trả `(decision, source)` với `source ∈ {"structured", "unavailable"}`; `tool_calls_match(expected: list, observed: list) -> bool`; `build_evaluation_payload(case_run: dict, feedback: dict | None) -> dict`

Phiên bản đầu chỉ cài nhánh `structured`. Khi SUT không trả `decision`, `source` là `unavailable` và facet `decision_match` mang giá trị `unknown` — **không đoán bừa**. Nhánh LLM-judge là việc riêng, làm sau khi smoke run cho biết tỉ lệ `unavailable` thực tế là bao nhiêu.

- [ ] **Step 1: Viết test thất bại**

```python
# thêm vào tests/unit/application/test_vita_case_scoring.py
from case_scoring import build_evaluation_payload, observed_decision, tool_calls_match  # noqa: E402


def test_decision_read_from_structured_exposure():
    assert observed_decision([{"key": "decision", "value": "clarify_or_offer"}]) == (
        "clarify_or_offer",
        "structured",
    )


def test_decision_unavailable_when_exposure_empty():
    assert observed_decision([]) == ("", "unavailable")


def test_decision_unavailable_when_key_missing():
    assert observed_decision([{"key": "toolCalls", "value": []}]) == ("", "unavailable")


def test_tool_calls_match_ignores_params():
    expected = [{"module": "climate", "key": "set_temperature", "params": {"temperature": 23}}]
    observed = [{"module": "climate", "key": "set_temperature", "params": {"temperature": 24}}]
    assert tool_calls_match(expected, observed) is True


def test_tool_calls_match_is_order_insensitive():
    expected = [{"module": "a", "key": "x"}, {"module": "b", "key": "y"}]
    observed = [{"module": "b", "key": "y"}, {"module": "a", "key": "x"}]
    assert tool_calls_match(expected, observed) is True


def test_tool_calls_mismatch_on_extra_call():
    assert tool_calls_match([], [{"module": "climate", "key": "set_temperature"}]) is False


def test_payload_marks_match_and_carries_facets():
    case_run = {
        "case_id": "vg_0137",
        "case": {
            "case_id": "vg_0137",
            "case_type": "unhappy",
            "group": "understanding",
            "error_type": "missing_information",
            "subintent_code": "destination_poi",
            "input_constraint": "omit_detail",
            "user_input": "Dẫn tôi đến đó",
            "expected": {"decision": "clarify_or_offer", "tool_calls": []},
        },
        "observation": {
            "first_user_message": "Dẫn giúp em tới chỗ đó với",
            "first_assistant_message": "Em chưa rõ anh chị muốn đến đâu ạ.",
            "structured_exposure": [{"key": "decision", "value": "clarify_or_offer"}],
            "turn_count": 2,
        },
    }
    payload = build_evaluation_payload(case_run, None)
    facets = {
        facet["key"]: facet["value"]
        for context in payload["contexts"]
        if context["contextType"] == "error_recovery"
        for facet in context["facets"]
    }
    assert facets["decision_match"] == "match"
    assert facets["case_integrity"] == "ok"
    assert facets["decision_source"] == "structured"
    assert facets["error_type"] == "missing_information"
    assert facets["subintent_code"] == "destination_poi"


def test_payload_marks_unknown_when_decision_unavailable():
    case_run = {
        "case_id": "vg_0001",
        "case": {
            "case_id": "vg_0001",
            "case_type": "happy",
            "group": "no_error",
            "error_type": "happy_case",
            "subintent_code": "climate",
            "input_constraint": "none",
            "user_input": "Chỉnh nhiệt độ điều hòa 23 độ",
            "expected": {"decision": "execute", "tool_calls": []},
        },
        "observation": {
            "first_user_message": "Cho anh 23 độ nhé",
            "first_assistant_message": "Dạ em chỉnh rồi ạ.",
            "structured_exposure": [],
            "turn_count": 1,
        },
    }
    facets = {
        facet["key"]: facet["value"]
        for context in build_evaluation_payload(case_run, None)["contexts"]
        if context["contextType"] == "error_recovery"
        for facet in context["facets"]
    }
    assert facets["decision_match"] == "unknown"
    assert facets["decision_source"] == "unavailable"
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `uv run pytest tests/unit/application/test_vita_case_scoring.py -v`
Expected: FAIL — `ImportError: cannot import name 'observed_decision'`

- [ ] **Step 3: Bổ sung `case_scoring.py`**

```python
DECISION_KEY = "decision"
TOOL_CALLS_KEY = "toolCalls"


def _exposure_value(exposure: Any, key: str) -> Any:
    for field in exposure or ():
        if isinstance(field, dict) and str(field.get("key") or "") == key:
            return field.get("value")
    return None


def observed_decision(exposure: Any) -> tuple[str, str]:
    """Return ``(decision, source)``; source is ``structured`` or ``unavailable``.

    There is deliberately no guessing branch: an assistant reply that carries no
    structured decision is reported as unknown rather than classified by keyword,
    which would silently invent data.
    """
    value = _exposure_value(exposure, DECISION_KEY)
    text = str(value or "").strip()
    return (text, "structured") if text else ("", "unavailable")


def _call_signature(call: Any) -> tuple[str, str]:
    if not isinstance(call, dict):
        return ("", "")
    return (str(call.get("module") or "").strip(), str(call.get("key") or "").strip())


def tool_calls_match(expected: Any, observed: Any) -> bool:
    """Compare tool calls on ``module`` + ``key`` only, ignoring params and order."""
    return {_call_signature(call) for call in expected or ()} == {
        _call_signature(call) for call in observed or ()
    }


def _facet(key: str, label: str, role: str, kind: str, value: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "role": role, "kind": kind, "value": value}


def build_evaluation_payload(
    case_run: dict[str, Any], feedback: dict[str, Any] | None
) -> dict[str, Any]:
    """Build the ``structured_output.json`` payload for one assigned case."""
    case = dict(case_run.get("case") or {})
    observation = dict(case_run.get("observation") or {})
    exposure = observation.get("structured_exposure") or []
    expected = dict(case.get("expected") or {})

    decision, decision_source = observed_decision(exposure)
    if decision_source == "unavailable":
        decision_match = "unknown"
    else:
        decision_match = "match" if decision == str(expected.get("decision") or "") else "mismatch"

    observed_calls = _exposure_value(exposure, TOOL_CALLS_KEY) or []
    if decision_source == "unavailable" and not observed_calls:
        tool_match = "unknown"
    else:
        tool_match = "match" if tool_calls_match(expected.get("tool_calls"), observed_calls) else "mismatch"

    integrity = classify_case_integrity(case, str(observation.get("first_user_message") or ""))

    contexts: list[dict[str, Any]] = [
        {
            "key": "error_recovery.primary",
            "label": "Error recovery",
            "contextType": "error_recovery",
            "facets": [
                _facet("decision_match", "Khớp quyết định", "primary", "categorical", decision_match),
                _facet("tool_call_match", "Khớp tool call", "primary", "categorical", tool_match),
                _facet("case_integrity", "Toàn vẹn case", "control", "categorical", integrity),
                _facet("decision_source", "Nguồn quyết định", "control", "categorical", decision_source),
                _facet("case_id", "Case", "control", "categorical", str(case.get("case_id") or "")),
                _facet("case_type", "Loại case", "control", "categorical", str(case.get("case_type") or "")),
                _facet("group", "Nhóm", "control", "categorical", str(case.get("group") or "")),
                _facet("error_type", "Nhóm lỗi", "control", "categorical", str(case.get("error_type") or "")),
                _facet("subintent_code", "Subintent", "control", "categorical", str(case.get("subintent_code") or "")),
                _facet("input_constraint", "Ràng buộc đầu vào", "control", "categorical", str(case.get("input_constraint") or "")),
                _facet("expected_decision", "Quyết định kỳ vọng", "evidence", "categorical", str(expected.get("decision") or "")),
                _facet("observed_decision", "Quyết định quan sát", "evidence", "categorical", decision),
                _facet("turn_count", "Số lượt", "metric", "continuous", int(observation.get("turn_count") or 0)),
            ],
        }
    ]

    if feedback is not None:
        rating = feedback.get("overallExperienceRating")
        contexts.append(
            {
                "key": "user_feedback.primary",
                "label": "User feedback",
                "contextType": "user_feedback",
                "facets": [
                    _facet(
                        "overall_experience_rating",
                        "Overall experience rating",
                        "primary",
                        "continuous",
                        int(rating) if isinstance(rating, int) else None,
                    )
                ],
            }
        )

    return {
        "schemaVersion": "1.0",
        "artifactType": "matraix.trial_evaluation",
        "contexts": contexts,
    }
```

- [ ] **Step 4: Chạy test**

Run: `uv run pytest tests/unit/application/test_vita_case_scoring.py -v`
Expected: PASS, 15 test.

- [ ] **Step 5: Viết `test_state.py` và `test.sh`**

`test.sh` giống hệt task chat hiện có:

```bash
#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/verifier_env.sh"

if python3 "${TESTS_DIR}/test_state.py"; then
  echo 1 > "${VERIFIER_DIR}/reward.txt"
else
  echo 0 > "${VERIFIER_DIR}/reward.txt"
  exit 1
fi
```

`test_state.py` đọc `case_run.json`, gọi `build_evaluation_payload`, ghi
`structured_output.json`, và trả mã thoát 0 chỉ khi
`decision_match == "match"` **và** `tool_call_match == "match"`:

```python
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from case_scoring import build_evaluation_payload

OUTPUT_DIR = Path(
    os.environ.get("HARBOR_OUTPUT_DIR") or os.environ.get("MATRIX_OUTPUT_DIR") or "/app/output"
)


def _verifier_dir() -> Path:
    explicit = os.environ.get("HARBOR_VERIFIER_DIR")
    if explicit:
        path = Path(explicit)
        path.mkdir(parents=True, exist_ok=True)
        return path
    container_default = Path("/logs/verifier")
    container_default.mkdir(parents=True, exist_ok=True)
    return container_default


def fail(message: str) -> None:
    print("FAIL: {}".format(message), file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    case_run_path = OUTPUT_DIR / "case_run.json"
    if not case_run_path.is_file():
        fail("{} is missing; the trial did not run with an assigned case".format(case_run_path))
    case_run = json.loads(case_run_path.read_text(encoding="utf-8"))

    feedback_path = OUTPUT_DIR / "user_feedback.json"
    feedback = json.loads(feedback_path.read_text(encoding="utf-8")) if feedback_path.is_file() else None

    payload = build_evaluation_payload(case_run, feedback)
    (_verifier_dir() / "structured_output.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    facets = {
        facet["key"]: facet["value"]
        for context in payload["contexts"]
        if context["contextType"] == "error_recovery"
        for facet in context["facets"]
    }
    if facets["decision_match"] != "match" or facets["tool_call_match"] != "match":
        fail(
            "case {} expected {!r} but observed {!r} (source={}, integrity={})".format(
                facets["case_id"],
                facets["expected_decision"],
                facets["observed_decision"],
                facets["decision_source"],
                facets["case_integrity"],
            )
        )
    print("PASS: case {} matched".format(facets["case_id"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Chạy verifier cục bộ trên một `case_run.json` giả**

```bash
TMP=$(mktemp -d)
mkdir -p "$TMP/output" "$TMP/verifier"
python3 - "$TMP/output/case_run.json" <<'PY'
import json, sys
json.dump({
  "case_id": "vg_0137",
  "case": {"case_id": "vg_0137", "case_type": "unhappy", "group": "understanding",
           "error_type": "missing_information", "subintent_code": "destination_poi",
           "input_constraint": "omit_detail", "user_input": "Dẫn tôi đến đó",
           "expected": {"decision": "clarify_or_offer", "tool_calls": []}},
  "observation": {"first_user_message": "Dẫn giúp em tới chỗ đó với",
                  "first_assistant_message": "Em chưa rõ ạ.",
                  "structured_exposure": [{"key": "decision", "value": "clarify_or_offer"}],
                  "turn_count": 2}
}, open(sys.argv[1], "w"), ensure_ascii=False)
PY
HARBOR_OUTPUT_DIR="$TMP/output" HARBOR_VERIFIER_DIR="$TMP/verifier" \
  python3 application/tasks/chat_vita-drive-error-recovery/tests/test_state.py
cat "$TMP/verifier/structured_output.json" | head -20
```
Expected: `PASS: case vg_0137 matched`, và `structured_output.json` có context `error_recovery`.

- [ ] **Step 7: Commit**

```bash
chmod +x application/tasks/chat_vita-drive-error-recovery/tests/test.sh
git add application/tasks/chat_vita-drive-error-recovery/tests/ tests/unit/application/test_vita_case_scoring.py
git commit -m "feat(vita): verifier chấm quyết định, tool call và toàn vẹn case"
```

---

## Task B4: Sinh job recipe persona × case

**Files:**
- Modify: `application/scripts/generate_application_job.py`
- Test: `tests/unit/application/test_generate_case_job.py`

**Interfaces:**
- Consumes: `input/cases.jsonl` (Task A3)
- Produces: `build_case_agent_entries(persona_paths: list[str], case_ids: list[str], model_name: str) -> list[dict]`

- [ ] **Step 1: Viết test thất bại**

```python
# tests/unit/application/test_generate_case_job.py
from application.scripts.generate_application_job import build_case_agent_entries


def test_produces_the_full_cross_product():
    entries = build_case_agent_entries(["p/a.yaml", "p/b.yaml"], ["vg_0001", "vg_0002"], "m")
    assert len(entries) == 4


def test_each_entry_carries_persona_and_case():
    entries = build_case_agent_entries(["p/a.yaml"], ["vg_0001"], "anthropic/claude-haiku-4-5")
    assert entries[0]["model_name"] == "anthropic/claude-haiku-4-5"
    assert entries[0]["kwargs"] == {"persona_path": "p/a.yaml", "case_id": "vg_0001"}


def test_case_varies_fastest_so_a_truncated_run_still_spans_personas():
    entries = build_case_agent_entries(["p/a.yaml", "p/b.yaml"], ["vg_0001", "vg_0002"], "m")
    assert [e["kwargs"]["persona_path"] for e in entries] == ["p/a.yaml", "p/a.yaml", "p/b.yaml", "p/b.yaml"]
    assert [e["kwargs"]["case_id"] for e in entries] == ["vg_0001", "vg_0002", "vg_0001", "vg_0002"]


def test_empty_inputs_produce_no_entries():
    assert build_case_agent_entries([], ["vg_0001"], "m") == []
    assert build_case_agent_entries(["p/a.yaml"], [], "m") == []
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `uv run pytest tests/unit/application/test_generate_case_job.py -v`
Expected: FAIL — `ImportError: cannot import name 'build_case_agent_entries'`

- [ ] **Step 3: Thêm hàm vào generator**

```python
def build_case_agent_entries(
    persona_paths: list[str], case_ids: list[str], model_name: str
) -> list[dict]:
    """Build one ``agents[]`` entry per persona x case pair.

    Case varies fastest so that stopping a run early still covers every persona.
    """
    return [
        {
            "name": "persona-claude-code",
            "model_name": model_name,
            "kwargs": {"persona_path": persona_path, "case_id": case_id},
        }
        for persona_path in persona_paths
        for case_id in case_ids
    ]
```

- [ ] **Step 4: Chạy test**

Run: `uv run pytest tests/unit/application/test_generate_case_job.py -v`
Expected: PASS, 4 test.

- [ ] **Step 5: Commit**

```bash
git add application/scripts/generate_application_job.py tests/unit/application/test_generate_case_job.py
git commit -m "feat(vita): sinh job recipe theo tích persona x case"
```

---

## Task B5: Smoke run — cửa chặn

**Files:**
- Create: `configs/jobs/application-task-job-recipe/appSim-vita-error-recovery-smoke-8b.yaml`
- Create: `configs/jobs/application-task-job-recipe/appSim-vita-error-recovery-smoke-baseline.yaml`

**Interfaces:**
- Consumes: mọi thứ ở trên

Đây là cửa chặn, **không phải bước hình thức**. Không sinh recipe đầy đủ 364 × 3–5 persona trước khi bước này cho số liệu.

- [ ] **Step 1: Chọn 20 case phủ đủ 10 nhóm lỗi**

```bash
uv run python - <<'PY'
import json, collections, itertools
path = "application/tasks/chat_vita-drive-error-recovery/input/cases.jsonl"
cases = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
by_type = collections.defaultdict(list)
for c in cases:
    by_type[c["error_type"]].append(c["case_id"])
picked = list(itertools.chain.from_iterable(sorted(v)[:2] for _, v in sorted(by_type.items())))
print(json.dumps(picked, indent=2))
PY
```
Expected: 20 case_id, hai case cho mỗi nhóm trong 10 nhóm lỗi.

- [ ] **Step 2: Sinh hai recipe, cùng persona cùng case, khác model**

Recipe `-8b` đặt `model_name` là model 8B; recipe `-baseline` đặt `anthropic/claude-haiku-4-5`. Cùng một `persona_path` và cùng 20 `case_id` ở cả hai, để hiệu số giữa hai lượt chỉ đến từ model.

- [ ] **Step 3: Chạy cả hai**

```bash
uv run python application/scripts/report_job.py --job appSim-vita-error-recovery-smoke-8b
uv run python application/scripts/report_job.py --job appSim-vita-error-recovery-smoke-baseline
```

- [ ] **Step 4: Đọc ba con số trước khi đi tiếp**

| Chỉ số | Ngưỡng | Nếu không đạt |
|---|---|---|
| `case_run.json` sinh ra ở mọi trial | 20/20 | Lỗi gán case, quay lại Task A8 |
| `decision_source = unavailable` | thấp | SUT không trả `decision` — cần nhánh LLM-judge trước khi chạy đầy đủ |
| `case_integrity = violated` của 8B | so với baseline | Xem bảng dưới |

`case_integrity` phải đọc **tách riêng cho `omit_detail` và `preserve_invalid_value`**, và tách riêng theo model. Nếu 8B vi phạm cao hơn baseline đáng kể, chọn theo thứ tự ưu tiên trong spec mục 13: phân hoá chính sách paraphrase theo `input_constraint` trước, rồi mới tính tới dùng model mạnh hơn cho 152 case bị ràng buộc.

- [ ] **Step 5: Commit recipe và ghi lại số liệu**

```bash
git add configs/jobs/application-task-job-recipe/appSim-vita-error-recovery-smoke-*.yaml
git commit -m "feat(vita): recipe smoke run đối chiếu persona 8B với baseline"
```

---

## Sau giai đoạn B

Chỉ khi Step 4 của Task B5 đạt: sinh recipe đầy đủ 364 × 3–5 persona và chạy. Sau đó chuyển sang giai đoạn C (task 3, dùng lại `sessionBody`) theo spec mục 15.
