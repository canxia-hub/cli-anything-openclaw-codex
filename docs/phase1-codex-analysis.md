# Phase 1 Codex/OpenClaw Analysis

## Executive Summary
This repository is a multi-harness monorepo: each software integration lives under `<software>/agent-harness/`, while agent-platform orchestration lives in root-level plugin/skill directories.

For Codex and OpenClaw specifically, support exists and is usable now (`codex-skill/`, `openclaw-skill/`), but the harness layer has consistency gaps that matter for agent reliability: not all harnesses ship `SKILL.md`, not all use the same REPL skin path/version, and JSON/session persistence patterns are not uniformly Windows-safe.

No destructive cleanup was performed in Phase 1.

## Relevant Files/Modules Map

### 1. Codex/OpenClaw integration surface
- `codex-skill/SKILL.md`: Codex-facing skill contract; delegates methodology to `cli-anything-plugin/HARNESS.md`.
- `codex-skill/scripts/install.ps1`, `codex-skill/scripts/install.sh`: Codex skill installers.
- `codex-skill/agents/openai.yaml`: Codex agent metadata.
- `openclaw-skill/SKILL.md`: OpenClaw-facing skill contract (parallel structure to Codex skill).
- `README.md` (`OpenClaw`, `Codex` sections): user-facing install/use flow.

### 2. Methodology and command orchestration
- `cli-anything-plugin/HARNESS.md`: source of truth for phases, REPL, JSON output, packaging, testing.
- `cli-anything-plugin/commands/*.md`: Claude command specs (`cli-anything`, `refine`, `test`, `validate`, `list`).
- `opencode-commands/*.md`: OpenCode command equivalents.
- `qoder-plugin/setup-qodercli.sh`: Qoder plugin registration script.

### 3. Skill generation and skill packaging
- `cli-anything-plugin/skill_generator.py`: extracts metadata from harnesses and emits SKILL docs.
- `cli-anything-plugin/templates/SKILL.md.template`: generated skill template.
- `skill_generation/tests/test_skill_path.py`: validates skill discovery and `setup.py` package-data assumptions.
- Per-harness skill location pattern: `<software>/agent-harness/cli_anything/<pkg>/skills/SKILL.md`.

### 4. REPL behavior and output formatting
- Canonical REPL skin: `cli-anything-plugin/repl_skin.py`.
- Per-harness REPL and command glue: `<software>/agent-harness/cli_anything/<pkg>/<pkg>_cli.py`.
- Session persistence examples:
  - `<software>/agent-harness/cli_anything/<pkg>/core/session.py`
  - `audacity/agent-harness/cli_anything/audacity/utils/file_io.py`
  - `mubu/agent-harness/cli_anything/mubu/mubu_cli.py` (custom lock/save/session handling)

### 5. Packaging and distribution
- Per-harness package files: `<software>/agent-harness/setup.py` (+ `mubu/agent-harness/pyproject.toml`).
- Hub registry: `registry.json` (install command, entry point, `skill_md` metadata).
- Hub UI: `docs/hub/index.html`.

### 6. Current consistency snapshot (high-signal)
- Missing `skills/SKILL.md`: `adguardhome`, `comfyui`, `mermaid` harnesses.
- Missing `utils/repl_skin.py`: `comfyui`, `notebooklm` harnesses.
- `setup.py` without `package_data`/skill inclusion: notably `adguardhome`, `mermaid`; `comfyui` has `include_package_data` but no explicit skills glob.
- `repl_skin.py` copies are version-drifted across harnesses; not all match `cli-anything-plugin/repl_skin.py`.

## Lower-Priority Areas to Defer
- Domain-specific backend behavior per app (e.g., media/render fidelity in each `core/` module).
- Visual/UX polish of `docs/hub/index.html`.
- Translation parity across `README_CN.md` / `README_JA.md` unless platform instructions diverge critically.
- Non-Codex/OpenClaw community surfaces not on immediate integration path.

## Top Risks
1. Agent discoverability inconsistency: missing `SKILL.md` and uneven packaging of skill files across harnesses.
2. REPL behavior divergence: not all harnesses use the same unified REPL skin or capability level.
3. Windows write-safety risk: many JSON persistence helpers rely on `fcntl` fallback; on Windows this can silently become unlocked writes.
4. Linux-centric assumptions in docs/scripts (`/root/...`, `which`, `apt install`, bash-first flows) increase friction for Windows-native execution.
5. Coverage gap: skill-path tests currently target a subset of harnesses, so regressions in newer harnesses can slip.

## Recommended Phase 2 Code Changes
1. Add a repository-level harness conformance checker (script + CI) for:
   - `invoke_without_command=True`
   - `--json` root option
   - REPL skin presence
   - `skills/SKILL.md` presence
   - `setup.py` skill packaging
   - registry alignment (`registry.json` `skill_md`/entry point).
2. Normalize missing skill packaging:
   - Add `skills/SKILL.md` for `adguardhome`, `comfyui`, `mermaid`.
   - Update corresponding `setup.py` package data to install skill files.
3. Normalize REPL baseline:
   - Introduce/align `utils/repl_skin.py` usage in `comfyui` and `notebooklm`.
   - Align existing harness copies to canonical plugin version (or centralize import strategy).
4. Unify JSON persistence with a Windows-safe helper:
   - Prefer temp-file + `os.replace` atomic writes and optional cross-platform locking hooks.
   - Replace repeated ad hoc `_locked_save_json` implementations.
5. Windows-native docs/script pass:
   - Replace hardcoded `/root/...` examples with repo-relative + PowerShell equivalents.
   - Replace `which` with cross-platform guidance (`Get-Command` / `where` / `which`).
   - Keep bash instructions but add first-class PowerShell paths.
6. Expand tests:
   - Extend `skill_generation/tests/test_skill_path.py` harness list to all active harnesses.
   - Add tests around Windows fallback behavior for persistence helpers.

## Recommended Task Ordering
1. Build and run conformance audit script (no behavior change).
2. Fix skill files + `setup.py` packaging deltas.
3. Align REPL skin usage/copies.
4. Introduce shared persistence helper and migrate harnesses incrementally.
5. Update Windows-native docs/scripts.
6. Extend test coverage and run full validation.

## Windows-Native Execution Notes
- Current repo includes a proper Codex PowerShell installer: `codex-skill/scripts/install.ps1`.
- OpenClaw setup is documented as manual file copy; consider adding a PowerShell helper in Phase 2.
- Prefer PowerShell-safe verification commands in docs:
  - `Get-Command cli-anything-<software>`
  - `python -m pip install -e .`
- Avoid hardcoding Linux paths in examples; use repo-relative paths and `%USERPROFILE%`/`$HOME`-aware instructions.
- Keep `cygpath` checks for bash environments, but avoid making bash the only documented Windows path.
