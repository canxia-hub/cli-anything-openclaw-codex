# Phase 1 Brief

## Objective
Create a Phase 1 inspection and adaptation plan for this isolated `CLI-Anything` clone.

## What to inspect
- Repository structure and key modules
- Existing OpenClaw support
- Existing Codex support
- Any skill/plugin directory layout
- REPL or interactive UX code paths
- Output formatting / JSON serialization paths
- Windows-sensitive assumptions
- Places where `codex exec`-first automation should replace older patterns
- Opportunities to add or improve `agents/openai.yaml` and skill metadata

## Required output
Write `docs/phase1-codex-analysis.md` containing:
1. executive summary
2. relevant files/modules map
3. unnecessary or lower-priority areas to defer
4. top risks
5. recommended Phase 2 code changes
6. recommended task ordering
7. notes for Windows-native execution

## Constraints
- Analysis first; avoid broad code changes.
- If you edit anything, keep it minimal and document why.
- Do not delete files in Phase 1.
