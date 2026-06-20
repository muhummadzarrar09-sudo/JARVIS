import csv
import io
import json
import platform
import subprocess
from typing import Any

from app.core.config import settings


class ProcessTool:
    def _windows(self) -> bool:
        return platform.system().lower().startswith("win")

    def list_processes(self, filter_name: str | None = None) -> dict[str, Any]:
        if not settings.allow_process_tool:
            return {"ok": False, "error": "Process tool is disabled in config."}

        try:
            if self._windows():
                completed = subprocess.run(
                    ["tasklist", "/FO", "CSV", "/NH"],
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                if completed.returncode != 0:
                    return {"ok": False, "error": completed.stderr or completed.stdout}
                reader = csv.reader(io.StringIO(completed.stdout))
                items = []
                for row in reader:
                    if len(row) < 5:
                        continue
                    item = {
                        "image_name": row[0],
                        "pid": row[1],
                        "session_name": row[2],
                        "session_num": row[3],
                        "mem_usage": row[4],
                    }
                    if filter_name and filter_name.lower() not in item["image_name"].lower():
                        continue
                    items.append(item)
                return {"ok": True, "count": len(items), "items": items[:200]}

            completed = subprocess.run(
                ["ps", "-eo", "pid,comm"],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if completed.returncode != 0:
                return {"ok": False, "error": completed.stderr or completed.stdout}
            lines = completed.stdout.splitlines()[1:]
            items = []
            for line in lines:
                parts = line.strip().split(maxsplit=1)
                if len(parts) != 2:
                    continue
                item = {"pid": parts[0], "command": parts[1]}
                if filter_name and filter_name.lower() not in item["command"].lower():
                    continue
                items.append(item)
            return {"ok": True, "count": len(items), "items": items[:200]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def list_windows(self) -> dict[str, Any]:
        if not settings.allow_process_tool:
            return {"ok": False, "error": "Process tool is disabled in config."}

        if not self._windows():
            return {"ok": False, "error": "Window enumeration currently targets Windows first."}

        script = (
            "Get-Process | Where-Object {$_.MainWindowTitle} | "
            "Select-Object Id, ProcessName, MainWindowTitle | ConvertTo-Json -Depth 2"
        )
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if completed.returncode != 0:
                return {"ok": False, "error": completed.stderr or completed.stdout}
            raw = completed.stdout.strip()
            if not raw:
                return {"ok": True, "count": 0, "items": []}
            items = json.loads(raw)
            if isinstance(items, dict):
                items = [items]
            return {"ok": True, "count": len(items), "items": items[:200]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def start_process(self, command: str) -> dict[str, Any]:
        if not settings.allow_process_tool:
            return {"ok": False, "error": "Process tool is disabled in config."}
        if not command.strip():
            return {"ok": False, "error": "Command is required."}
        try:
            proc = subprocess.Popen(command, shell=True)
            return {"ok": True, "command": command, "pid": proc.pid}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def kill_process(self, target: str) -> dict[str, Any]:
        if not settings.allow_process_tool:
            return {"ok": False, "error": "Process tool is disabled in config."}
        if not target.strip():
            return {"ok": False, "error": "Target is required."}
        try:
            if self._windows():
                args = ["taskkill", "/F"]
                if target.isdigit():
                    args += ["/PID", target]
                else:
                    args += ["/IM", target]
                completed = subprocess.run(args, capture_output=True, text=True, timeout=20)
                return {
                    "ok": completed.returncode == 0,
                    "target": target,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }

            if target.isdigit():
                completed = subprocess.run(["kill", "-9", target], capture_output=True, text=True, timeout=20)
            else:
                completed = subprocess.run(["pkill", "-f", target], capture_output=True, text=True, timeout=20)
            return {
                "ok": completed.returncode == 0,
                "target": target,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}


process_tool = ProcessTool()
