#!/usr/bin/env bash
# Two-stage persona evaluation of a Vita chat task, end to end.
#
#   stage 1  nine utterance surveys  -> one stimulus workbook
#   stage 2  each stimulus replayed  -> one multi-turn conversation per row
#   export   three workbooks keyed by --slug
#
# Stage 1 depends only on the persona pool, not on --task: the stimuli are what
# a driver would say, which does not change with the application answering. So
# --reuse-stimuli points a second task at an existing workbook and evaluates a
# different application against the identical stimulus set -- the only way a
# comparison between two tasks means anything.
#
# Every step that spends money is preceded by a guard. A dead endpoint or an
# empty merge stops the run instead of buying failures.
#
# Usage:
#   scripts/run_vita_pipeline.sh --slug lab3p \
#       --task application/tasks/chat_vita-drive-assistant \
#       --endpoint https://<deployment-host> \
#       --persona vn-drv-055 --persona vn-drv-032 --persona vn-drv-015
#
#   # same stimuli, different application under test
#   scripts/run_vita_pipeline.sh --slug agent3p \
#       --task application/tasks/chat_vita-drive-agent \
#       --reuse-stimuli data/vita-stimuli-lab3p.csv
set -u
cd "$(dirname "$0")/.."

SLUG=""
TASK="application/tasks/chat_vita-drive-assistant"
ENDPOINT="${VITA_ASSISTANT_API_URL:-http://127.0.0.1:3001}"
POOL="vn-drivers"
PER_SUBINTENT=3
REUSE_STIMULI=""
PERSONAS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --slug)           SLUG="$2"; shift 2 ;;
    --task)           TASK="$2"; shift 2 ;;
    --endpoint)       ENDPOINT="$2"; shift 2 ;;
    --persona)        PERSONAS+=("$2"); shift 2 ;;
    --persona-pool)   POOL="$2"; shift 2 ;;
    --per-subintent)  PER_SUBINTENT="$2"; shift 2 ;;
    --reuse-stimuli)  REUSE_STIMULI="$2"; shift 2 ;;
    -h|--help)        sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "unknown flag: $1"; exit 2 ;;
  esac
done

[ -n "${SLUG}" ] || { echo "ABORT: --slug is required (names the jobs and the workbooks)"; exit 2; }
[ -d "${TASK}" ] || { echo "ABORT: --task ${TASK} is not a directory"; exit 2; }
if [ -z "${REUSE_STIMULI}" ] && [ ${#PERSONAS[@]} -eq 0 ]; then
  echo "ABORT: give --persona at least once, or --reuse-stimuli to skip stage 1"; exit 2
fi

set -a; source application/playground/.env.local; set +a
export VITA_ASSISTANT_API_URL="${ENDPOINT}"
export VITA_APP_PASSWORD="${VITA_APP_PASSWORD:-}"

STIMULI="data/vita-stimuli-${SLUG}.csv"
RECIPE="configs/jobs/vita-${SLUG}/vita-${SLUG}-s2.yaml"
S2_JOB="jobs/vita-${SLUG}-s2"

echo "### task     : ${TASK}"
echo "### endpoint : ${ENDPOINT}"
echo "### slug     : ${SLUG}"

# --- guard: the endpoint must answer before anything is generated ------------
echo "### probing the endpoint"
probe=$(curl -sk -o /dev/null -w "%{http_code}" -X POST "${ENDPOINT}/api/chat" \
  -H "Content-Type: application/json" \
  -H "x-app-password: ${VITA_APP_PASSWORD}" \
  -H "x-vehicle-session: pipeline-probe" \
  -d '{"sessionId":"pipeline-probe","message":"Vita ơi, pin còn bao nhiêu?","drivingContext":"driving","intent":"vehicle_control"}' \
  --max-time 60 || echo "000")
if [ "${probe}" != "200" ]; then
  echo "ABORT: endpoint answered ${probe}, not 200. Nothing was spent."
  echo "       A 400 wrapping 'Agent service request failed (500)' means the"
  echo "       application's own LLM key is out of credit -- fix that first."
  exit 1
fi
echo "### endpoint healthy"

# --- stage 1 ----------------------------------------------------------------
if [ -n "${REUSE_STIMULI}" ]; then
  [ -f "${REUSE_STIMULI}" ] || { echo "ABORT: --reuse-stimuli ${REUSE_STIMULI} not found"; exit 1; }
  STIMULI="${REUSE_STIMULI}"
  echo "### stage 1 skipped, reusing ${STIMULI}"
else
  echo "### stage 1: generating recipes"
  uv run python scripts/generate_vita_stage1_jobs.py \
    "${PERSONAS[@]/#/--persona=}" \
    --persona-pool "${POOL}" \
    --out-dir "configs/jobs/vita-${SLUG}" \
    --job-prefix "vita-${SLUG}-s1" || exit 1

  for cfg in configs/jobs/vita-${SLUG}/vita-${SLUG}-s1-*.yaml; do
    intent=$(basename "${cfg}" .yaml | sed "s/^vita-${SLUG}-s1-//")
    export MATRIX_SURVEY_TASK_PATH="application/tasks/survey_vita-utterance-${intent}"
    echo "### stage 1: ${intent}"
    uv run matraix run -c "${cfg}" 2>&1 | tail -3
  done

  echo "### merging stimuli -> ${STIMULI}"
  uv run python scripts/merge_vita_datasets.py jobs/vita-${SLUG}-s1-* -o "${STIMULI}" || exit 1
fi

rows=$(uv run python -c "
import csv
print(sum(1 for _ in csv.DictReader(open('${STIMULI}', encoding='utf-8-sig'))))
")
echo "### stimuli rows: ${rows}"
[ "${rows}" -ge 100 ] || { echo "ABORT: only ${rows} usable rows. Not spending on stage 2."; exit 1; }

# --- stage 2 ----------------------------------------------------------------
echo "### stage 2: generating recipe for ${TASK}"
uv run python scripts/generate_vita_multiturn_job.py "${STIMULI}" \
  -o "${RECIPE}" \
  --job-name "vita-${SLUG}-s2" \
  --task "${TASK}" \
  --persona-pool "${POOL}" \
  --per-subintent "${PER_SUBINTENT}" || exit 1

trials=$(uv run python -c "
import yaml
print(len(yaml.safe_load(open('${RECIPE}', encoding='utf-8'))['agents']))
")
echo "### stage 2 trials: ${trials}"

export MATRIX_CHATBOT_TASK_PATH="${TASK}"
uv run matraix run -c "${RECIPE}" 2>&1 | tail -25

# --- export -----------------------------------------------------------------
echo "### exporting"
uv run python scripts/export_vita_multiturn_results.py "${S2_JOB}" \
  -o "data/vita-results-${SLUG}" 2>&1 | tail -20

echo "### done"
ls -la "${STIMULI}" "data/vita-results-${SLUG}.csv" "data/vita-results-${SLUG}.jsonl" 2>/dev/null
