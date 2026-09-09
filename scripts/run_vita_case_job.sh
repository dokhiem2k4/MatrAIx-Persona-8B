#!/usr/bin/env bash
#
# Run one case-bound Vita job end to end, and leave the run's data files behind.
#
# Running the job and exporting it used to be two commands, and the second one
# was easy to forget -- the results then existed only as 128 folders of JSON
# under jobs/, which nobody reads. This does both, and creates the run folder
# up front so an in-flight run is visible on disk.
#
# The four MATRIX_CHATBOT_* variables are the other thing that used to be
# remembered by hand. Without MATRIX_CHATBOT_TASK_PATH the runtime silently
# ignores the task's chatbot.yaml and calls /v1/messages instead of /api/chat,
# so the whole run talks to the wrong endpoint and nobody notices.
#
# Usage:
#   scripts/run_vita_case_job.sh <task-slug> <run-name> [generator args...]
#
#   scripts/run_vita_case_job.sh chat_0709-vita-drive-golden-error-recovery \
#       golden-2p-128 \
#       --personas persona/datasets/vn-drivers/persona_vn-drv-001.yaml \
#                  persona/datasets/vn-drivers/persona_vn-drv-003.yaml \
#       --max-cases 64
#
# Re-run an earlier run's exact persona x case pairs, to compare before and
# after a fix. The task comes from the manifest, so any slug is accepted here:
#
#   scripts/run_vita_case_job.sh chat_0709-vita-drive-golden-error-recovery \
#       golden-2p-128-after \
#       --replay data/golden-2p-128/golden-2p-128-manifest.json

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

if [[ $# -lt 2 ]]; then
    sed -n '3,25p' "$0" >&2
    exit 2
fi

TASK_SLUG="$1"; shift
RUN_NAME="$1"; shift
TASK_PATH="application/tasks/${TASK_SLUG}"
DATA_DIR="data/${RUN_NAME}"

[[ -d "${TASK_PATH}" ]] || { echo "no such task: ${TASK_PATH}" >&2; exit 1; }
# Check before spending, not after: a name clash discovered at export time
# means the run already happened and its money is gone.
[[ -e "${DATA_DIR}" ]] && { echo "run folder exists: ${DATA_DIR}" >&2; exit 1; }

# Create it now so an in-flight run is visible on disk, and remove it on the
# way out if no results were written. A run that dies early -- the system under
# test returning 500 for every trial, say -- would otherwise leave a folder
# behind that blocks re-running under the same name. The recipe generator drops
# a manifest in here before the run starts, so "nothing was written" means
# "nothing but the manifest", and the manifest is reproducible from the recipe.
mkdir -p "${DATA_DIR}"
cleanup_empty_run_dir() {
    [[ -d "${DATA_DIR}" ]] || return 0
    if ! compgen -G "${DATA_DIR}/*-results.*" > /dev/null; then
        rm -f "${DATA_DIR}/${RUN_NAME}-manifest.json"
        rmdir "${DATA_DIR}" 2>/dev/null || true
    fi
}
trap cleanup_empty_run_dir EXIT

ENV_LOCAL="application/playground/.env.local"
if [[ -f "${ENV_LOCAL}" ]]; then
    set -a; source "${ENV_LOCAL}"; set +a
fi
# An OpenRouter key pointed at another vendor's endpoint 404s on every model
# that vendor does not host.
unset OPENROUTER_API_BASE OPENROUTER_BASE_URL

export PYTHONPATH=".:environment/runtime:packages/playground/src:application/playground"
export MATRIX_CHATBOT_TASK_PATH="${TASK_PATH}"
export MATRIX_CHATBOT_APPLICATION_ID="${MATRIX_CHATBOT_APPLICATION_ID:-vita_drive_assistant}"
export MATRIX_CHATBOT_DOMAIN="${MATRIX_CHATBOT_DOMAIN:-automotive_ai}"
# Read the turn budget from the task instead of defaulting: a 6-turn task run
# with maxTurns=2 would cut every conversation short and the coverage numbers
# would look like the assistant gave up.
TASK_MAX_TURNS="$(sed -n 's/^  maxTurns: *//p' "${TASK_PATH}/input/chatbot.yaml" | head -1)"
export MATRIX_CHATBOT_MAX_TURNS="${MATRIX_CHATBOT_MAX_TURNS:-${TASK_MAX_TURNS:-2}}"
# Render the persona profile in Vietnamese. The ids and values in the data stay
# English -- this only translates the prose the model reads, the same way the
# UI translates what a person reads. Every persona here is a Vietnamese driver
# talking to a Vietnamese assistant, so an English profile made the model
# translate its own character sheet before it could play it.
export MATRIX_PERSONA_LABEL_LOCALE="${MATRIX_PERSONA_LABEL_LOCALE:-vi}"

RECIPE="configs/jobs/application-task-job-recipe/${RUN_NAME}.yaml"

echo "### generating recipe"
uv run python application/scripts/generate_vita_case_job.py \
    --job-name "${RUN_NAME}" --task "${TASK_PATH}" "$@"

echo "### running (task ${TASK_SLUG}, model ${MATRIX_PERSONA_MODEL:-<default>}, maxTurns ${MATRIX_CHATBOT_MAX_TURNS})"
uv run matraix run -c "${RECIPE}"

echo "### exporting to ${DATA_DIR}"
uv run python scripts/export_vita_multiturn_results.py \
    "jobs/${RUN_NAME}" --run-dir "${RUN_NAME}"

# The CSV and JSONL are for machines. This is the copy a person opens: one
# page, every conversation, filterable. Generated here so it cannot be the
# step somebody forgets.
uv run python scripts/build_vita_run_report.py "${DATA_DIR}"

echo "### done"
ls -la "${DATA_DIR}"
