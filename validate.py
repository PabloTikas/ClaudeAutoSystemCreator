#!/usr/bin/env python3
"""Validate AutoSystem template setup. Flags placeholders, missing folders, name mismatches.

Exit code: 0 if no errors (warnings allowed), 1 otherwise.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PLACEHOLDER = re.compile(r"\[[^\]\n]+\]")

errors: list[str] = []
warnings: list[str] = []


def need(path: Path, label: str) -> bool:
    if not path.exists():
        errors.append(f"missing: {label} ({path.relative_to(ROOT)})")
        return False
    return True


def scan_placeholders(path: Path, label: str) -> None:
    hits = PLACEHOLDER.findall(path.read_text(encoding="utf-8"))
    if hits:
        warnings.append(f"{label}: {len(hits)} placeholder(s) remain")


# config.json
cfg_path = ROOT / "config.json"
if need(cfg_path, "config.json"):
    try:
        json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"config.json invalid JSON: {e}")

# workflow.json + agent folders
wf_path = ROOT / "workflow.json"
agents: list[str] = []
if need(wf_path, "workflow.json"):
    try:
        wf = json.loads(wf_path.read_text(encoding="utf-8"))
        for i, step in enumerate(wf.get("steps", []), 1):
            name = step.get("agent", "")
            if not name or name.startswith("["):
                errors.append(f"step {i}: agent name not set")
                continue
            if name in agents:
                errors.append(f"step {i}: duplicate agent '{name}'")
            agents.append(name)
            adir = ROOT / name
            if not adir.exists():
                errors.append(f"step {i}: folder '{name}/' missing")
                continue
            for sub in ("inputs", "outputs", "tools"):
                if not (adir / sub).exists():
                    warnings.append(f"{name}/: '{sub}/' missing")
            ai = adir / "AgentInstructions.md"
            if not ai.exists():
                errors.append(f"{name}/: AgentInstructions.md missing")
            else:
                scan_placeholders(ai, f"{name}/AgentInstructions.md")
    except json.JSONDecodeError as e:
        errors.append(f"workflow.json invalid JSON: {e}")

# Top-level dirs
for d in ("user_inputs", "repository", "runs"):
    if not (ROOT / d).exists():
        warnings.append(f"top-level '{d}/' missing (created on first run)")

# CLAUDE.md
claude_md = ROOT / "CLAUDE.md"
if need(claude_md, "CLAUDE.md"):
    scan_placeholders(claude_md, "CLAUDE.md")

# Output
for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"ERROR {e}")
if not errors and not warnings:
    print("OK")
sys.exit(1 if errors else 0)
