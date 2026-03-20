#!/usr/bin/env python3
"""Repository-level conformance audit for CLI-Anything harnesses.

Checks performed:
- skills/SKILL.md presence
- REPL skin presence and drift from canonical plugin copy
- setup.py skill-file packaging hints where skills exist
- registry.json alignment for entry_point and skill_md
- root CLI expectations (invoke_without_command + --json option)
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


CHECK_ORDER = [
    "skill_md_presence",
    "repl_skin_presence",
    "repl_skin_alignment",
    "setup_skill_packaging",
    "registry_entry_point",
    "registry_skill_md",
    "root_cli_invoke_without_command",
    "root_cli_json_option",
]

CHECK_LABELS = {
    "skill_md_presence": "Skill file",
    "repl_skin_presence": "REPL skin",
    "repl_skin_alignment": "REPL align",
    "setup_skill_packaging": "Setup skill pkg",
    "registry_entry_point": "Registry entry",
    "registry_skill_md": "Registry skill_md",
    "root_cli_invoke_without_command": "CLI invoke",
    "root_cli_json_option": "CLI --json",
}

VALID_STATUS = {"PASS", "WARN", "FAIL", "N/A"}


@dataclass
class CheckResult:
    status: str
    detail: str

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUS:
            raise ValueError(f"Invalid status: {self.status}")


@dataclass
class Harness:
    software: str
    harness_root: Path
    setup_path: Path
    package_name: str | None
    package_path: Path | None
    cli_path: Path | None
    expected_skill_path: Path | None
    expected_repl_skin_path: Path | None


@dataclass
class HarnessResult:
    harness: Harness
    checks: dict[str, CheckResult] = field(default_factory=dict)

    @property
    def overall(self) -> str:
        statuses = [c.status for c in self.checks.values()]
        if any(s == "FAIL" for s in statuses):
            return "FAIL"
        if any(s == "WARN" for s in statuses):
            return "WARN"
        return "PASS"

    @property
    def findings(self) -> list[str]:
        out: list[str] = []
        for key in CHECK_ORDER:
            check = self.checks.get(key)
            if not check:
                continue
            if check.status in {"FAIL", "WARN"}:
                label = CHECK_LABELS.get(key, key)
                out.append(f"{label}: {check.detail}")
        return out


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def discover_harnesses(repo_root: Path) -> list[Harness]:
    harnesses: list[Harness] = []
    setup_paths = sorted(repo_root.glob("*/agent-harness/setup.py"))
    for setup_path in setup_paths:
        harness_root = setup_path.parent
        software = setup_path.parent.parent.name
        cli_anything_root = harness_root / "cli_anything"

        package_dirs: list[Path] = []
        if cli_anything_root.is_dir():
            package_dirs = sorted(
                p
                for p in cli_anything_root.iterdir()
                if p.is_dir() and not p.name.startswith("__")
            )

        selected_package: Path | None = None
        selected_cli: Path | None = None
        for package_dir in package_dirs:
            cli_candidates = sorted(package_dir.glob("*_cli.py"))
            if cli_candidates:
                selected_package = package_dir
                selected_cli = cli_candidates[0]
                break

        package_name = selected_package.name if selected_package else None
        expected_skill_path = (
            selected_package / "skills" / "SKILL.md" if selected_package else None
        )
        expected_repl_skin_path = (
            selected_package / "utils" / "repl_skin.py" if selected_package else None
        )

        harnesses.append(
            Harness(
                software=software,
                harness_root=harness_root,
                setup_path=setup_path,
                package_name=package_name,
                package_path=selected_package,
                cli_path=selected_cli,
                expected_skill_path=expected_skill_path,
                expected_repl_skin_path=expected_repl_skin_path,
            )
        )
    return harnesses


def ast_name(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = ast_name(node.value)
        if base:
            return f"{base}.{node.attr}"
    return None


def extract_console_scripts_from_setup_text(setup_text: str) -> list[str]:
    scripts: list[str] = []
    try:
        tree = ast.parse(setup_text)
    except SyntaxError:
        tree = None

    if tree is not None:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if ast_name(node.func) != "setup":
                continue
            for kw in node.keywords:
                if kw.arg != "entry_points":
                    continue
                scripts.extend(extract_console_scripts_from_node(kw.value))

    if scripts:
        return dedupe(scripts)

    block_match = re.search(
        r"['\"]console_scripts['\"]\s*:\s*\[(.*?)\]",
        setup_text,
        flags=re.DOTALL,
    )
    if not block_match:
        return []
    block = block_match.group(1)
    scripts = [m[0] or m[1] for m in re.findall(r"'([^']+)'|\"([^\"]+)\"", block)]
    return dedupe(scripts)


def extract_console_scripts_from_node(node: ast.AST) -> list[str]:
    if not isinstance(node, ast.Dict):
        return []

    scripts: list[str] = []
    for key_node, value_node in zip(node.keys, node.values):
        if not isinstance(key_node, ast.Constant):
            continue
        if key_node.value != "console_scripts":
            continue
        if isinstance(value_node, (ast.List, ast.Tuple)):
            for element in value_node.elts:
                if isinstance(element, ast.Constant) and isinstance(element.value, str):
                    scripts.append(element.value)
    return scripts


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def parse_console_script_specs(specs: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for spec in specs:
        if "=" not in spec:
            continue
        name, target = spec.split("=", 1)
        parsed[name.strip()] = target.strip()
    return parsed


def check_setup_skill_packaging(setup_text: str) -> bool:
    lowered = setup_text.lower()
    if "skills/*.md" in lowered or "skills\\*.md" in lowered:
        return True
    if re.search(
        r"cli_anything\.[a-z0-9_]+\.skills['\"]?\s*:\s*\[\s*['\"]skill\.md['\"]",
        lowered,
    ):
        return True
    return False


def inspect_cli_root_contract(cli_text: str) -> tuple[bool, bool, bool]:
    try:
        tree = ast.parse(cli_text)
    except SyntaxError:
        return (False, False, False)

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue

        group_call: ast.Call | None = None
        has_json_option = False

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and ast_name(decorator.func) == "click.group":
                group_call = decorator
            if isinstance(decorator, ast.Call) and ast_name(decorator.func) == "click.option":
                for arg in decorator.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "--json" in arg.value:
                            has_json_option = True
                            break

        if group_call is None:
            continue

        invoke_without_command = False
        for kw in group_call.keywords:
            if kw.arg != "invoke_without_command":
                continue
            if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                invoke_without_command = True

        return (True, invoke_without_command, has_json_option)

    return (False, False, False)


def load_registry(registry_path: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if not registry_path.is_file():
        return ({}, ["registry.json is missing"])

    raw = json.loads(read_text(registry_path))
    entries = raw.get("clis", [])
    if not isinstance(entries, list):
        return ({}, ["registry.json field `clis` is not a list"])

    by_name: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    for item in entries:
        if not isinstance(item, dict):
            issues.append("registry.json contains a non-object entry in `clis`")
            continue
        name = item.get("name")
        if not isinstance(name, str):
            issues.append("registry.json contains an entry without string `name`")
            continue
        if name in by_name:
            issues.append(f"registry.json duplicate entry name: {name}")
            continue
        by_name[name] = item
    return (by_name, issues)


def run_audit(repo_root: Path) -> dict[str, Any]:
    canonical_repl_path = repo_root / "cli-anything-plugin" / "repl_skin.py"
    canonical_repl_text = (
        normalize_newlines(read_text(canonical_repl_path))
        if canonical_repl_path.is_file()
        else None
    )

    registry_map, registry_issues = load_registry(repo_root / "registry.json")
    harnesses = discover_harnesses(repo_root)
    results: list[HarnessResult] = []

    for harness in harnesses:
        result = HarnessResult(harness=harness)

        if harness.package_name is None or harness.package_path is None:
            for check in CHECK_ORDER:
                result.checks[check] = CheckResult(
                    "FAIL",
                    "Could not identify cli_anything package folder with *_cli.py",
                )
            results.append(result)
            continue

        skill_path = harness.expected_skill_path
        repl_path = harness.expected_repl_skin_path
        cli_path = harness.cli_path
        setup_text = read_text(harness.setup_path)
        setup_scripts = parse_console_script_specs(
            extract_console_scripts_from_setup_text(setup_text)
        )

        skill_exists = bool(skill_path and skill_path.is_file())
        if skill_exists:
            result.checks["skill_md_presence"] = CheckResult(
                "PASS",
                f"Found {relative_posix(skill_path, repo_root)}",
            )
        else:
            expected = (
                relative_posix(skill_path, repo_root)
                if skill_path is not None
                else "unknown"
            )
            result.checks["skill_md_presence"] = CheckResult(
                "FAIL",
                f"Missing expected skill file at {expected}",
            )

        if repl_path and repl_path.is_file():
            result.checks["repl_skin_presence"] = CheckResult(
                "PASS",
                f"Found {relative_posix(repl_path, repo_root)}",
            )
            if canonical_repl_text is None:
                result.checks["repl_skin_alignment"] = CheckResult(
                    "WARN",
                    "Canonical plugin REPL skin is missing; alignment not checked",
                )
            else:
                harness_repl_text = normalize_newlines(read_text(repl_path))
                if harness_repl_text == canonical_repl_text:
                    result.checks["repl_skin_alignment"] = CheckResult(
                        "PASS",
                        "Matches canonical cli-anything-plugin/repl_skin.py",
                    )
                else:
                    result.checks["repl_skin_alignment"] = CheckResult(
                        "WARN",
                        "Differs from canonical cli-anything-plugin/repl_skin.py",
                    )
        else:
            expected = (
                relative_posix(repl_path, repo_root)
                if repl_path is not None
                else "unknown"
            )
            result.checks["repl_skin_presence"] = CheckResult(
                "FAIL",
                f"Missing expected REPL skin at {expected}",
            )
            result.checks["repl_skin_alignment"] = CheckResult(
                "N/A",
                "No harness repl_skin.py available for alignment check",
            )

        has_skill_packaging = check_setup_skill_packaging(setup_text)
        if skill_exists and has_skill_packaging:
            result.checks["setup_skill_packaging"] = CheckResult(
                "PASS",
                "setup.py appears to include skill file packaging",
            )
        elif skill_exists and not has_skill_packaging:
            result.checks["setup_skill_packaging"] = CheckResult(
                "FAIL",
                "SKILL.md exists but setup.py has no obvious skill file packaging pattern",
            )
        elif not skill_exists and has_skill_packaging:
            result.checks["setup_skill_packaging"] = CheckResult(
                "WARN",
                "setup.py references skill packaging but SKILL.md is missing",
            )
        else:
            result.checks["setup_skill_packaging"] = CheckResult(
                "N/A",
                "No SKILL.md in harness package; packaging check not applicable",
            )

        registry_entry = registry_map.get(harness.software)
        if registry_entry is None:
            result.checks["registry_entry_point"] = CheckResult(
                "FAIL",
                f"No registry.json entry with name={harness.software}",
            )
            result.checks["registry_skill_md"] = CheckResult(
                "FAIL",
                f"No registry.json entry with name={harness.software}",
            )
        else:
            reg_entry_point = registry_entry.get("entry_point")
            if not isinstance(reg_entry_point, str):
                result.checks["registry_entry_point"] = CheckResult(
                    "FAIL",
                    "registry.json entry_point is missing or not a string",
                )
            elif reg_entry_point in setup_scripts:
                result.checks["registry_entry_point"] = CheckResult(
                    "PASS",
                    f"entry_point {reg_entry_point} found in setup.py console_scripts",
                )
            else:
                known = ", ".join(sorted(setup_scripts)) or "(none)"
                result.checks["registry_entry_point"] = CheckResult(
                    "FAIL",
                    f"registry entry_point={reg_entry_point} not found in setup.py console_scripts ({known})",
                )

            reg_skill_md = registry_entry.get("skill_md")
            expected_skill_md = (
                f"{harness.software}/agent-harness/cli_anything/{harness.package_name}/skills/SKILL.md"
            )

            if skill_exists:
                if not isinstance(reg_skill_md, str) or not reg_skill_md.strip():
                    result.checks["registry_skill_md"] = CheckResult(
                        "FAIL",
                        "SKILL.md exists but registry skill_md is null/empty",
                    )
                else:
                    normalized = reg_skill_md.replace("\\", "/")
                    if normalized != expected_skill_md:
                        result.checks["registry_skill_md"] = CheckResult(
                            "FAIL",
                            f"registry skill_md={normalized} does not match expected {expected_skill_md}",
                        )
                    elif not (repo_root / normalized).is_file():
                        result.checks["registry_skill_md"] = CheckResult(
                            "FAIL",
                            f"registry skill_md path does not exist on disk: {normalized}",
                        )
                    else:
                        result.checks["registry_skill_md"] = CheckResult(
                            "PASS",
                            f"skill_md matches expected path {expected_skill_md}",
                        )
            else:
                if reg_skill_md is None or reg_skill_md == "":
                    result.checks["registry_skill_md"] = CheckResult(
                        "PASS",
                        "SKILL.md missing and registry skill_md is null/empty",
                    )
                else:
                    normalized = str(reg_skill_md).replace("\\", "/")
                    result.checks["registry_skill_md"] = CheckResult(
                        "FAIL",
                        f"registry skill_md points to {normalized} but SKILL.md is missing",
                    )

        if cli_path and cli_path.is_file():
            cli_text = read_text(cli_path)
            detected, invoke_flag, json_flag = inspect_cli_root_contract(cli_text)
            if detected:
                if invoke_flag:
                    result.checks["root_cli_invoke_without_command"] = CheckResult(
                        "PASS",
                        "Root click.group uses invoke_without_command=True",
                    )
                else:
                    result.checks["root_cli_invoke_without_command"] = CheckResult(
                        "FAIL",
                        "Root click.group missing invoke_without_command=True",
                    )

                if json_flag:
                    result.checks["root_cli_json_option"] = CheckResult(
                        "PASS",
                        "Root click.group defines a --json option",
                    )
                else:
                    result.checks["root_cli_json_option"] = CheckResult(
                        "FAIL",
                        "Root click.group is missing a --json option",
                    )
            else:
                result.checks["root_cli_invoke_without_command"] = CheckResult(
                    "WARN",
                    f"Could not detect root click.group in {relative_posix(cli_path, repo_root)}",
                )
                result.checks["root_cli_json_option"] = CheckResult(
                    "WARN",
                    f"Could not detect root click.group in {relative_posix(cli_path, repo_root)}",
                )
        else:
            result.checks["root_cli_invoke_without_command"] = CheckResult(
                "FAIL",
                "Missing *_cli.py file for root CLI contract check",
            )
            result.checks["root_cli_json_option"] = CheckResult(
                "FAIL",
                "Missing *_cli.py file for root CLI contract check",
            )

        results.append(result)

    summary_counts = {
        "harnesses": len(results),
        "overall_pass": sum(1 for r in results if r.overall == "PASS"),
        "overall_warn": sum(1 for r in results if r.overall == "WARN"),
        "overall_fail": sum(1 for r in results if r.overall == "FAIL"),
    }

    check_status_counts: dict[str, dict[str, int]] = {}
    for check in CHECK_ORDER:
        check_status_counts[check] = {status: 0 for status in VALID_STATUS}
    for result in results:
        for check in CHECK_ORDER:
            status = result.checks[check].status
            check_status_counts[check][status] += 1

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(repo_root),
        "registry_issues": registry_issues,
        "summary": summary_counts,
        "check_status_counts": check_status_counts,
        "results": results,
    }


def render_text(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("CLI-Anything Harness Conformance Audit")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Harnesses: {report['summary']['harnesses']}")
    lines.append(
        "Overall: "
        f"PASS={report['summary']['overall_pass']} "
        f"WARN={report['summary']['overall_warn']} "
        f"FAIL={report['summary']['overall_fail']}"
    )
    if report["registry_issues"]:
        lines.append("Registry issues:")
        for issue in report["registry_issues"]:
            lines.append(f"- {issue}")

    lines.append("")
    lines.append("Per-harness results:")
    for item in report["results"]:
        harness: Harness = item.harness
        lines.append(f"- {harness.software}: {item.overall}")
        for check in CHECK_ORDER:
            c = item.checks[check]
            lines.append(f"  - {CHECK_LABELS[check]}: {c.status} ({c.detail})")
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Harness Conformance Audit Report")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Harnesses scanned: `{report['summary']['harnesses']}`")
    lines.append(
        "- Overall status counts:"
        f" `PASS={report['summary']['overall_pass']}`,"
        f" `WARN={report['summary']['overall_warn']}`,"
        f" `FAIL={report['summary']['overall_fail']}`"
    )

    if report["registry_issues"]:
        lines.append("")
        lines.append("## Registry Notes")
        for issue in report["registry_issues"]:
            lines.append(f"- {issue}")

    lines.append("")
    lines.append("## Per-Harness Summary")
    lines.append("")
    lines.append("| Harness | Overall | Skill file | REPL skin | REPL align | Setup skill pkg | Registry entry | Registry skill_md | CLI invoke | CLI --json |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for item in report["results"]:
        harness: Harness = item.harness
        row = [
            harness.software,
            item.overall,
            item.checks["skill_md_presence"].status,
            item.checks["repl_skin_presence"].status,
            item.checks["repl_skin_alignment"].status,
            item.checks["setup_skill_packaging"].status,
            item.checks["registry_entry_point"].status,
            item.checks["registry_skill_md"].status,
            item.checks["root_cli_invoke_without_command"].status,
            item.checks["root_cli_json_option"].status,
        ]
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## High-Signal Findings")
    findings_written = False
    for item in report["results"]:
        if not item.findings:
            continue
        findings_written = True
        lines.append(f"- `{item.harness.software}` ({item.overall})")
        for finding in item.findings:
            lines.append(f"  - {finding}")

    if not findings_written:
        lines.append("- No WARN/FAIL findings.")

    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    serializable = {
        "generated_at": report["generated_at"],
        "repo_root": report["repo_root"],
        "registry_issues": report["registry_issues"],
        "summary": report["summary"],
        "check_status_counts": report["check_status_counts"],
        "results": [
            {
                "software": r.harness.software,
                "overall": r.overall,
                "checks": {
                    check: {"status": r.checks[check].status, "detail": r.checks[check].detail}
                    for check in CHECK_ORDER
                },
            }
            for r in report["results"]
        ],
    }
    return json.dumps(serializable, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit CLI-Anything harness conformance across the repository."
    )
    parser.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output",
        help="Optional file path to write the report output.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 when FAIL findings exist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    report = run_audit(repo_root)

    if args.format == "markdown":
        rendered = render_markdown(report)
    elif args.format == "json":
        rendered = render_json(report)
    else:
        rendered = render_text(report)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = repo_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        print(f"Wrote report: {output_path.relative_to(repo_root).as_posix()}")
    else:
        print(rendered)

    has_fail = any(r.overall == "FAIL" for r in report["results"])
    if args.strict and has_fail:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
