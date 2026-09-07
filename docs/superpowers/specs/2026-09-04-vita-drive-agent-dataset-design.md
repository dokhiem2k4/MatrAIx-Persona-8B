# Vita Drive Agent multi-turn dataset (VN-Drives, 3 personas)

Date: 2026-09-04

## Goal

Produce the same three-file dataset as `data/vita-*-3p9i.*`, but driven by the
VN-Drives persona pool against the deployed Vita agent, whose address and
app password come from the environment rather than this file.

Outputs:

| File | Shape |
| --- | --- |
| `data/vita-drive-agent-stimuli-3p9i.csv` | ~828 rows, 13 columns — one stimulus per persona x grid cell |
| `data/vita-drive-agent-results-3p9i.csv` | 138 rows, 21 columns — one conversation per row, with ratings |
| `data/vita-drive-agent-results-3p9i.jsonl` | 138 records — same fields plus the full `messages` transcript |

## Why stage 1 has to run again

`data/vita-stimuli-3p9i.csv` was produced by three `matraix-persona-1m`
personas (`wiki-9f3c655902f2`, `wiki-62c08cb727c5`, `wiki-62706e3ac3c2`).
Each stimulus row carries the `persona_id` that wrote it, and stage 2 binds the
conversation to that persona. Reusing those rows would produce a wiki-persona
dataset wearing a VN-Drives label, so the utterance surveys are re-run with
VN-Drives personas.

## Persona selection

Three personas drawn once from the 42 in `persona/datasets/vn-drivers/` using
`random.Random(20260904).sample(...)` over the sorted id list, then written
literally into the job recipes:

- `vn-drv-017`
- `vn-drv-026`
- `vn-drv-041`

Random at selection time, fixed thereafter. The rest of this pipeline is
deliberately deterministic — `generate_vita_multiturn_job.py` interleaves
personas rather than shuffling precisely so a given dataset always yields the
same job — and leaving an RNG inside the recipe would break that.

## Pipeline

### Stage 1 — stimuli (no traffic to the Vita server)

```
uv run python scripts/generate_vita_stage1_jobs.py \
    --persona vn-drv-017 --persona vn-drv-026 --persona vn-drv-041 \
    --job-prefix vita-drive-agent-s1 --out-dir configs/jobs/vita-drive-agent-stage1
uv run matraix run -c configs/jobs/vita-drive-agent-stage1/<each>.yaml
```

Nine recipes, one per `survey_vita-utterance-*` intent, three trials each — 27
stage-1 trials. `persona-json-survey` on
`openrouter/google/gemini-3.5-flash-lite`. These are survey tasks: the persona
writes `scenario` + `first_input` for every cell of the intent grid. Nothing
reaches the application under test.

### Stage 1b — merge

```
uv run python scripts/merge_vita_datasets.py jobs/vita-drive-agent-s1-* \
    -o data/vita-drive-agent-stimuli-3p9i.csv
```

Expected ~828 rows (3 personas x 276), matching the 3p9i reference set.

### Stage 2 — conversations against the live endpoint

```
uv run python scripts/generate_vita_multiturn_job.py \
    data/vita-drive-agent-stimuli-3p9i.csv \
    --task application/tasks/chat_vita-drive-agent \
    --job-name vita-drive-agent-3p9i --per-subintent 3 \
    -o configs/jobs/application-task-job-recipe/vita-drive-agent-3p9i.yaml
```

`--per-subintent 3` over 46 subintents yields 138 trials, the same cap the
reference run used. Each agent entry carries `kwargs.seed` = the stimulus row,
so the conversation opens on a fixed need instead of one the persona invents.

Run environment:

```
MATRIX_CHATBOT_TASK_PATH=application/tasks/chat_vita-drive-agent
VITA_ASSISTANT_API_URL=<deployment host>
VITA_APP_PASSWORD=<deployment app password>
OPENROUTER_API_KEY=<from application/playground/.env.local>
```

`application/tasks/chat_vita-drive-agent/input/chatbot.yaml` reads the URL from
`VITA_ASSISTANT_API_URL`, authenticates with header
`x-app-password: ${VITA_APP_PASSWORD}`, and POSTs to `/api/agent/chat` with a
6-turn ceiling.

### Stage 3 — export

```
uv run python scripts/export_vita_multiturn_results.py jobs/vita-drive-agent-3p9i \
    -o data/vita-drive-agent-results-3p9i
```

Writes the CSV and the JSONL, then prints rating distributions by intent and by
persona. Trials with incomplete artifacts are dropped and named rather than
counted as zeros.

## Risk and how it is handled

The only differences from the working 3p9i run are the task
(`chat_vita-drive-agent` instead of `chat_vita-drive-assistant`) and a live
remote endpoint instead of localhost. Job `vn-drv-chat-agent-v3` already ran
that exact combination — 3/3 completed, reward 1.0, $0.021 — so the
combination is known good, but credentials and deployments drift.

Mitigation: run a single seeded trial end to end and confirm its
`transcript.json`, `application_result.json` and `user_feedback.json` before
launching the remaining 137. A failure at trial 1 costs seconds; the same
failure at trial 90 costs the run.

Concurrency is held at 6 so the deployed server is not hammered.

## Expected cost and duration

Measured from the jobs in this repo that have the same shape, not estimated:

| Stage | Reference jobs | Trials | Wall clock | Cost |
| --- | --- | --- | --- | --- |
| 1 | `jobs/vita-s1lite-*` (9 intents x 3 personas) | 27 | 4.7 min | $0.303 |
| 2 | `jobs/vita-full-3p9i` (concurrency 6) | 138 | 26m50s | $0.905 |
| | | **165** | **~32 min** | **$1.21** |

Two adjustments for this run:

- Stage 2 calls an HTTPS endpoint instead of localhost. Per-trial cost is
  unchanged — `vn-drv-chat-agent-v3` hit that same endpoint at $0.007/trial,
  matching $0.905/138 = $0.0066 — but network latency may stretch wall clock,
  so budget 30-40 minutes for stage 2.
- The smoke trial adds about $0.01.

Total: roughly **$1.2 and 35-45 minutes**. The cost is OpenRouter usage for
`gemini-3.5-flash-lite` playing the personas; the Vita server itself is free.

## Not in scope

- No changes to `chat_vita-drive-agent` or to any script; every step uses the
  existing tooling as-is.
- The existing `data/vita-*-3p9i.*` files are left untouched.
