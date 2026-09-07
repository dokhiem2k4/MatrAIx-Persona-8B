#!/usr/bin/env bash
# Rerun the 131 stage-2 conversations the endpoint could not answer, then merge
# them with the 7 that already came back and re-export the workbooks.
#
# Run this once the VoiceLab backend has LLM credit again. It probes the
# endpoint first: a run started against a dead backend produces 131 more
# failures and buys nothing.
set -u
cd "$(dirname "$0")/.."
set -a; source application/playground/.env.local; set +a

export MATRIX_CHATBOT_TASK_PATH=application/tasks/chat_vita-drive-assistant
# Endpoint and password come from the environment. Baking either into a
# tracked file would publish the deployment's address and its shared
# password to everyone who clones the repo.
: "${VITA_ASSISTANT_API_URL:?set VITA_ASSISTANT_API_URL to the deployment under test}"
: "${VITA_APP_PASSWORD:?set VITA_APP_PASSWORD to the deployment's app password}"

echo "### probing the endpoint before spending"
probe=$(curl -sk -o /dev/null -w "%{http_code}" -X POST "${VITA_ASSISTANT_API_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -H "x-app-password: ${VITA_APP_PASSWORD}" \
  -H "x-vehicle-session: retry-probe" \
  -d '{"sessionId":"retry-probe","message":"Vita ơi, pin còn bao nhiêu?","drivingContext":"driving","intent":"vehicle_control"}' \
  --max-time 60)
if [ "${probe}" != "200" ]; then
  echo "ABORT: endpoint answered ${probe}, not 200. The backend is still down -- topping up its"
  echo "       LLM credit is what unblocks this. Nothing was spent."
  exit 1
fi
echo "### endpoint healthy (200), running 131 retries"

uv run matraix run -c configs/jobs/vita-lab3p/vita-lab3p-s2-retry.yaml 2>&1 | tail -25

# Both job directories hold trials of the same recipe, so the exporter reads
# them together and the workbook covers all 138 stimuli rather than whichever
# run happened to be exported last.
echo "### merging both runs into one workbook"
merged=jobs/vita-lab3p-s2-all
rm -rf "${merged}"; mkdir -p "${merged}"
for trial in jobs/vita-lab3p-s2/*/ jobs/vita-lab3p-s2-retry/*/; do
  [ -d "${trial}" ] || continue
  ln -sfn "$(realpath "${trial}")" "${merged}/$(basename "${trial}")"
done

uv run python scripts/export_vita_multiturn_results.py "${merged}" -o data/vita-results-lab3p 2>&1 | tail -20
echo "### done"
ls -la data/vita-stimuli-lab3p.csv data/vita-results-lab3p.csv data/vita-results-lab3p.jsonl
