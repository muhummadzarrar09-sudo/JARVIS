from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from bravo1.brain.obsidian import ObsidianBrain
from bravo1.config import Settings
from bravo1.core.session import SessionManager, SessionState
from bravo1.core.summary import SessionSummaryWriter
from bravo1.models.router import ModelRouter
from bravo1.models.runtime import RuntimeBootstrap
from bravo1.tools.registry import ToolRegistry


class Operator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_dirs()
        self.sessions = SessionManager(settings.session_dir)
        self.brain = ObsidianBrain(settings.brain_dir)
        self.router = ModelRouter(settings)
        self.runtime = RuntimeBootstrap(settings)
        self.tools = ToolRegistry(self.sessions, self.brain, self.runtime)
        self.summaries = SessionSummaryWriter(settings.summary_dir)

    def handle(self, message: str) -> dict[str, Any]:
        state = self.sessions.load()
        self.brain.bootstrap()

        if message.strip().startswith("/"):
            result = self._handle_slash_command(state, message.strip())
            self.sessions.append_message(state, "assistant", result["reply"])
            return result

        self.sessions.append_message(state, "user", message)
        active_context = self.brain.read_active()
        route = self.router.route(self._task_type_for(message))
        primary_action = self._pick_primary_action(message, state)
        reply = self._build_normal_reply(state, active_context, route.lane, route.model_name, primary_action)

        state.last_primary_action = primary_action
        self.brain.sync_from_session(state, primary_action)
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

    def _build_normal_reply(
        self,
        state: SessionState,
        active_context: str,
        route_lane: str,
        model_name: str,
        primary_action: str,
    ) -> str:
        lines = [
            "BRAVO-1 operator scaffold online.",
            f"Session: {state.session_id}",
            f"Route: {route_lane} -> {model_name}",
            f"Primary action: {primary_action}",
        ]
        if state.current_project:
            lines.append(f"Current project: {state.current_project}")
        if state.current_goal:
            lines.append(f"Current goal: {state.current_goal}")
        lines.extend(
            [
                "",
                "Fast commands:",
                "/help, /brief, /session, /active, /tools, /runtime, /summarize",
                "/setgoal <text>, /project <text>, /tool <name>",
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
        elif command == "/runtime":
            reply = json.dumps(self.runtime.status(), ensure_ascii=False, indent=2)
        elif command == "/setgoal":
            if not argument:
                reply = "Usage: /setgoal <goal text>"
            else:
                self.sessions.set_goal(state, argument)
                state.last_primary_action = argument
                self.brain.sync_from_session(state, argument)
                reply = f"Goal set: {argument}"
        elif command == "/project":
            if not argument:
                if state.current_project:
                    reply = f"Current project: {state.current_project}"
                else:
                    reply = "No current project set. Use /project <name or path>."
            else:
                self.sessions.set_project(state, argument)
                self.brain.sync_from_session(state, state.last_primary_action or "stabilize project continuity structure")
                reply = f"Project set: {argument}"
        elif command == "/summarize":
            path = self.summaries.write(state, trigger="slash_command")
            state.last_summary_path = str(path)
            self.sessions.save(state)
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
                "/runtime — inspect local GGUF runtime bootstrap status",
                "/setgoal <text> — set the current goal",
                "/project <text> — set or inspect current project",
                "/summarize — write a session summary markdown file",
            ]
        )

    def _brief_text(self, state: SessionState) -> str:
        active = self.brain.read_active()
        route = self.router.route("brief")
        primary_action = state.last_primary_action or state.current_goal or "define the next core loop"
        lines = [
            "BRAVO-1 brief",
            f"Primary action: {primary_action}",
            f"Project: {state.current_project or 'not set'}",
            f"Goal: {state.current_goal or 'not set'}",
            f"Route: {route.lane} -> {route.model_name}",
            "",
            "Active context:",
            active[:500],
        ]
        return "\n".join(lines)
