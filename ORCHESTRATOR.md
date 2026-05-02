# Orchestrator runtime spec

Template-invariant. Do not edit per project. Defines how Claude executes any pipeline built from this template.

## Model
Sequential pipeline. Claude orchestrates: moves files, tracks state, logs. Agents only read `inputs/` and write `outputs/`.

## Sources of truth
- `workflow.json` — step order, retry, error policy. **Only place chain order is defined.**
- `config.json` — shared settings.
- `<Agent>/AgentInstructions.md` — agent behavior. Never references next agent.
- `runs/<run_id>/state.json` — current run progress.

## Run lifecycle

### Start
1. Read `config.json` and `workflow.json`.
2. `run_id = <UTC YYYYMMDD_HHMMSS>`. Create `runs/<run_id>/`.
3. Write `manifest.json`: `{run_id, started_at, trigger, user_inputs:[...], steps:[agent,...]}`.
4. Write `state.json`: `{run_id, current_step:1, status:"running"}`.
5. Copy `user_inputs/*` → step-1 agent's `inputs/`.
6. Open append-only `runs/<run_id>/run.log` (JSONL).

### Per step
1. Update `state.json` (`current_step`, `status:"running"`). Log `step_start`.
2. Verify agent's `inputs/` has expected files per its `AgentInstructions.md`.
3. Invoke agent.
4. On success:
   - Determine handoff files: if `outputs/_handoff.json` exists (`{"files":["a","b"]}`) use that, else newest file in `outputs/`.
   - Validate output against schema if declared.
   - Copy handoff file(s) → `repository/<agent>/`.
   - If next step exists: ensure next `inputs/` empty (warn if not), copy handoff file(s) there.
   - Verify byte length matches after each copy.
   - Clear current agent's `inputs/`. Never clear `outputs/`.
   - Log `step_end` with `status:"success"` and file list.
5. On failure: do NOT copy or clear. Apply error policy.

### End
1. `state.json`: `status:"success"|"failure"`, `ended_at`.
2. Log `run_end`. Append summary line to `runs/index.jsonl`.
3. Report to user: per-step agent name, output path, status, warnings; final run id and status.

## File handoff rules
- `user_inputs/` is never cleared.
- An agent's `outputs/` is never cleared.
- An agent's `inputs/` is cleared only after that step succeeds.
- Multi-file handoff requires `outputs/_handoff.json`. Without it, hand off the newest file by `run_id` in filename.
- Filename convention: `<agent>_output_<run_id>.<ext>`.

## Logging
`runs/<run_id>/run.log` — JSONL, one event per line:
`{"ts":"<ISO8601>","event":"step_start|step_end|file_copy|error|run_end","step":N,"agent":"<name>","status":"...","files":[...],"error":"..."}`

## Error handling
Per-step `on_error` overrides workflow-level. Values:
- `stop` — halt, mark run failed.
- `skip` — log, continue. Forced to `stop` if step has `required:true`.
- `retry` — retry up to step's `retry` count (total attempts = retry + 1). On exhaustion fall through to `stop`.

On any error: never copy or clear files. Preserve `inputs/` and partial `outputs/`.

## Resume
If `runs/<run_id>/state.json` shows `status:"running"` with no active process, ask user: resume from `current_step` or restart. Resume re-invokes that step using preserved `inputs/`.

## Single-agent runs
If user names a specific agent: skip orchestration, run that agent against its current `inputs/`, do not advance the chain. Still write to `runs/<run_id>/run.log` and tag the run `partial:true` in the manifest.
