# Progress — MatrAIx Persona 8B

> Update this whenever a feature changes state. `done` must come with **evidence** (command/test output).
> Active feature: see `feature_list.json.active_feature` — also surfaced automatically by the
> SessionStart hook at the top of every session.

## Current State
- **Last Updated:** 2026-09-11.
- **Phase:** BLUEPRINT finished → ready to BUILD.  _(update as you progress)_
- **What has been built:** nothing yet (the repo only has the harness).
- **Blockers:** _(list what is waiting on the Homeowner — keys, decisions...)_
- **Recommended Next Step:** scaffold per the Blueprint → `./init.sh scaffold`.

## Feature board (source: feature_list.json)
| ID | Feature | Deps | Status |
|----|---------|------|--------|
| F01 | Scaffold | — | pending ◀ active |
| F02 | Data layer | F01 | pending |
| F03 | Auth | F01,F02 | pending |

## Log (newest first)
Each entry tied to a feature carries its id in the heading: `### 2026-09-11 — <ID>: <title>`. Once
that feature ships (status done/verified + dossier written), move the full entry into
`progress-archive.md` and replace it here with a one-line pointer:
`### 2026-09-11 — <ID>: <title> (shipped — see progress-archive.md)`.
`./init.sh state` fails if a shipped feature's entry is still here untagged.

### 2026-09-11 — Harness setup
- Stood up the harness from the harness-kit template. No product code yet.

## Verification Evidence (command and output — paste it here as it arrives)
_(empty — nothing built yet)_
