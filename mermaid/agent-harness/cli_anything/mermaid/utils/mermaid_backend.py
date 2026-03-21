"""Backend helpers for Mermaid Live Editor render/share state."""

from __future__ import annotations

import base64
import json
import os
import socket
import time
import urllib.error
import urllib.request
import zlib


RENDER_BASE = os.environ.get("MERMAID_RENDERER_URL", "https://mermaid.ink").rstrip("/")
LIVE_BASE = os.environ.get("MERMAID_LIVE_URL", "https://mermaid.live").rstrip("/")
DEFAULT_RENDER_TIMEOUT = float(os.environ.get("MERMAID_RENDER_TIMEOUT", "15"))
DEFAULT_RENDER_RETRIES = max(1, int(os.environ.get("MERMAID_RENDER_RETRIES", "3")))
DEFAULT_RENDER_RETRY_BACKOFF = float(os.environ.get("MERMAID_RENDER_RETRY_BACKOFF", "1.0"))


def serialize_state(state: dict) -> str:
    payload = json.dumps(state, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(payload, level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    return f"pako:{encoded}"


def build_render_url(serialized: str, fmt: str) -> str:
    if fmt == "svg":
        return f"{RENDER_BASE}/svg/{serialized}"
    if fmt == "png":
        return f"{RENDER_BASE}/img/{serialized}?type=png"
    raise ValueError(f"Unsupported format: {fmt}")


def build_live_url(serialized: str, mode: str) -> str:
    if mode not in {"edit", "view"}:
        raise ValueError(f"Unsupported share mode: {mode}")
    return f"{LIVE_BASE}/{mode}#{serialized}"


def _fetch_render_bytes(url: str, timeout: float | None = None, retries: int | None = None) -> bytes:
    timeout = DEFAULT_RENDER_TIMEOUT if timeout is None else timeout
    retries = DEFAULT_RENDER_RETRIES if retries is None else max(1, retries)
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except (TimeoutError, socket.timeout, urllib.error.URLError, OSError) as exc:
            last_error = exc
            if attempt >= retries:
                break
            sleep_seconds = DEFAULT_RENDER_RETRY_BACKOFF * attempt
            time.sleep(sleep_seconds)

    detail = str(last_error) if last_error is not None else "unknown render failure"
    raise RuntimeError(
        f"Mermaid renderer request failed after {retries} attempts (timeout={timeout}s): {detail}. URL: {url}"
    ) from last_error


def render_to_file(serialized: str, output_path: str, fmt: str) -> dict:
    url = build_render_url(serialized, fmt)
    data = _fetch_render_bytes(url)
    parent = os.path.dirname(os.path.abspath(output_path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(output_path, "wb") as fh:
        fh.write(data)
    return {
        "output": os.path.abspath(output_path),
        "format": fmt,
        "method": "mermaid-renderer",
        "file_size": os.path.getsize(output_path),
        "url": url,
    }
