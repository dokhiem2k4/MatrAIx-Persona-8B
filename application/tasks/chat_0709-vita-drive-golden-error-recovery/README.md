# chat_0709-vita-drive-golden-error-recovery

Đo khả năng xử lý và báo lỗi của Vita Drive Assistant trên bộ golden single-turn
364 case (happy + fallback).

**Trial = 1 persona × 1 case.** Case gán qua `agents[].kwargs.case_id` trong job
recipe; runner phát `case_run.json` gộp case và quan sát để verifier tự chứa.

- `input/cases.jsonl` — 364 case, sinh bằng `application/scripts/convert_vita_golden_dataset.py`
- `input/intent_taxonomy.json` — 60 mã subintent và nhãn hiển thị tiếng Việt
- `input/chatbot.yaml` — `sessionBody` bơm state của case vào request; `structuredExposure` lấy `decision` và `toolCalls` từ SUT

Verifier chấm ba tầng: `decision_match`, `tool_call_match`, `case_integrity`.
Con số đáng tin là con số đã lọc theo `case_integrity` — xem
`docs/superpowers/specs/2026-09-07-vita-three-task-program-design.md` mục 9.

Nguồn dataset nằm ngoài repo và không được commit.
