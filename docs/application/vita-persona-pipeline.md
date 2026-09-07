# Vita persona pipeline

Scoring a Vita application with simulated Vietnamese drivers, end to end.
One command; **swap `--task` and the results follow that task.**

```bash
scripts/run_vita_pipeline.sh --slug lab3p \
    --task application/tasks/chat_vita-drive-assistant \
    --endpoint https://<host> \
    --persona vn-drv-055 --persona vn-drv-032 --persona vn-drv-015
```

Set `VITA_APP_PASSWORD` first if the deployment is password-gated.

## What runs

| Stage | What happens | Depends on `--task`? |
|-------|--------------|----------------------|
| 1 | Nine `survey_vita-utterance-*` tasks ask each persona what they would say in every cell of an intent grid | **No** |
| 2 | Each stimulus row opens one multi-turn conversation against the application | **Yes** |
| export | Three workbooks keyed by `--slug` | — |

Stage 1 is the part that surprises people: the stimuli are *what a driver would
say*, which does not change with the application answering them. Only stage 2
talks to `--task`.

## Comparing two applications

Because stage 1 is task-independent, `--reuse-stimuli` points a second task at a
workbook that already exists:

```bash
scripts/run_vita_pipeline.sh --slug agent3p \
    --task application/tasks/chat_vita-drive-agent \
    --reuse-stimuli data/vita-stimuli-lab3p.csv
```

Both runs now answer the **identical** stimulus set, so a rating difference
between them is a difference between the applications. Regenerating stage 1 per
task would confound the two — a lower score could just mean that task drew
harder questions.

## Outputs

| File | One row per | Notes |
|------|-------------|-------|
| `data/vita-stimuli-<slug>.csv` | stimulus (~828 for 3 personas × 9 intents) | the full set, not only the rows stage 2 sampled |
| `data/vita-results-<slug>.csv` | conversation | scores, joined to the stimulus that caused them |
| `data/vita-results-<slug>.jsonl` | conversation | same, with the transcript |

Both workbooks carry **`persona_profile`**: one readable line of age, urbanicity,
patience, skepticism, trust, and attitude to EVs. A rating is only interpretable
next to the person who gave it — a 4/10 from a high-skepticism driver is a
different signal than a 4 from a trusting one. `scripts/persona_profile.py`
builds it, and renders **only dimensions the persona actually answered**; a
value sampled from the synthesis graph would read as a fact about a person when
it is a draw from a distribution.

## Sizing the run

`--per-subintent N` caps stage 2 at N conversations per subintent. There are 46
subintents, so the default `3` yields **138 conversations** out of ~828 stimuli.
Raising it multiplies stage-2 cost roughly linearly — running all 828 rows costs
about six times as much as 138 for the same three personas.

Measured on `gemini-3.1-flash-lite` via the Google endpoint:

| | Cost |
|---|---:|
| Stage 1, 27 trials | ~$0.22 |
| Stage 2, per conversation | ~$0.008 |
| Stage 2, 138 conversations | ~$1.10 |

Not included: what the **application under test** spends answering. 138
conversations of 4+ turns is 550+ calls on its own LLM key, billed to whoever
runs the deployment.

## Which persona pool

`--persona-pool vn-drivers-forum` (42 personas) is the grounded Vietnamese driver
set. Pick ids from `persona/datasets/vn-drivers-forum/persona_*.yaml`. Sample
them with a fixed seed if the choice must be reproducible from the repo alone.

## When it fails

The guards abort **before** spending, so a failed precondition costs nothing.

| Symptom | Cause | Fix |
|---------|-------|-----|
| `endpoint answered 400, not 200` and the body wraps `Agent service request failed (500)` | The application's own LLM key is out of credit. `/api/health` still returns `ok:true` — it is a shallow check that never touches the LLM | Top up the deployment's key |
| `402 in_flight_budget_exhausted` in trial results | **Our** persona-side key is out of credit | Top up, or point `OPENROUTER_API_BASE` at the Google endpoint |
| `only N usable rows` | Stage 1 returned little; usually a persona-side key or model-id problem | Check `MATRIX_PERSONA_MODEL` matches whatever `OPENROUTER_API_BASE` points at |

A bulk stage-2 failure is almost never about the conversations themselves. Read
one `result.json` before assuming otherwise — the exception message carries the
endpoint's own words.

### Rerunning only what failed

Do not rerun the whole recipe; that re-buys the conversations that already
succeeded.

```bash
uv run python scripts/build_vita_retry_job.py jobs/vita-<slug>-s2 \
    --recipe configs/jobs/vita-<slug>/vita-<slug>-s2.yaml \
    -o configs/jobs/vita-<slug>/vita-<slug>-s2-retry.yaml
```

It selects by `row_id` — the stimulus a trial replays — because trial directory
names are minted fresh per run and say nothing about which stimulus went
unanswered.
