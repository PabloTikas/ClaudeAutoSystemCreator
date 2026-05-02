# Agent: [Name]

## Purpose
[One line.]

## Input
- Format: [CSV | JSON | PDF | unstructured]
- Schema: [field list, or "unstructured"]

## Steps
1. [Step]
2. [Step]

## Output
- File: `outputs/<agent>_output_<run_id>.<ext>`
- Schema: [field list or example]
- Validation: [how to verify before handoff]
- Multi-file: write `outputs/_handoff.json` with `{"files":[...]}` if more than one file should pass to the next agent.

## Tools
- `tools/`: [name — purpose — invocation]
- MCP / APIs: [list]

## Errors
- [case]: [action]

## Hard rules
- [rule]
