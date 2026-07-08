from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from bravo1.config import Settings


@dataclass(slots=True)
class RuntimeBootstrap:
    settings: Settings

    def _project_root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    def _profile_path(self, name: str) -> Path:
        return self._project_root() / "runtime" / "profiles" / name

    def _ping_endpoint(self, base_url: str) -> dict:
        checks = [f"{base_url}/health", f"{base_url}/v1/models"]
        last_error = "unreachable"
        for url in checks:
            try:
                with urlopen(url, timeout=2) as response:
                    body = response.read().decode("utf-8")
                parsed: dict | str
                try:
                    parsed = json.loads(body) if body else {}
                except json.JSONDecodeError:
                    parsed = body[:300]
                return {"ok": True, "url": url, "status_code": 200, "response": parsed}
            except URLError as exc:
                last_error = str(exc)
            except OSError as exc:
                last_error = str(exc)
        return {"ok": False, "error": last_error}

    def status(self) -> dict:
        fast_profile = self._profile_path("llama-server-fast.ps1")
        main_profile = self._profile_path("llama-server-main.ps1")
        fast_base = f"http://{self.settings.runtime_host}:{self.settings.runtime_fast_port}"
        main_base = f"http://{self.settings.runtime_host}:{self.settings.runtime_main_port}"
        fast_health = self._ping_endpoint(fast_base)
        main_health = self._ping_endpoint(main_base)
        return {
            "ok": True,
            "host": self.settings.runtime_host,
            "fast": {
                "model": self.settings.fast_model,
                "port": self.settings.runtime_fast_port,
                "endpoint": f"{fast_base}/v1/chat/completions",
                "profile": str(fast_profile),
                "profile_exists": fast_profile.exists(),
                "health": fast_health,
            },
            "main": {
                "model": self.settings.main_model,
                "port": self.settings.runtime_main_port,
                "endpoint": f"{main_base}/v1/chat/completions",
                "profile": str(main_profile),
                "profile_exists": main_profile.exists(),
                "health": main_health,
            },
            "plain_english": "This is the BRAVO-1 runtime bootstrap status for local GGUF serving.",
            "next_action": "Run the runtime profile scripts when you are ready to serve local models.",
        }
