"""Convert the Vita golden single-turn workbook into ``cases.jsonl``.

Run offline; the source workbook is not committed to the repository:

    uv run --with openpyxl python application/scripts/convert_vita_golden_dataset.py \
        --source "/path/to/golden_singleturn_cover intent_happy&fallback.xlsx" \
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

CASE_TYPE_CODES = {"happy": "happy", "unhappy": "unhappy"}

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
    calls: list[dict[str, Any]] = []
    for entry in parsed:
        if not isinstance(entry, dict):
            raise ConversionError("every tool call must be a JSON object")
        # Two golden rows spell the call as action/parameters instead of
        # key/params. Same meaning, different wording, so normalize rather than
        # reject -- the module+key requirement below still holds.
        module = _text(entry.get("module"))
        key = _text(entry.get("key")) or _text(entry.get("action"))
        if not module or not key:
            raise ConversionError("every tool call needs a non-empty module and key")
        params = entry.get("params")
        if params is None:
            params = entry.get("parameters")
        calls.append({"module": module, "key": key, "params": params or {}})
    return calls


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
        "case_type": _lookup(CASE_TYPE_CODES, row.get("case_type"), "case_type"),
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
        for label, (code, parent) in sorted(
            SUBINTENT_BY_LABEL_VI.items(), key=lambda item: item[1][0]
        )
    }
    (args.out_dir / "intent_taxonomy.json").write_text(
        json.dumps(taxonomy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("wrote {} cases to {}".format(len(records), cases_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
