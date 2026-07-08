from __future__ import annotations

import json
import os
import signal
import subprocess
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

    def _runtime_state_dir(self) -> Path:
        path = self.settings.data_dir / "runtime"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _pid_path(self, lane: str) -> Path:
        return self._runtime_state_dir() / f"{lane}.pid"

    def _platform_profile_path(self, lane: str) -> Path:
        suffix = ".ps1" if os.name == "nt" else ".sh"
        return self._profile_path(f"llama-server-{lane}{suffix}")

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

    def _lane_status(self, lane: str, model: str, port: int) -> dict:
        base = f"http://{self.settings.runtime_host}:{port}"
        profile_ps1 = self._profile_path(f"llama-server-{lane}.ps1")
        profile_sh = self._profile_path(f"llama-server-{lane}.sh")
        pid_path = self._pid_path(lane)
        pid = pid_path.read_text(encoding="utf-8").strip() if pid_path.exists() else None
        return {
            "model": model,
            "port": port,
            "endpoint": f"{base}/v1/chat/completions",
            "profile_ps1": str(profile_ps1),
            "profile_ps1_exists": profile_ps1.exists(),
            "profile_sh": str(profile_sh),
            "profile_sh_exists": profile_sh.exists(),
            "active_profile": str(self._platform_profile_path(lane)),
            "health": self._ping_endpoint(base),
            "pid": pid,
            "pid_file": str(pid_path),
        }

    def status(self) -> dict:
        return {
            "ok": True,
            "host": self.settings.runtime_host,
            "fast": self._lane_status("fast", self.settings.fast_model, self.settings.runtime_fast_port),
            "main": self._lane_status("main", self.settings.main_model, self.settings.runtime_main_port),
            "plain_english": "This is the BRAVO-1 runtime bootstrap status for local GGUF serving.",
            "next_action": "Run the runtime profile scripts when you are ready to serve local models.",
        }

    def launch(self, lane: str) -> dict:
        clean_lane = lane.strip().lower()
        if clean_lane not in {"fast", "main"}:
            return {"ok": False, "error": f"Unknown runtime lane: {lane}"}
        profile = self._platform_profile_path(clean_lane)
        if not profile.exists():
            return {"ok": False, "error": f"Runtime profile not found: {profile}"}
        try:
            if os.name == "nt":
                proc = subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(profile)], cwd=str(self._project_root()))
            else:
                proc = subprocess.Popen(["bash", str(profile)], cwd=str(self._project_root()))
            self._pid_path(clean_lane).write_text(str(proc.pid), encoding="utf-8")
            return {
                "ok": True,
                "lane": clean_lane,
                "pid": proc.pid,
                "profile": str(profile),
                "plain_english": f"Attempted to launch the {clean_lane} runtime lane.",
            }
        except OSError as exc:
            return {"ok": False, "lane": clean_lane, "error": str(exc)}

    def stop(self, lane: str) -> dict:
        clean_lane = lane.strip().lower()
        if clean_lane not in {"fast", "main"}:
            return {"ok": False, "error": f"Unknown runtime lane: {lane}"}
        pid_path = self._pid_path(clean_lane)
        if not pid_path.exists():
            return {"ok": False, "lane": clean_lane, "error": "No PID file found for that lane."}
        pid = int(pid_path.read_text(encoding="utf-8").strip())
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False, capture_output=True, text=True)
            else:
                os.kill(pid, signal.SIGTERM)
            pid_path.unlink(missing_ok=True)
            return {
                "ok": True,
                "lane": clean_lane,
                "pid": pid,
                "plain_english": f"Attempted to stop the {clean_lane} runtime lane.",
            }
        except OSError as exc:
            return {"ok": False, "lane": clean_lane, "pid": pid, "error": str(exc)}
