from __future__ import annotations

import json
import re
import webbrowser
from dataclasses import dataclass, field
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


@dataclass(slots=True)
class BrowserAdapter:
    data_dir: Path
    fetch_timeout_seconds: int = 8
    provider: str = "external-browser"
    state_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.data_dir / "browser_state.json"

    def _load_state(self) -> dict:
        if not self.state_path.exists():
            return {
                "last_url": None,
                "last_opened_at": None,
                "last_fetched_at": None,
                "launch_count": 0,
                "fetch_count": 0,
                "mode": "external",
                "last_title": None,
            }
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save_state(self, state: dict) -> None:
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _normalize_url(self, url: str | None) -> str | None:
        clean = (url or "").strip()
        if not clean:
            return None
        if clean.startswith("file://"):
            return clean
        if "://" not in clean:
            clean = f"https://{clean}"
        return clean

    def _extract_text(self, html: str, max_chars: int = 2500) -> tuple[str | None, str, bool]:
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
        title = unescape(title_match.group(1).strip()) if title_match else None
        body = re.sub(r"<script.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
        body = re.sub(r"<style.*?</style>", " ", body, flags=re.IGNORECASE | re.DOTALL)
        body = re.sub(r"<[^>]+>", " ", body)
        body = unescape(re.sub(r"\s+", " ", body)).strip()
        truncated = len(body) > max_chars
        return title, body[:max_chars], truncated

    def open_url(self, url: str) -> dict:
        clean = self._normalize_url(url)
        if not clean:
            return {"ok": False, "error": "URL is required."}
        try:
            opened = webbrowser.open(clean, new=2, autoraise=True)
            state = self._load_state()
            state["last_url"] = clean
            state["last_opened_at"] = datetime.now(UTC).isoformat()
            state["launch_count"] = int(state.get("launch_count", 0)) + 1
            state["mode"] = "external"
            self._save_state(state)
            return {
                "ok": bool(opened),
                "provider": self.provider,
                "mode": "external",
                "url": clean,
                "state": state,
                "plain_english": "Attempted to open the URL in the real external browser.",
                "next_action": "Use /browser-fetch to inspect the remembered page content from BRAVO-1.",
            }
        except OSError as exc:
            return {"ok": False, "provider": self.provider, "url": clean, "error": str(exc)}

    def fetch_page(self, url: str | None = None, max_chars: int = 2500) -> dict:
        target = self._normalize_url(url) or self._load_state().get("last_url")
        if not target:
            return {"ok": False, "error": "No browser URL is available to fetch."}
        try:
            with urlopen(target, timeout=self.fetch_timeout_seconds) as response:
                raw = response.read().decode("utf-8", errors="replace")
            title, text, truncated = self._extract_text(raw, max_chars=max_chars)
            state = self._load_state()
            state["last_url"] = target
            state["last_title"] = title
            state["last_fetched_at"] = datetime.now(UTC).isoformat()
            state["fetch_count"] = int(state.get("fetch_count", 0)) + 1
            self._save_state(state)
            return {
                "ok": True,
                "provider": self.provider,
                "mode": "fetch",
                "url": target,
                "title": title,
                "text": text,
                "truncated": truncated,
                "state": state,
                "plain_english": "Fetched a lightweight text snapshot of the remembered browser page.",
            }
        except (URLError, OSError, ValueError) as exc:
            return {"ok": False, "provider": self.provider, "url": target, "error": str(exc)}

    def status(self) -> dict:
        state = self._load_state()
        return {
            "ok": True,
            "provider": self.provider,
            "mode": state.get("mode", "external"),
            "last_url": state.get("last_url"),
            "last_title": state.get("last_title"),
            "last_opened_at": state.get("last_opened_at"),
            "last_fetched_at": state.get("last_fetched_at"),
            "launch_count": state.get("launch_count", 0),
            "fetch_count": state.get("fetch_count", 0),
            "plain_english": "This is the current BRAVO-1 remembered browser state.",
            "next_action": "Use /browser <url> to open a page or /browser-fetch to inspect the remembered page.",
        }

    def inspect(self) -> dict:
        status = self.status()
        status["planned_capabilities"] = [
            "launch real browser session",
            "persist remembered browser state",
            "upgrade later into DOM extraction + action loop",
            "bridge into controlled browser mode later",
        ]
        status["plain_english"] = "This is the current browser adapter implementation + future browser operator shape."
        return status
