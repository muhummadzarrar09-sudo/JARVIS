from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from bravo1.adapters.browser import BrowserAdapter
from bravo1.adapters.windows import WindowsAdapter
from bravo1.brain.obsidian import ObsidianBrain
from bravo1.config import Settings
from bravo1.core.project import ProjectContinuity
from bravo1.core.response import OperatorResponse
from bravo1.core.session import SessionManager, SessionState
from bravo1.core.state_store import StateStore
from bravo1.core.summary import SessionSummaryWriter
from bravo1.models.client import ModelClient
from bravo1.models.router import ModelRoute, ModelRouter
from bravo1.models.runtime import RuntimeBootstrap
from bravo1.prompts.loader import PromptPack
from bravo1.tools.registry import ToolRegistry
from bravo1.tools.shell import ShellTool


class Operator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_dirs()
        self.sessions = SessionManager(settings.session_dir)
        self.brain = ObsidianBrain(settings.brain_dir)
        self.router = ModelRouter(settings)
        self.runtime = RuntimeBootstrap(settings)
        self.project = ProjectContinuity(settings.data_dir)
        self.shell = ShellTool(timeout_seconds=settings.shell_timeout_seconds, default_cwd=settings.data_dir.parent)
        self.browser = BrowserAdapter(settings.data_dir / "browser", fetch_timeout_seconds=settings.browser_fetch_timeout_seconds)
        self.windows = WindowsAdapter()
        prompt_dir = Path(__file__).resolve().parents[1] / "prompts"
        self.prompts = PromptPack(prompt_dir)
        self.tools = ToolRegistry(self.sessions, self.brain, self.runtime, self.project, self.shell, self.browser, self.windows)
        self.summaries = SessionSummaryWriter(settings.summary_dir)
        self.state_store = StateStore(settings.data_dir)
        self.model_client = ModelClient(timeout_seconds=settings.model_request_timeout_seconds)

    def state_snapshot(self) -> dict[str, Any]:
        state = self.sessions.load()
        self.brain.bootstrap()
        snapshot = {
            "ok": True,
            "session": self.sessions.snapshot(state),
            "project": self.project.inspect(),
            "runtime": self.runtime.status(),
            "browser": self.browser.status(),
            "windows": self.windows.status(),
        }
        self.state_store.save(snapshot)
        return snapshot

    def handle(self, message: str) -> dict[str, Any]:
        state = self.sessions.load()
        self.brain.bootstrap()

        if message.strip().startswith("/"):
            response = self._handle_slash_command(state, message.strip())
            self.sessions.append_message(state, "assistant", response.reply)
            self.state_snapshot()
            return response.to_dict()

        self.sessions.append_message(state, "user", message)
        route = self.router.route(self._task_type_for(message))
        primary_action = self._pick_primary_action(message, state)
        state.last_primary_action = primary_action
        self.project.sync_from_session(state)
        self.brain.sync_from_session(state, primary_action)
        active_context = self.brain.read_active()
        reply, model_meta = self._generate_operator_reply(state, route, primary_action, active_context, message)

        self.sessions.append_message(state, "assistant", reply)
        self._maybe_auto_summarize(state, active_context)
        self.sessions.save(state)
        response = OperatorResponse(
            ok=True,
            session_id=state.session_id,
            kind="chat",
            primary_action=primary_action,
            route=asdict(route),
            reply=reply,
            data={
                "model": model_meta,
                "project": self.project.inspect(),
                "session": self.sessions.snapshot(state),
                "browser": self.browser.status(),
                "windows": self.windows.status(),
            },
        )
        self.state_snapshot()
        return response.to_dict()

    def _task_type_for(self, message: str) -> str:
        lowered = message.lower()
        if lowered.startswith("/"):
            return "tool"
        if any(token in lowered for token in ["now", "next", "brief", "summary"]):
            return "brief"
        return "main"

    def _pick_primary_action(self, message: str, state: SessionState) -> str:
        lowered = message.lower()
        if "browser" in lowered:
            return "design the browser operator adapter"
        if "project" in lowered:
            return "stabilize project continuity structure"
        if "runtime" in lowered or "model" in lowered:
            return "wire the local GGUF runtime bootstrap"
        if state.current_goal:
            return state.current_goal
        return "define the next core loop"

    def _generate_operator_reply(
        self,
        state: SessionState,
        route: ModelRoute,
        primary_action: str,
        active_context: str,
        user_message: str,
    ) -> tuple[str, dict[str, Any]]:
        system_prompt = self.prompts.system_operator()
        user_prompt = (
            f"Session ID: {state.session_id}\n"
            f"Current project: {state.current_project or 'BRAVO-1 rebuild'}\n"
            f"Current goal: {state.current_goal or 'not set'}\n"
            f"Primary action: {primary_action}\n"
            f"Remembered browser: {self.browser.status().get('last_url') or 'not set'}\n\n"
            f"Active context:\n{active_context[:1200]}\n\n"
            f"User message:\n{user_message}"
        )
        result = self.model_client.generate(route, system_prompt, user_prompt)
        if result.get("ok") and result.get("content"):
            lines = [
                f"Primary action: {primary_action}",
                f"Project: {state.current_project or 'BRAVO-1 rebuild'}",
                "",
                result["content"],
            ]
            return "\n".join(lines), result

        return self._build_fallback_reply(state, route, primary_action, active_context, result.get("error")), result

    def _build_fallback_reply(
        self,
        state: SessionState,
        route: ModelRoute,
        primary_action: str,
        active_context: str,
        model_error: str | None,
    ) -> str:
        lines = [
            "BRAVO-1 operator scaffold online.",
            f"Session: {state.session_id}",
            f"Route: {route.lane} -> {route.model_name}",
            f"Primary action: {primary_action}",
            f"Project: {state.current_project or 'BRAVO-1 rebuild'}",
            f"Goal: {state.current_goal or 'not set'}",
        ]
        if model_error:
            lines.append(f"Model status: local runtime unavailable ({model_error})")
        lines.extend(["", self.prompts.fallback_footer(), "", "Active context preview:", active_context[:500]])
        return "\n".join(lines)

    def _handle_slash_command(self, state: SessionState, raw: str) -> OperatorResponse:
        parts = raw.split(maxsplit=1)
        command = parts[0].lower()
        argument = parts[1].strip() if len(parts) > 1 else ""
        kind = "command"
        payload: dict[str, Any] = {}

        if command == "/help":
            reply = self._help_text()
        elif command == "/brief":
            reply = self._brief_text(state)
            kind = "brief"
        elif command == "/session":
            snapshot = self.sessions.snapshot(state)
            payload = {"session": snapshot}
            reply = self._format_session_snapshot(snapshot)
            kind = "session"
        elif command == "/active":
            context = self.brain.read_active()
            payload = {"active_context": context}
            reply = f"Active brain context\n\n{context}"
            kind = "brain"
        elif command == "/tools":
            tools = [asdict(tool) for tool in self.tools.list_tools()]
            payload = {"tools": tools}
            reply = self._format_tools_list(tools)
            kind = "tools"
        elif command == "/tool":
            if not argument:
                reply = "Usage: /tool <tool_name>"
            else:
                result = self.tools.execute(argument, state=state)
                payload = {"tool_result": result}
                reply = self._format_tool_result(argument, result)
                kind = "tool"
        elif command == "/run":
            if not argument:
                reply = "Usage: /run <shell command>"
            else:
                candidate_cwd = state.current_project or None
                if candidate_cwd and not self._looks_like_real_dir(candidate_cwd):
                    candidate_cwd = None
                result = self.shell.run(argument, cwd=candidate_cwd)
                payload = {"shell": result}
                reply = self._format_shell_result(result)
                kind = "shell"
        elif command == "/runtime":
            runtime_status = self.runtime.status()
            payload = {"runtime": runtime_status}
            reply = self._format_runtime_status(runtime_status)
            kind = "runtime"
        elif command == "/web-health":
            runtime_status = self.runtime.status()
            payload = {"runtime": runtime_status}
            reply = self._format_runtime_health(runtime_status)
            kind = "runtime"
        elif command == "/runtime-start":
            lane = argument or "fast"
            result = self.runtime.launch(lane)
            payload = {"runtime": result}
            reply = self._format_runtime_action("start", result)
            kind = "runtime"
        elif command == "/runtime-stop":
            lane = argument or "fast"
            result = self.runtime.stop(lane)
            payload = {"runtime": result}
            reply = self._format_runtime_action("stop", result)
            kind = "runtime"
        elif command == "/setgoal":
            if not argument:
                reply = "Usage: /setgoal <goal text>"
            else:
                self.sessions.set_goal(state, argument)
                state.last_primary_action = argument
                self.project.sync_from_session(state)
                self.brain.sync_from_session(state, argument)
                payload = {"goal": argument}
                reply = f"Goal set: {argument}"
        elif command == "/project":
            if not argument:
                continuity = self.project.inspect()
                payload = {"project": continuity}
                reply = self._format_project_inspect(continuity)
                kind = "project"
            else:
                self.sessions.set_project(state, argument)
                self.project.sync_from_session(state)
                self.brain.sync_from_session(state, state.last_primary_action or "stabilize project continuity structure")
                payload = {"project": argument}
                reply = f"Project set: {argument}"
                kind = "project"
        elif command == "/summarize":
            path = self.summaries.write(state, trigger="slash_command", active_context=self.brain.read_active(), project_snapshot=self.project.inspect())
            state.last_summary_path = str(path)
            self.sessions.save(state)
            self.project.sync_from_session(state)
            payload = {"summary_path": str(path)}
            reply = f"Session summary written: {path}"
            kind = "summary"
        elif command == "/browser":
            if not argument:
                browser_status = self.browser.inspect()
                payload = {"browser": browser_status}
                reply = self._format_browser_status(browser_status)
            else:
                result = self.browser.open_url(argument)
                payload = {"browser": result}
                reply = self._format_browser_action(result)
            kind = "browser"
        elif command == "/browser-controlled":
            if not argument:
                browser_status = self.browser.inspect()
                payload = {"browser": browser_status}
                reply = self._format_browser_status(browser_status)
            else:
                result = self.browser.open_url_controlled(argument)
                payload = {"browser": result}
                reply = self._format_browser_action(result)
            kind = "browser"
        elif command == "/browser-fetch":
            result = self.browser.fetch_page(argument or None)
            payload = {"browser": result}
            reply = self._format_browser_fetch(result)
            kind = "browser"
        elif command == "/browser-status":
            browser_status = self.browser.inspect()
            payload = {"browser": browser_status}
            reply = self._format_browser_status(browser_status)
            kind = "browser"
        elif command == "/windows-status":
            windows_status = self.windows.inspect()
            payload = {"windows": windows_status}
            reply = self._format_windows_status(windows_status)
            kind = "windows"
        elif command == "/windows-find":
            result = self.windows.find_windows(argument)
            payload = {"windows": result}
            reply = self._format_windows_find(result)
            kind = "windows"
        elif command == "/windows-focus":
            result = self.windows.focus_window(argument)
            payload = {"windows": result}
            reply = self._format_windows_focus(result)
            kind = "windows"
        elif command in {"/note", "/idea", "/blocker", "/followup"}:
            if not argument:
                reply = f"Usage: {command} <text>"
            else:
                capture_kind = command.lstrip("/")
                result = self.project.capture(state, capture_kind, argument)
                payload = {"capture": result}
                reply = self._format_capture_result(result)
                kind = "capture"
        elif command == "/capture":
            capture_parts = argument.split(maxsplit=1)
            if len(capture_parts) < 2:
                reply = "Usage: /capture <kind> <text>"
            else:
                capture_kind, capture_text = capture_parts[0], capture_parts[1]
                result = self.project.capture(state, capture_kind, capture_text)
                payload = {"capture": result}
                reply = self._format_capture_result(result)
                kind = "capture"
        elif command == "/captures":
            continuity = self.project.inspect()
            payload = {"project": continuity}
            reply = self._format_project_inspect(continuity)
            kind = "capture"
        else:
            reply = f"Unknown command: {command}. Try /help"

        return OperatorResponse(
            ok=True,
            session_id=state.session_id,
            kind=kind,
            primary_action=state.last_primary_action,
            route={},
            reply=reply,
            data=payload,
        )

    def _help_text(self) -> str:
        return "\n".join(
            [
                "BRAVO-1 slash commands",
                "",
                "/help — show this help",
                "/brief — show the current operator brief",
                "/session — inspect the active session",
                "/active — show active brain context",
                "/tools — list available Week-1 tools",
                "/tool <name> — execute a Week-1 tool",
                "/run <command> — execute a local shell command",
                "/runtime — inspect local GGUF runtime bootstrap status",
                "/web-health — quick runtime reachability check",
                "/runtime-start [fast|main] — start a runtime lane",
                "/runtime-stop [fast|main] — stop a runtime lane",
                "/browser <url> — open a URL in the external browser",
                "/browser-controlled <url> — prepare the controlled browser lane",
                "/browser-fetch [url] — fetch a lightweight text snapshot of the remembered page",
                "/browser-status — inspect remembered browser state",
                "/windows-status — inspect Windows adapter status",
                "/windows-find <text> — search titled windows by text",
                "/windows-focus <title> — attempt to focus a window title",
                "/setgoal <text> — set the current goal",
                "/project <text> — set or inspect current project continuity",
                "/summarize — write a session summary markdown file",
                "/note <text> — capture a project note",
                "/idea <text> — capture a project idea",
                "/blocker <text> — capture a project blocker",
                "/followup <text> — capture a project follow-up",
                "/capture <kind> <text> — generic project capture",
                "/captures — inspect recent captures",
            ]
        )

    def _brief_text(self, state: SessionState) -> str:
        active = self.brain.read_active()
        route = self.router.route("brief")
        continuity = self.project.inspect()
        primary_action = state.last_primary_action or state.current_goal or "define the next core loop"
        lines = [
            "BRAVO-1 brief",
            "",
            f"Primary action: {primary_action}",
            f"Project: {continuity.get('current_project') or state.current_project or 'not set'}",
            f"Goal: {continuity.get('current_goal') or state.current_goal or 'not set'}",
            f"Route: {route.lane} -> {route.model_name}",
            f"Remembered browser: {self.browser.status().get('last_url') or 'not set'}",
        ]
        captures = continuity.get("recent_captures") or []
        if captures:
            lines.extend(["", "Recent captures:"])
            for item in captures[:3]:
                lines.append(f"- {item.get('kind')}: {item.get('text')}")
        lines.extend(["", "Active context:", active[:500]])
        return "\n".join(lines)

    def _format_session_snapshot(self, snapshot: dict[str, Any]) -> str:
        return "\n".join(
            [
                "Session snapshot",
                f"- session_id: {snapshot.get('session_id')}",
                f"- current_goal: {snapshot.get('current_goal') or 'not set'}",
                f"- current_project: {snapshot.get('current_project') or 'not set'}",
                f"- last_primary_action: {snapshot.get('last_primary_action') or 'not set'}",
                f"- last_summary_path: {snapshot.get('last_summary_path') or 'not set'}",
                f"- recent_messages: {len(snapshot.get('recent_messages') or [])}",
            ]
        )

    def _format_tools_list(self, tools: list[dict[str, Any]]) -> str:
        lines = ["Available tools", ""]
        for tool in tools:
            lines.append(f"- {tool.get('name')} ({tool.get('risk')}) — {tool.get('description')}")
        return "\n".join(lines)

    def _format_tool_result(self, tool_name: str, result: dict[str, Any]) -> str:
        lines = [f"Tool result: {tool_name}"]
        if result.get("plain_english"):
            lines.append(result["plain_english"])
        if result.get("error"):
            lines.append(f"Error: {result['error']}")
        if result.get("snapshot"):
            lines.append(self._format_session_snapshot(result["snapshot"]))
        if result.get("active_context"):
            lines.append("\n" + result["active_context"][:600])
        if result.get("current_project"):
            lines.append(f"Project: {result.get('current_project')}")
        if result.get("fast") and result.get("main"):
            lines.append(f"Fast: {result.get('fast', {}).get('model')} @ {result.get('fast', {}).get('endpoint')}")
            lines.append(f"Main: {result.get('main', {}).get('model')} @ {result.get('main', {}).get('endpoint')}")
        return "\n".join(lines)

    def _format_shell_result(self, result: dict[str, Any]) -> str:
        lines = [f"Shell command: {result.get('command')}", f"Working directory: {result.get('cwd')}"]
        if result.get("ok"):
            lines.append(f"Return code: {result.get('returncode')}")
            if result.get("stdout"):
                lines.append("\nstdout:\n" + result["stdout"])
            if result.get("stderr"):
                lines.append("\nstderr:\n" + result["stderr"])
        else:
            lines.append(f"Error: {result.get('error') or result.get('stderr') or 'command failed'}")
        return "\n".join(lines)

    def _format_runtime_status(self, runtime_status: dict[str, Any]) -> str:
        fast = runtime_status.get("fast", {})
        main = runtime_status.get("main", {})
        lines = [
            "Runtime status",
            f"Fast: {fast.get('model')} @ {fast.get('endpoint')}",
            f"Main: {main.get('model')} @ {main.get('endpoint')}",
            f"Fast profile exists: {fast.get('profile_ps1_exists') or fast.get('profile_sh_exists')}",
            f"Main profile exists: {main.get('profile_ps1_exists') or main.get('profile_sh_exists')}",
        ]
        return "\n".join(lines)

    def _format_runtime_health(self, runtime_status: dict[str, Any]) -> str:
        fast = runtime_status.get("fast", {})
        main = runtime_status.get("main", {})
        fast_health = fast.get("health", {})
        main_health = main.get("health", {})
        return "\n".join(
            [
                "Runtime reachability",
                f"Fast lane: {'reachable' if fast_health.get('ok') else 'offline'}",
                f"Main lane: {'reachable' if main_health.get('ok') else 'offline'}",
                f"Fast endpoint: {fast.get('endpoint')}",
                f"Main endpoint: {main.get('endpoint')}",
            ]
        )

    def _format_runtime_action(self, action: str, result: dict[str, Any]) -> str:
        if result.get("ok"):
            return f"Runtime {action} requested for lane: {result.get('lane')} (pid: {result.get('pid', 'n/a')})"
        return f"Runtime {action} failed: {result.get('error') or 'unknown error'}"

    def _format_project_inspect(self, continuity: dict[str, Any]) -> str:
        lines = [
            "Project continuity",
            f"Project: {continuity.get('current_project') or 'not set'}",
            f"Goal: {continuity.get('current_goal') or 'not set'}",
            f"Last primary action: {continuity.get('last_primary_action') or 'not set'}",
            f"Last summary: {continuity.get('last_summary_path') or 'not set'}",
        ]
        captures = continuity.get("recent_captures") or []
        if captures:
            lines.append("Recent captures:")
            for item in captures[:5]:
                lines.append(f"- {item.get('kind')}: {item.get('text')}")
        return "\n".join(lines)

    def _format_capture_result(self, result: dict[str, Any]) -> str:
        if not result.get("ok"):
            return result.get("error") or "Capture failed."
        capture = result.get("capture", {})
        lines = [
            result.get("plain_english") or "Capture saved.",
            f"Project: {capture.get('project')}",
            f"Kind: {capture.get('kind')}",
            f"Text: {capture.get('text')}",
        ]
        recent = result.get("recent_captures") or []
        if recent:
            lines.append("Recent captures:")
            for item in recent[:3]:
                lines.append(f"- {item.get('kind')}: {item.get('text')}")
        return "\n".join(lines)

    def _format_browser_status(self, status: dict[str, Any]) -> str:
        lines = [
            "Browser status",
            f"Provider: {status.get('provider')}",
            f"Mode: {status.get('mode')}",
            f"Last URL: {status.get('last_url') or 'not set'}",
            f"Last opened at: {status.get('last_opened_at') or 'not set'}",
            f"Launch count: {status.get('launch_count', 0)}",
        ]
        planned = status.get('planned_capabilities') or []
        if planned:
            lines.append("Planned:")
            lines.extend(f"- {item}" for item in planned[:4])
        return "\n".join(lines)

    def _format_browser_action(self, result: dict[str, Any]) -> str:
        if result.get("ok"):
            return f"Opened browser URL: {result.get('url')}"
        next_action = result.get("next_action")
        if next_action:
            return f"Browser action failed: {result.get('error') or 'unknown error'}\nNext: {next_action}"
        return f"Browser action failed: {result.get('error') or 'unknown error'}"

    def _format_browser_fetch(self, result: dict[str, Any]) -> str:
        if not result.get("ok"):
            return f"Browser fetch failed: {result.get('error') or 'unknown error'}"
        lines = [
            "Browser fetch",
            f"URL: {result.get('url')}",
            f"Title: {result.get('title') or 'not set'}",
            "",
            result.get('text') or '(empty)',
        ]
        return "\n".join(lines)

    def _format_windows_status(self, status: dict[str, Any]) -> str:
        lines = [
            "Windows adapter status",
            f"Provider: {status.get('provider')}",
            f"Platform: {status.get('platform')}",
            f"is_windows: {status.get('is_windows')}",
            f"pywinauto_installed: {status.get('pywinauto_installed')}",
            f"pyautogui_installed: {status.get('pyautogui_installed')}",
            f"window_count: {status.get('window_count', 0)}",
        ]
        planned = status.get('planned_capabilities') or []
        if planned:
            lines.append("Planned:")
            lines.extend(f"- {item}" for item in planned[:4])
        return "\n".join(lines)

    def _format_windows_find(self, result: dict[str, Any]) -> str:
        if not result.get("ok"):
            return f"Window search failed: {result.get('error') or 'unknown error'}"
        lines = [f"Window search: {result.get('query')}", f"Matches: {result.get('count', 0)}"]
        for item in (result.get('items') or [])[:5]:
            lines.append(f"- {item.get('ProcessName')}: {item.get('MainWindowTitle')}")
        return "\n".join(lines)

    def _format_windows_focus(self, result: dict[str, Any]) -> str:
        if result.get("ok"):
            return f"Attempted to focus window: {result.get('title')}"
        return f"Window focus failed: {result.get('error') or 'unknown error'}"

    def _looks_like_real_dir(self, value: str) -> bool:
        candidate = Path(value).expanduser()
        return candidate.exists() and candidate.is_dir()

    def _maybe_auto_summarize(self, state: SessionState, active_context: str) -> None:
        interval = self.settings.auto_summary_message_interval
        if interval <= 0:
            return
        message_count = len(state.recent_messages)
        if message_count == 0 or message_count % interval != 0:
            return
        path = self.summaries.write(
            state,
            trigger="auto_interval",
            active_context=active_context,
            project_snapshot=self.project.inspect(),
        )
        state.last_summary_path = str(path)
        self.project.sync_from_session(state)
