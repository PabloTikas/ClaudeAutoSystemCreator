# Project: [Name]

[One paragraph: what this system does and why.]

## Operation
This is an AutoSystem pipeline. Before running any agent or workflow read [ORCHESTRATOR.md](ORCHESTRATOR.md) — it defines run lifecycle, file handoff, state, logging, and error handling. Step order lives only in `workflow.json`.

If the user names a specific agent, run only that agent. Otherwise run the full pipeline.

## Project rules
[Project-specific constraints. Empty if none.]

## Project memory
[Critical facts the system must remember across runs.]
