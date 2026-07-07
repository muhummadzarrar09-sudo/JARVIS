from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bravo1.config import Settings


@dataclass(slots=True)
class RuntimeBootstrap:
    settings: Settings

    def _project_root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    def _profile_path(self, name: str) -> Path:
        return self._project_root() / "runtime" / "profiles" / name

    def status(self) -> dict:
        fast_profile = self._profile_path("llama-server-fast.ps1")
        main_profile = self._profile_path("llama-server-main.ps1")
        return {
            "ok": True,
            "host": self.settings.runtime_host,
            "fast": {
                "model": self.settings.fast_model,
                "port": self.settings.runtime_fast_port,
                "endpoint": f"http://{self.settings.runtime_host}:{self.settings.runtime_fast_port}/v1/chat/completions",
                "profile": str(fast_profile),
                "profile_exists": fast_profile.exists(),
            },
            "main": {
                "model": self.settings.main_model,
                "port": self.settings.runtime_main_port,
                "endpoint": f"http://{self.settings.runtime_host}:{self.settings.runtime_main_port}/v1/chat/completions",
                "profile": str(main_profile),
                "profile_exists": main_profile.exists(),
            },
            "plain_english": "This is the BRAVO-1 runtime bootstrap status for local GGUF serving.",
            "next_action": "Run the runtime profile scripts when you are ready to serve local models.",
        }
