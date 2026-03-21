import json
import os
import tempfile

import pytest

from cli_anything.mermaid.core import export as export_mod
from cli_anything.mermaid.core import project as project_mod
from cli_anything.mermaid.core.session import Session, default_state
from cli_anything.mermaid.utils import mermaid_backend


def test_default_state():
    state = default_state()
    assert "flowchart TD" in state["code"]
    assert json.loads(state["mermaid"])["theme"] == "default"


def test_save_open_roundtrip():
    session = Session()
    project_mod.new_project(session, sample="sequence")
    with tempfile.NamedTemporaryFile(suffix=".mermaid.json", delete=False) as fh:
        path = fh.name
    try:
        project_mod.save_project(session, path)
        other = Session()
        result = project_mod.open_project(other, path)
        assert result["line_count"] > 0
        assert "sequenceDiagram" in other.state["code"]
    finally:
        os.unlink(path)


def test_undo_redo():
    session = Session()
    session.new_project()
    original = session.state["code"]
    session.set_code("graph TD\n  A --> B\n")
    assert session.undo() is True
    assert session.state["code"] == original
    assert session.redo() is True
    assert "A --> B" in session.state["code"]


def test_backend_serialization_and_urls():
    serialized = mermaid_backend.serialize_state(default_state())
    assert serialized.startswith("pako:")
    assert mermaid_backend.build_render_url(serialized, "svg").startswith("https://")
    assert mermaid_backend.build_live_url(serialized, "view").startswith("https://")


def test_share_payload():
    session = Session()
    session.new_project()
    result = export_mod.share(session, mode="edit")
    assert result["mode"] == "edit"
    assert result["url"].startswith("https://mermaid.live/edit#")


def test_fetch_render_bytes_retries_then_succeeds(monkeypatch):
    attempts = {"count": 0}

    class DummyResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"<svg/>"

    def fake_urlopen(req, timeout):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise TimeoutError("temporary timeout")
        return DummyResponse()

    monkeypatch.setattr(mermaid_backend.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(mermaid_backend.time, "sleep", lambda *_args, **_kwargs: None)

    data = mermaid_backend._fetch_render_bytes("https://example.test/render", timeout=0.01, retries=2)
    assert data == b"<svg/>"
    assert attempts["count"] == 2


def test_fetch_render_bytes_raises_clear_error_after_retries(monkeypatch):
    attempts = {"count": 0}

    def fake_urlopen(req, timeout):
        attempts["count"] += 1
        raise TimeoutError("still timing out")

    monkeypatch.setattr(mermaid_backend.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(mermaid_backend.time, "sleep", lambda *_args, **_kwargs: None)

    with pytest.raises(RuntimeError, match="Mermaid renderer request failed after 2 attempts"):
        mermaid_backend._fetch_render_bytes("https://example.test/render", timeout=0.01, retries=2)

    assert attempts["count"] == 2
