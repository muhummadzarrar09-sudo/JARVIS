from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from bravo1.brain.obsidian import ObsidianBrain
from bravo1.config import Settings
from bravo1.core.project import ProjectContinuity
from bravo1.core.session import SessionManager, SessionState
from bravo1.core.summary import SessionSummaryWriter
from bravo1.models.client import ModelClient
from bravo1.models.router import ModelRoute, ModelRouter
from bravo1.models.runtime import RuntimeBootstrap
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
        self.tools = ToolRegistry(self.sessions, self.brain, self.runtime, self.project, self.shell)
        self.summaries = SessionSummaryWriter(settings.summary_dir)
        self.model_client = ModelClient(timeout_seconds=settings.model_request_timeout_seconds)

    def handle(self, message: str) -> dict[str, Any]:
        state = self.sessions.load()
        self.brain.bootstrap()

        if message.strip().startswith("/"):
            result = self._handle_slash_command(state, message.strip())
            self.sessions.append_message(state, "assistant", result["reply"])
            return result

        self.sessions.append_message(state, "user", message)
        route = self.router.route(self._task_type_for(message))
        primary_action = self._pick_primary_action(message, state)
        state.last_primary_action = primary_action
        self.project.sync_from_session(state)
        self.brain.sync_from_session(state, primary_action)
        active_context = self.brain.read_active()
        reply = self._generate_operator_reply(state, route, primary_action, active_context, message)

        self.sessions.append_message(state, "assistant", reply)
        self.sessions.save(state)
        return {
            "ok": True,
            "session_id": state.session_id,
            "primary_action": primary_action,
            "route": asdict(route),
            "reply": reply,
        }

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
    ) -> str:
        system_prompt = (
            "You are BRAVO-1, a calm local-first executive operator shell. "
            "Respond briefly, clearly, and in an operator tone. Use the provided active context."
        )
        user_prompt = (
            f"Session ID: {state.session_id}\n"
            f"Current project: {state.current_project or 'BRAVO-1 rebuild'}\n"
            f"Current goal: {state.current_goal or 'not set'}\n"
            f"Primary action: {primary_action}\n\n"
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
            return "\n".join(lines)

        return self._build_fallback_reply(state, route, primary_action, active_context, result.get("error"))

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
        lines.extend(
            [
                "",
                "Fast commands:",
                "/help, /brief, /session, /active, /tools, /runtime, /summarize",
                "/setgoal <text>, /project <text>, /tool <name>, /run <command>",
                "",
                "Active context preview:",
                active_context[:500],
            ]
        )
        return "\n".join(lines)

    def _handle_slash_command(self, state: SessionState, raw: str) -> dict[str, Any]:
        parts = raw.split(maxsplit=1)
        command = parts[0].lower()
        argument = parts[1].strip() if len(parts) > 1 else ""

        if command == "/help":
            reply = self._help_text()
        elif command == "/brief":
            reply = self._brief_text(state)
        elif command == "/session":
            snapshot = self.sessions.snapshot(state)
            reply = "Session snapshot:\n" + json.dumps(snapshot, ensure_ascii=False, indent=2)
        elif command == "/active":
            reply = self.brain.read_active()
        elif command == "/tools":
            items = [f"- {tool.name} ({tool.risk}) — {tool.description}" for tool in self.tools.list_tools()]
            reply = "Available tools:\n" + "\n".join(items)
        elif command == "/tool":
            if not argument:
                reply = "Usage: /tool <tool_name>"
            else:
                result = self.tools.execute(argument, state=state)
                reply = json.dumps(result, ensure_ascii=False, indent=2)
        elif command == "/run":
            if not argument:
                reply = "Usage: /run <shell command>"
            else:
                candidate_cwd = state.current_project or None
                if candidate_cwd and not self._looks_like_real_dir(candidate_cwd):
                    candidate_cwd = None
                result = self.shell.run(argument, cwd=candidate_cwd)
                reply = json.dumps(result, ensure_ascii=False, indent=2)
        elif command == "/runtime":
            reply = json.dumps(self.runtime.status(), ensure_ascii=False, indent=2)
        elif command == "/setgoal":
            if not argument:
                reply = "Usage: /setgoal <goal text>"
            else:
                self.sessions.set_goal(state, argument)
                state.last_primary_action = argument
                self.project.sync_from_session(state)
                self.brain.sync_from_session(state, argument)
                reply = f"Goal set: {argument}"
        elif command == "/project":
            if not argument:
                continuity = self.project.inspect()
                reply = json.dumps(continuity, ensure_ascii=False, indent=2)
            else:
                self.sessions.set_project(state, argument)
                self.project.sync_from_session(state)
                self.brain.sync_from_session(state, state.last_primary_action or "stabilize project continuity structure")
                reply = f"Project set: {argument}"
        elif command == "/summarize":
            path = self.summaries.write(state, trigger="slash_command")
            state.last_summary_path = str(path)
            self.sessions.save(state)
            self.project.sync_from_session(state)
            reply = f"Session summary written: {path}"
        else:
            reply = f"Unknown command: {command}. Try /help"

        return {
            "ok": True,
            "session_id": state.session_id,
            "reply": reply,
        }

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
                "/setgoal <text> — set the current goal",
                "/project <text> — set or inspect current project continuity",
                "/summarize — write a session summary markdown file",
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
            "",
            "Active context:",
            active[:500],
        ]
        return "\n".join(lines)

    def _looks_like_real_dir(self, value: str) -> bool:
        from pathlib import Path

        candidate = Path(value).expanduser()
        return candidate.exists() and candidate.is_dir()
