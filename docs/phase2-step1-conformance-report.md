# Harness Conformance Audit Report

- Generated: `2026-03-20T22:57:18`
- Harnesses scanned: `17`
- Overall status counts: `PASS=1`, `WARN=12`, `FAIL=4`

## Per-Harness Summary

| Harness | Overall | Skill file | REPL skin | REPL align | Setup skill pkg | Registry entry | Registry skill_md | CLI invoke | CLI --json |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adguardhome | FAIL | FAIL | PASS | WARN | N/A | PASS | PASS | PASS | PASS |
| anygen | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| audacity | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| blender | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| comfyui | FAIL | FAIL | FAIL | N/A | N/A | PASS | PASS | PASS | PASS |
| drawio | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| gimp | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| inkscape | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| kdenlive | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| libreoffice | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| mermaid | FAIL | FAIL | PASS | WARN | N/A | PASS | PASS | PASS | PASS |
| mubu | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| notebooklm | FAIL | PASS | FAIL | N/A | PASS | PASS | PASS | PASS | PASS |
| obs-studio | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| ollama | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| shotcut | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |
| zoom | WARN | PASS | PASS | WARN | PASS | PASS | PASS | PASS | PASS |

## High-Signal Findings
- `adguardhome` (FAIL)
  - Skill file: Missing expected skill file at adguardhome/agent-harness/cli_anything/adguardhome/skills/SKILL.md
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `anygen` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `audacity` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `blender` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `comfyui` (FAIL)
  - Skill file: Missing expected skill file at comfyui/agent-harness/cli_anything/comfyui/skills/SKILL.md
  - REPL skin: Missing expected REPL skin at comfyui/agent-harness/cli_anything/comfyui/utils/repl_skin.py
- `drawio` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `gimp` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `inkscape` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `kdenlive` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `libreoffice` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `mermaid` (FAIL)
  - Skill file: Missing expected skill file at mermaid/agent-harness/cli_anything/mermaid/skills/SKILL.md
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `notebooklm` (FAIL)
  - REPL skin: Missing expected REPL skin at notebooklm/agent-harness/cli_anything/notebooklm/utils/repl_skin.py
- `obs-studio` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `ollama` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `shotcut` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py
- `zoom` (WARN)
  - REPL align: Differs from canonical cli-anything-plugin/repl_skin.py