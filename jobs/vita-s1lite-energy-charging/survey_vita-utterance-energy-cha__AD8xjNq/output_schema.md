Platform-derived answer envelope (from `questionnaire.yaml`).

```json
{
  "instrument": {"id": "vita_utterance_energy_charging", "title": "Vita — bối cảnh & câu mở đầu (energy_charging)"},
  "answers": [
    {
      "questionId": "q0",
      "value": "<answer value>"
    }
  ]
}
```

Use exact `questionId` values from the questionnaire.
For choice questions, `value` must be the exact choice id (or list of ids for multi-select).
Default surveys emit `questionId` + `value` only (choice / likert / bool).