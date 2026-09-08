# survey_vita-utterance-offline-degraded-mode

Bước 1 của pipeline Vita: persona diễn đạt lại các câu lệnh mẫu theo giọng riêng.

- **Nguồn**: `Dataset - Vita Demo`, intent `offline_degraded_mode`
- **Số seed**: 24 (4 subintent)
- **Sinh ra**: 24 câu / persona

`input/seed_index.json` map `questionId` -> ô gốc trong lưới
(intent / subintent / vehicle_state / assistant_mode) để bước 2 ghép lại được.

Sinh lại task này:

```bash
uv run python scripts/generate_vita_utterance_tasks.py \
  application/vita-intent-bank/intent_bank.json \
  --intent offline_degraded_mode --force
```
