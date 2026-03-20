# AGENTS.md

## Project scope
This repository is an isolated working clone for evaluating and adapting `HKUDS/CLI-Anything` for OpenClaw and Codex.

## Hard boundaries
- Never read from or modify anything under `C:\Users\Administrator\.openclaw\`.
- Never touch the live OpenClaw gateway, config, skills, or runtime files.
- Work only inside this repository.
- Prefer analysis-first changes. If uncertain, write findings to docs instead of making broad edits.

## Codex execution policy for this repo
- Prefer `codex exec` style automation over interactive-only flows.
- Preserve upstream core behavior unless a change is explicitly justified.
- Keep edits small, reviewable, and Windows-friendly.
- Prefer PowerShell-safe paths and clear notes for Windows-native usage.

## Current mission
Phase 1 only:
1. Inspect repository layout.
2. Identify files relevant to Codex, OpenClaw, skills, REPL, output formatting, and packaging.
3. Produce a concrete cleanup/adaptation plan.
4. Do not perform destructive cleanup yet.
