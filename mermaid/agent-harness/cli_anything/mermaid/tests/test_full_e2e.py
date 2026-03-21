import json
import os
import shutil
import subprocess
import sys


def _resolve_cli(name: str):
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m cli_anything.mermaid")
    return [sys.executable, "-m", "cli_anything.mermaid"]


class TestMermaidCLI:
    CLI = _resolve_cli("cli-anything-mermaid")

    def _run(self, args, **kwargs):
        run_kwargs = {
            "capture_output": True,
            "text": True,
            "check": True,
            "timeout": 60,
        }
        run_kwargs.update(kwargs)
        return subprocess.run(self.CLI + args, **run_kwargs)

    def test_help(self):
        result = self._run(["--help"])
        assert "Mermaid" in result.stdout

    def test_repl_quit_with_piped_stdin(self):
        result = self._run([], input="quit\n")
        assert "cli-anything" in result.stdout
        assert "Goodbye" in result.stdout

    def test_project_new_json(self, tmp_path):
        path = str(tmp_path / "demo.mermaid.json")
        result = self._run(["--json", "project", "new", "-o", path])
        data = json.loads(result.stdout)
        assert data["action"] == "new_project"
        assert os.path.exists(path)

    def test_render_svg(self, tmp_path):
        project_path = str(tmp_path / "demo.mermaid.json")
        output_path = str(tmp_path / "demo.svg")
        self._run(["project", "new", "-o", project_path])
        self._run(["--project", project_path, "diagram", "set", "--text", "graph TD; A[Test] --> B[Works]"])
        result = self._run(
            ["--json", "--project", project_path, "export", "render", output_path, "-f", "svg", "--overwrite"]
        )
        data = json.loads(result.stdout)
        assert data["action"] == "render"
        assert os.path.exists(output_path)
        with open(output_path, "r", encoding="utf-8") as fh:
            assert "<svg" in fh.read(200)

    def test_render_png(self, tmp_path):
        project_path = str(tmp_path / "demo.mermaid.json")
        output_path = str(tmp_path / "demo.png")
        self._run(["project", "new", "-o", project_path])
        self._run(["--project", project_path, "diagram", "set", "--text", "graph TD; A[Test] --> B[Works]"])
        result = self._run(
            ["--json", "--project", project_path, "export", "render", output_path, "-f", "png", "--overwrite"]
        )
        data = json.loads(result.stdout)
        assert data["format"] == "png"
        with open(output_path, "rb") as fh:
            assert fh.read(4) == b"\x89PNG"

    def test_share_view_url(self, tmp_path):
        project_path = str(tmp_path / "demo.mermaid.json")
        self._run(["project", "new", "-o", project_path])
        result = self._run(["--json", "--project", project_path, "export", "share", "--mode", "view"])
        data = json.loads(result.stdout)
        assert data["url"].startswith("https://mermaid.live/view#")
