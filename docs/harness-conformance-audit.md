# Harness Conformance Audit

Repository-level audit script for Phase 2 Step 1.

## Run

From repository root:

```powershell
py -3 scripts/harness_conformance_audit.py --format text
```

Generate a markdown artifact:

```powershell
py -3 scripts/harness_conformance_audit.py --format markdown --output docs/phase2-step1-conformance-report.md
```

Optional strict mode (non-zero exit if any harness has `FAIL`):

```powershell
py -3 scripts/harness_conformance_audit.py --strict
```

## What It Checks

Per `*/agent-harness/setup.py` harness:

1. `skills/SKILL.md` presence in the harness package
2. `utils/repl_skin.py` presence
3. REPL skin alignment against `cli-anything-plugin/repl_skin.py`
4. `setup.py` skill file packaging hints when a skill file exists
5. `registry.json` alignment for:
   - `entry_point` vs `setup.py` console script names
   - `skill_md` path vs expected package location
6. Root CLI contract in `*_cli.py`:
   - `@click.group(invoke_without_command=True)`
   - root `--json` option

## Status Semantics

- `PASS`: check satisfies expected baseline
- `WARN`: check is non-blocking but indicates drift/uncertainty
- `FAIL`: check violates expected baseline
- `N/A`: check not applicable for current harness state
