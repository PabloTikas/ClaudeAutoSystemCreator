# Setup — AI Copilot Playbook

This file is **for the AI**, not the user. When the user asks to set up, personalize, or initialize this template, follow this playbook end-to-end. Act as a copilot: drive the conversation, propose decisions, then execute.

## 0. Preconditions

- If the user gave a repo URL instead of a local clone, clone it first (`git clone <url>`) and `cd` into it. Confirm the working directory before any edits.
- **Detach from the template remote immediately** so customizations never push back to it. Run `git remote remove origin` (and remove any other remotes that point at the template). If the user wants version control for their new project, ask for their own remote URL and `git remote add origin <their-url>`; otherwise leave it remoteless. Confirm with `git remote -v` (should be empty or point only at the user's repo) before any other edits.
- Confirm this is the unmodified template (check for `Agent1Name/`, placeholder `[Name]` in `CLAUDE.md`). If it's already customized, ask whether to reset, extend, or abort.
- Read `ORCHESTRATOR.md` once so you understand the runtime contract you're configuring for.

## 1. Interview the user

Ask in batches, not one-by-one. Group related questions; show your proposed answer where you can infer one and let the user override. Use `AskUserQuestion` if available.

**Batch A — project identity**
- Project name (becomes folder/repo name and `workflow.json#name`).
- One-paragraph purpose: what it does, for whom, why it exists.
- Hard project rules (compliance, tone, languages, must-not-do). Empty is fine.

**Batch B — pipeline shape**
- What does the user drop into `user_inputs/`? Format, typical size, frequency.
- What is the final deliverable? Format, where it should land, who consumes it.
- Based on input → output, **propose** a pipeline (3–6 agents is typical). Name each agent by role (`Extractor`, `Classifier`, `Reporter` — not `Agent1`). Show the chain as a one-line diagram and ask the user to confirm, add, remove, or reorder.

**Batch C — per agent (loop once per confirmed agent)**
- Purpose (one line).
- Input schema (fields or "unstructured").
- Step list (3–7 steps).
- Output schema and file extension.
- **Proactively propose tools.** Don't wait to be asked. Suggest:
  - Local scripts in `tools/` (e.g., a Python parser, a deduper, a validator) — name them and describe their I/O.
  - MCP servers that fit the job (e.g., Notion/Drive/Gmail for content; web fetch/search for research; database MCPs for queries). Only suggest ones the user is likely to have or can plausibly add.
  - External APIs the user already mentioned or that obviously fit.
  Mark each suggestion `[suggested]` so the user knows it's your idea, not a requirement. Confirm before writing.
- Failure modes worth handling explicitly (and `on_error`: stop/skip/retry + count).

## 2. Confirm the plan

Before writing any file, summarize:
- Project name + purpose
- Full agent chain with one-line role per agent
- Tools per agent (with `[suggested]` flags)
- Anything you're unsure about — ask now, not after writing

Wait for explicit "go".

## 3. Execute

Do these in order. Use parallel tool calls where independent.

1. **Rename agent folders.** `Agent1Name/` → first agent's role-name, etc. Add or delete folders to match the confirmed chain. Each agent folder keeps `inputs/`, `outputs/`, `tools/`, `AgentInstructions.md`.
2. **Fill `workflow.json`** — `name`, `description`, ordered `steps[]` with `retry` and `required` per step, workflow-level `on_error`.
3. **Fill each `AgentInstructions.md`** using the existing template sections (Purpose, Input, Steps, Output, Tools, Errors, Hard rules). No placeholders left. Never reference the next agent by name (orchestrator handles handoff).
4. **Fill `CLAUDE.md`** — project name, one-paragraph purpose, project rules, project memory. Keep it lean (it auto-loads every turn).
5. **Scaffold proposed tools.** For each `[suggested]` tool the user accepted, create a stub in the agent's `tools/` directory with a short header comment describing inputs, outputs, and invocation. Don't implement full logic unless the user asked — stubs let them iterate.
6. **Update `config.json`** only if the user specified non-default language, date format, or shared settings.
7. **Run `python validate.py`.** If it reports errors, fix them and re-run until clean. Warnings about empty `user_inputs/`, `repository/`, `runs/` are expected on a fresh setup — leave them.

## 4. Hand off

Report to the user:
- Final agent chain (names, in order)
- Files changed
- Tool stubs created and what's left for the user to implement
- `validate.py` result
- How to run: drop files into `user_inputs/`, then ask Claude to run the workflow (or name a single agent for partial runs)

Offer one concrete next step (e.g., "want me to flesh out the `Extractor/tools/parse_pdf.py` stub now?"). Don't push more.

## Notes for the AI

- Don't invent agents to look thorough. If two agents do the work, propose two.
- Don't write code in `tools/` beyond stubs unless asked — the user may have strong preferences.
- If the user pushes back on a suggestion, drop it without re-litigating.
- Keep written files lean. `CLAUDE.md` and `AgentInstructions.md` files are read on every run; bloat costs tokens forever.
