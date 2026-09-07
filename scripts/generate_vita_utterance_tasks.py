#!/usr/bin/env python3
"""Generate step-1 (utterance generation) survey tasks from the Vita intent bank.

Step 1 of the two-step pipeline: instead of replaying the 276 seed utterances
verbatim, each persona rephrases every seed in their own voice. One task is
emitted per ``intent_code`` so a single job recipe can cover the whole bank
while each trial stays a reasonably sized questionnaire (24-42 questions).

The generated tasks reuse the stock survey verifier — it treats ``free_text``
answers as textual facets, so each persona utterance flows straight into
``structured_output.json`` and then into the job aggregation.

Usage:
    uv run python scripts/generate_vita_utterance_tasks.py \
        application/vita-intent-bank/intent_bank.json \
        --intent journey_navigation_places        # omit to emit every intent
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / "application" / "tasks"
# The stock survey verifier is task-agnostic; copy it rather than fork it.
VERIFIER_SOURCE = TASKS_DIR / "example-survey_product-feedback" / "tests"
VERIFIER_FILES = ("test.sh", "test_state.py", "verifier_env.sh")

STATE_LABELS = {"driving": "xe đang chạy trên đường", "parking": "xe đang đỗ"}
MODE_LABELS = {
    "quiet": "trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)",
    "balance": "trợ lý ở chế độ Cân bằng",
    "proactive": "trợ lý ở chế độ Chủ động (hay gợi ý thêm)",
}


def slug(intent_code: str) -> str:
    return intent_code.replace("_", "-")


def _scenario_prompt(subintent: dict[str, Any], seed: dict[str, Any]) -> str:
    state = STATE_LABELS.get(seed["vehicle_state"], seed["vehicle_state"])
    mode = MODE_LABELS.get(seed["assistant_mode"], seed["assistant_mode"])
    return (
        f"[Tình huống: {state}, {mode}]\n"
        f"Bạn đang muốn: {subintent['subintent_name']}.\n"
        f'Tham khảo — một người dùng khác đã nói: "{seed["input"]}"\n\n'
        "Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, "
        "vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra "
        "sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.\n"
        "Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT."
    )


def _first_input_prompt(subintent: dict[str, Any], seed: dict[str, Any]) -> str:
    state = STATE_LABELS.get(seed["vehicle_state"], seed["vehicle_state"])
    mode = MODE_LABELS.get(seed["assistant_mode"], seed["assistant_mode"])
    return (
        f"[Tình huống: {state}, {mode}]\n"
        f"Bạn đang muốn: {subintent['subintent_name']}.\n"
        f'Tham khảo — một người dùng khác đã nói: "{seed["input"]}"\n\n'
        "Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra "
        "với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của "
        "chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.\n"
        "Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT."
    )


# Each seed yields two free_text questions: the scenario, then its opening line.
FIELDS = (("scenario", _scenario_prompt), ("first_input", _first_input_prompt))


def build_questionnaire(intent: dict[str, Any]) -> dict[str, Any]:
    """Two free_text questions per seed; `construct` carries the subintent."""
    questions: list[dict[str, Any]] = []
    index = 0
    for subintent in intent["subintents"]:
        for seed in subintent["seeds"]:
            for field, render in FIELDS:
                questions.append(
                    {
                        "id": f"q{index}",
                        "prompt": render(subintent, seed),
                        "type": "free_text",
                        "construct": f"{subintent['subintent_code']}__{field}",
                        "required": True,
                    }
                )
                index += 1

    return {
        "schemaVersion": "1.0",
        "id": f"vita_utterance_{intent['intent_code']}",
        "title": f"Vita — bối cảnh & câu mở đầu ({intent['intent_code']})",
        "description": (
            "Với mỗi tình huống dùng trợ lý xe VinFast VF9, persona tự dựng bối "
            "cảnh của mình rồi viết câu đầu tiên mở đầu hội thoại."
        ),
        "questions": questions,
    }


def seed_index(intent: dict[str, Any]) -> list[dict[str, Any]]:
    """Sidecar map so the exporter can pivot answers back onto the grid."""
    rows: list[dict[str, Any]] = []
    index = 0
    for subintent in intent["subintents"]:
        for seed in subintent["seeds"]:
            for field, _ in FIELDS:
                rows.append(
                    {
                        "questionId": f"q{index}",
                        "field": field,
                        "intent_code": intent["intent_code"],
                        "subintent_code": subintent["subintent_code"],
                        "subintent_name": subintent["subintent_name"],
                        "seed_input": seed["input"],
                        "vehicle_state": seed["vehicle_state"],
                        "assistant_mode": seed["assistant_mode"],
                    }
                )
                index += 1
    return rows


CONTEXT_MD = """\
# Bối cảnh — Trợ lý xe thông minh Vita (VinFast VF9)

> **NGÔN NGỮ: TIẾNG VIỆT.** Mọi câu trả lời phải viết bằng tiếng Việt, kể cả
> khi tiếng mẹ đẻ của bạn là ngôn ngữ khác. Bạn đang ở Việt Nam và chiếc xe
> này chỉ hiểu tiếng Việt — đây là ràng buộc của tình huống, không phải lựa
> chọn. Giữ nguyên tính cách, thói quen và cách nói của bạn, nhưng diễn đạt
> chúng bằng tiếng Việt.

Bạn là chủ/người lái một chiếc VinFast VF9 2026 tại Việt Nam. Xe có trợ lý
giọng nói tên **Vita**, nghe và thực hiện lệnh khi bạn đang lái hoặc đang đỗ.

Vita xử lý các nhóm việc: dẫn đường và tìm địa điểm, sạc pin và quãng đường
còn lại, điều khiển khoang lái (điều hòa, ghế, cửa, đèn), gọi điện và nhắn tin,
phát nhạc, lịch và nhắc việc, tra cứu thông tin xe, hỏi đáp chung.

## Việc của bạn

Mỗi câu hỏi cho bạn xem **một câu lệnh mẫu** mà người khác đã nói với Vita.
Hãy viết lại câu đó theo cách **bạn** sẽ nói.

Giữ nguyên:
- **Ý định** — bạn muốn Vita làm đúng việc đó
- **Tình huống** — xe đang chạy hay đang đỗ (khi đang lái, người ta thường nói
  ngắn hơn)

Thay đổi theo đúng con người bạn:
- Cách xưng hô (tôi / mình / anh / em / con...) và cách gọi trợ lý
- Mức độ lịch sự, có "làm ơn"/"giúp tôi"/"nhé" hay không
- Độ dài: có người nói cộc lốc, có người nói cả câu đầy đủ
- Từ địa phương, cách dùng từ quen thuộc của bạn

Đừng cố viết cho hay hoặc cho đúng ngữ pháp sách vở. Viết đúng như bạn nói
hằng ngày trong xe.
"""

INSTRUCTION_MD = """\
# Dựng bối cảnh & câu mở đầu cho trợ lý xe Vita

Đọc `input/context.md` để nắm bối cảnh, rồi trả lời toàn bộ bảng hỏi.

Bảng hỏi đi theo **từng cặp**. Với mỗi tình huống bạn trả lời hai câu hỏi liền
nhau:

1. **Bối cảnh** — chuyện gì đang xảy ra với *bạn*: đi đâu, vì việc gì, vội hay
   thong thả, có ai trên xe, tâm trạng thế nào. 1–2 câu, ngôi thứ nhất.
2. **Câu mở đầu** — đúng một câu bạn nói ra với Vita để bắt đầu hội thoại,
   khớp với bối cảnh bạn vừa dựng.

Câu mở đầu này sẽ được dùng để khởi động một cuộc hội thoại nhiều lượt, nên nó
phải tự nhiên như lời nói thật, không phải câu lệnh mẫu.

Yêu cầu cho mỗi câu trả lời:
- **VIẾT BẰNG TIẾNG VIỆT.** Bắt buộc, không có ngoại lệ. Kể cả khi tiếng mẹ đẻ
  của bạn là tiếng Anh, Tây Ban Nha, Thổ Nhĩ Kỳ hay bất kỳ thứ tiếng nào khác —
  chiếc xe này chỉ hiểu tiếng Việt. Tính cách của bạn thể hiện qua *cách* bạn
  dùng tiếng Việt (xưng hô, lịch sự, dài ngắn), không phải qua việc đổi ngôn ngữ.
- Viết **đúng một câu** — thứ bạn sẽ thực sự nói ra thành tiếng trong xe
- **Không** thêm lời giải thích, không đặt trong ngoặc kép, không đánh số
- Không lặp lại nguyên văn câu mẫu, trừ khi bạn thật sự sẽ nói y hệt như vậy

Ghi kết quả vào `/app/output/survey_result.json` theo đúng định dạng bảng hỏi.
"""


def write_task(intent: dict[str, Any], sample_size: int, force: bool) -> Path:
    name = f"survey_vita-utterance-{slug(intent['intent_code'])}"
    task_dir = TASKS_DIR / name
    if task_dir.exists() and not force:
        raise SystemExit(f"{task_dir} already exists (pass --force to overwrite)")

    (task_dir / "input").mkdir(parents=True, exist_ok=True)
    (task_dir / "tests").mkdir(parents=True, exist_ok=True)

    seed_count = sum(len(s["seeds"]) for s in intent["subintents"])

    (task_dir / "task.toml").write_text(
        f'''version = "1.0"
artifacts = [ "/app/output",]

[task]
name = "application/vita-utterance-{slug(intent["intent_code"])}"

[metadata]
difficulty = "easy"
type = "survey"
domain = "automotive-ai"
tags = [ "vita drive", "vf9", "utterance generation", "{intent["intent_code"]}",]

[verifier]
timeout_sec = 120.0

[agent]
timeout_sec = 900.0

[environment]
definition = "application/shared-survey-form"
build_timeout_sec = 600.0
cpus = 1
memory_mb = 2048
storage_mb = 10240
gpus = 0
''',
        encoding="utf-8",
    )

    (task_dir / "instruction.md").write_text(INSTRUCTION_MD, encoding="utf-8")
    (task_dir / "input" / "context.md").write_text(CONTEXT_MD, encoding="utf-8")

    import yaml  # local import: only needed when actually emitting a task

    (task_dir / "input" / "questionnaire.yaml").write_text(
        yaml.safe_dump(
            build_questionnaire(intent),
            allow_unicode=True,
            sort_keys=False,
            width=100,
        ),
        encoding="utf-8",
    )

    (task_dir / "input" / "seed_index.json").write_text(
        json.dumps(seed_index(intent), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    (task_dir / "persona_strategy.json").write_text(
        json.dumps(
            {
                "schemaVersion": "1.0",
                "sources": [],
                "dimensionFilters": {},
                "sampling": {"mode": "random", "sampleSize": sample_size},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (task_dir / "reporting.json").write_text(
        json.dumps(
            {
                "schemaVersion": "1.0",
                "contextRules": [
                    {
                        "match": {"contextType": "trial_summary"},
                        "distributions": [
                            {
                                "id": "survey.summary.answer_count",
                                "facetKey": "answer_count",
                                "title": "Số câu đã sinh",
                            }
                        ],
                    }
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    for filename in VERIFIER_FILES:
        shutil.copy2(VERIFIER_SOURCE / filename, task_dir / "tests" / filename)
    (task_dir / "tests" / "test.sh").chmod(0o755)

    (task_dir / "README.md").write_text(
        f"""# {name}

Bước 1 của pipeline Vita: persona diễn đạt lại các câu lệnh mẫu theo giọng riêng.

- **Nguồn**: `Dataset - Vita Demo`, intent `{intent["intent_code"]}`
- **Số seed**: {seed_count} ({len(intent["subintents"])} subintent)
- **Sinh ra**: {seed_count} câu / persona

`input/seed_index.json` map `questionId` -> ô gốc trong lưới
(intent / subintent / vehicle_state / assistant_mode) để bước 2 ghép lại được.

Sinh lại task này:

```bash
uv run python scripts/generate_vita_utterance_tasks.py \\
  application/vita-intent-bank/intent_bank.json \\
  --intent {intent["intent_code"]} --force
```
""",
        encoding="utf-8",
    )
    return task_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bank", type=Path, help="path to intent_bank.json")
    parser.add_argument(
        "--intent",
        action="append",
        default=None,
        help="only emit this intent_code (repeatable); default is all",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=3,
        help="personas per task in persona_strategy.json (default 3, pilot size)",
    )
    parser.add_argument("--force", action="store_true", help="overwrite existing tasks")
    args = parser.parse_args()

    bank = json.loads(args.bank.read_text(encoding="utf-8"))
    intents = bank["intents"]
    if args.intent:
        wanted = set(args.intent)
        known = {i["intent_code"] for i in intents}
        unknown = wanted - known
        if unknown:
            raise SystemExit(
                f"unknown intent(s): {', '.join(sorted(unknown))}\n"
                f"available: {', '.join(sorted(known))}"
            )
        intents = [i for i in intents if i["intent_code"] in wanted]

    for intent in intents:
        path = write_task(intent, args.sample_size, args.force)
        count = sum(len(s["seeds"]) for s in intent["subintents"])
        rel = path.relative_to(REPO_ROOT)
        print(f"{rel}  ({count} câu/persona)")


if __name__ == "__main__":
    main()
