from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from bravo1.adapters.browser import BrowserAdapter
from bravo1.adapters.windows import WindowsAdapter
from bravo1.brain.obsidian import ObsidianBrain
from bravo1.core.project import ProjectContinuity
from bravo1.core.session import SessionManager, SessionState
from bravo1.models.runtime import RuntimeBootstrap
from bravo1.tools.shell import ShellTool


@dataclass(slots=True)
class ToolSpec:
    name: str
    description: str
    risk: str


class ToolRegistry:
    def __init__(
        self,
        sessions: SessionManager,
        brain: ObsidianBrain,
        runtime: RuntimeBootstrap,
        project: ProjectContinuity,
        shell: ShellTool,
        browser: BrowserAdapter | None = None,
        windows: WindowsAdapter | None = None,
    ) -> None:
        self.sessions = sessions
        self.brain = brain
        self.runtime = runtime
        self.project = project
        self.shell = shell
        self.browser = browser
        self.windows = windows
        self._tools = [
            ToolSpec(name="session.inspect", description="Inspect current session state", risk="low"),
            ToolSpec(name="brain.read_active", description="Read active brain context", risk="low"),
            ToolSpec(name="runtime.inspect", description="Inspect local runtime bootstrap status", risk="low"),
            ToolSpec(name="project.inspect", description="Inspect current project continuity state", risk="low"),
            ToolSpec(name="browser.inspect", description="Inspect remembered browser adapter state", risk="low"),
            ToolSpec(name="windows.inspect", description="Inspect current Windows adapter status", risk="low"),
        ]
        self._handlers: dict[str, Callable[[SessionState], dict[str, Any]]] = {
            "session.inspect": self._session_inspect,
            "brain.read_active": self._brain_read_active,
            "runtime.inspect": self._runtime_inspect,
            "project.inspect": self._project_inspect,
            "browser.inspect": self._browser_inspect,
            "windows.inspect": self._windows_inspect,
        }

    def list_tools(self) -> list[ToolSpec]:
        return list(self._tools)

    def execute(self, tool_name: str, state: SessionState, **_: Any) -> dict[str, Any]:
        handler = self._handlers.get(tool_name)
        if not handler:
            return {
                "ok": False,
                "tool": tool_name,
                "error": "Unknown tool in the Week-1 scaffold.",
            }
        result = handler(state)
        result.setdefault("tool", tool_name)
        return result

    def _session_inspect(self, state: SessionState) -> dict[str, Any]:
        return {
            "ok": True,
            "snapshot": self.sessions.snapshot(state),
            "plain_english": "This is the current BRAVO-1 session snapshot.",
        }

    def _brain_read_active(self, _: SessionState) -> dict[str, Any]:
        return {
            "ok": True,
            "active_context": self.brain.read_active(),
            "plain_english": "This is the active brain context currently injected into BRAVO-1 turns.",
        }

    def _runtime_inspect(self, _: SessionState) -> dict[str, Any]:
        return self.runtime.status()

    def _project_inspect(self, _: SessionState) -> dict[str, Any]:
        return self.project.inspect()

    def _browser_inspect(self, _: SessionState) -> dict[str, Any]:
        if self.browser is None:
            return {"ok": False, "error": "Browser adapter is not attached."}
        return self.browser.inspect()

    def _windows_inspect(self, _: SessionState) -> dict[str, Any]:
        if self.windows is None:
            return {"ok": False, "error": "Windows adapter is not attached."}
        return self.windows.inspect()
