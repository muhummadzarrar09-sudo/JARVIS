from difflib import SequenceMatcher
from typing import Any

from app.services.app_wrapper_service import app_wrapper_service
from app.services.executive_brief_service import executive_brief_service
from app.services.memory import memory_service
from app.services.project_intelligence_service import project_intelligence_service
from app.services.task_service import task_service


class QuickActionsService:
    def guide(self) -> dict[str, Any]:
        return {
            "ok": True,
            "title": "JARVIS Starter Guide",
            "categories": [
                {
                    "name": "Project",
                    "items": [
                        {"say": "show my project", "does": "Inspect the current workspace and show project context."},
                        {"say": "review this project", "does": "Inspect the project and show or open the README."},
                        {"say": "resume project", "does": "Reopen the remembered project flow using wrappers."},
                        {"say": "resume work", "does": "Show the stronger project resume packet for getting back into the live operating thread."},
                        {"say": "open readme", "does": "Open the README in VS Code if one exists."},
                        {"say": "show my project files", "does": "Open or preview the project folder contents."},
                        {"say": "show my setup blockers", "does": "Show the main issues stopping tools from working right now."},
                        {"say": "project idea ...", "does": "Capture an idea against the current project context."},
                        {"say": "project blocker ...", "does": "Capture a blocker against the current project context."},
                    ],
                },
                {
                    "name": "Do this for me",
                    "items": [
                        {"say": "set me up to work on this project", "does": "Open project tools like code, files, and terminal."},
                        {"say": "start coding", "does": "Open code and terminal flows for the current project."},
                        {"say": "continue coding", "does": "Resume the last coding workspace and terminal context."},
                        {"say": "help me continue where I left off", "does": "Resume the remembered project flow."},
                        {"say": "what should i do now", "does": "Get the executive brief for the most grounded next move right now."},
                        {"say": "show me what to do next", "does": "Suggest the next beginner-friendly actions."},
                        {"say": "show me today's focus", "does": "Show the most important thing to work on right now."},
                        {"say": "show me today", "does": "Show a simple day brief with tasks, project, and browser context."},
                        {"say": "show my progress", "does": "Show overall progress and recent activity."},
                        {"say": "start my workday", "does": "Get the workspace ready to work."},
                        {"say": "review this project", "does": "Inspect the project and show a quick README-based overview."},
                        {"say": "start coding", "does": "Open or prepare the project coding setup."},
                    ],
                },
                {
                    "name": "Tasks",
                    "items": [
                        {"say": "show my tasks", "does": "Show open tasks."},
                        {"say": "what task should i do next", "does": "Pick the next task to focus on."},
                        {"say": "what am i doing now", "does": "Show the task currently in progress."},
                        {"say": "work on next task", "does": "Mark the next task as in progress."},
                        {"say": "complete current task", "does": "Mark the current task as done."},
                        {"say": "wrap up current task", "does": "Finish the task you are currently working on."},
                    ],
                },
                {
                    "name": "Sessions",
                    "items": [
                        {"say": "show my sessions", "does": "Show recent sessions."},
                        {"say": "show me recent work", "does": "Show recent sessions and where you left off."},
                        {"say": "resume last session", "does": "Switch back to your recent session in the terminal."},
                    ],
                },
                {
                    "name": "Browser",
                    "items": [
                        {"say": "open browser", "does": "Open your real external browser by default."},
                        {"say": "open browser to https://example.com", "does": "Open a specific URL."},
                        {"say": "search for local ai agents", "does": "Search the web."},
                        {"say": "research local ai agents", "does": "Open a controlled browser review and capture a text snapshot."},
                        {"say": "search this site for pricing", "does": "Search only within the current site you were viewing."},
                        {"say": "show me the current page", "does": "Resume the current or remembered page in controlled review mode."},
                        {"say": "show browser options", "does": "Show which installed browsers JARVIS can try to use."},
                    ],
                },
                {
                    "name": "Apps",
                    "items": [
                        {"say": "open code here", "does": "Open the current folder in VS Code."},
                        {"say": "open files here", "does": "Open the current folder in File Explorer."},
                        {"say": "open terminal here", "does": "Open a terminal in the current folder."},
                        {"say": "write note remember this idea", "does": "Open Notepad and type a quick note."},
                    ],
                },
                {
                    "name": "Models",
                    "items": [
                        {"say": "show model status", "does": "Show which GGUF models JARVIS can see and whether local inference is ready."},
                        {"say": "use local models", "does": "Configure JARVIS to prefer your downloaded GGUF models."},
                        {"say": "use mock mode", "does": "Switch back to mock replies for non-tool chat."},
                    ],
                },
                {
                    "name": "Desktop",
                    "items": [
                        {"say": "take screenshot", "does": "Capture a desktop screenshot."},
                        {"say": "show wrapper status", "does": "Show app wrapper status table."},
                        {"say": "check my setup", "does": "Run wrapper readiness diagnostics."},
                    ],
                },
            ],
        }

    def next_steps(self) -> dict[str, Any]:
        return executive_brief_service.next_steps()

    def focus(self) -> dict[str, Any]:
        current = task_service.current_task()
        next_task = task_service.next_task()
        project = app_wrapper_service.current_project_context(None)

        if current.get("ok"):
            headline = f"Current focus: {current.get('title')}"
            status = current.get("status")
            plain = "You already have an active task in progress."
            next_action = "complete current task"
        elif next_task.get("ok"):
            headline = f"Next focus: {next_task.get('title')}"
            status = next_task.get("status")
            plain = "JARVIS found the next task you can start right now."
            next_action = "work on next task"
        else:
            headline = "No active task focus found"
            status = None
            plain = "There is no current task focus yet."
            next_action = "start my workday"

        return {
            "ok": True,
            "headline": headline,
            "status": status,
            "plain_english": plain,
            "next_action": next_action,
            "current_task": current if current.get("ok") else None,
            "next_task": next_task if next_task.get("ok") else None,
            "project_path": project.get("path") if project.get("ok") else None,
            "recommended": self.next_steps().get("items", []),
        }

    def executive_brief(self) -> dict[str, Any]:
        return executive_brief_service.build()

    def project_intelligence(self) -> dict[str, Any]:
        return project_intelligence_service.current(None)

    def resume_work_packet(self) -> dict[str, Any]:
        return project_intelligence_service.resume_work_packet(None)

    def project_capture(self, kind: str, text: str) -> dict[str, Any]:
        return project_intelligence_service.capture(kind, text)

    def today_brief(self) -> dict[str, Any]:
        focus = self.focus()
        project = app_wrapper_service.current_project_context(None)
        browser = app_wrapper_service.current_browser_context()
        sessions = memory_service.list_sessions(limit=3)
        tasks = task_service.task_summary()
        brief = self.executive_brief()
        next_steps = self.next_steps().get("items", [])
        return {
            "ok": True,
            "headline": brief.get("headline") or focus.get("headline"),
            "plain_english": "This is your simple day snapshot: what matters now, where your project stands, and the fastest next move.",
            "next_action": brief.get("primary_action") or (next_steps[0] if next_steps else None),
            "brief": brief,
            "focus": focus,
            "project": project if project.get("ok") else None,
            "browser": browser,
            "recent_sessions": sessions,
            "task_summary": tasks,
            "next_steps": next_steps,
        }

    def progress(self) -> dict[str, Any]:
        summary = task_service.task_summary()
        recent_sessions = memory_service.list_sessions(limit=5)
        browser = app_wrapper_service.current_browser_context()
        project = app_wrapper_service.current_project_context(None)
        next_steps = self.next_steps().get("items", [])
        return {
            "ok": True,
            "plain_english": "This is your overall progress snapshot across tasks, sessions, project state, and browser state.",
            "next_action": next_steps[0] if next_steps else None,
            "task_summary": summary,
            "recent_sessions": recent_sessions,
            "browser": browser,
            "project": project if project.get("ok") else None,
            "next_steps": next_steps,
        }

    def setup_summary(self) -> dict[str, Any]:
        doctor = app_wrapper_service.wrapper_doctor()
        project = app_wrapper_service.current_project_context(None)
        browser = app_wrapper_service.current_browser_context()
        next_steps = self.next_steps().get("items", [])

        blockers = []
        for item in doctor.get("items", []):
            if not item.get("ready"):
                blockers.append({"name": item.get("name"), "notes": item.get("notes")})

        plain = "Your setup looks usable." if not blockers else "JARVIS found a few setup blockers you may want to fix."
        return {
            "ok": True,
            "plain_english": plain,
            "next_action": next_steps[0] if next_steps else None,
            "doctor": doctor,
            "project": project if project.get("ok") else None,
            "browser": browser,
            "blockers": blockers,
            "next_steps": next_steps,
        }

    def search(self, query: str) -> dict[str, Any]:
        q = query.strip().lower()
        if not q:
            return {"ok": False, "error": "Search query is required."}

        scored = []
        for category in self.guide().get("categories", []):
            for item in category.get("items", []):
                say = item.get("say", "")
                does = item.get("does", "")
                hay = f"{say} {does}".lower()
                if q in hay:
                    score = 1.0
                else:
                    score = SequenceMatcher(None, q, hay).ratio()
                if score >= 0.18:
                    scored.append(
                        {
                            "score": score,
                            "category": category.get("name"),
                            "say": say,
                            "does": does,
                        }
                    )
        scored.sort(key=lambda item: item.get("score", 0), reverse=True)
        items = [{k: v for k, v in item.items() if k != "score"} for item in scored[:8]]
        return {"ok": True, "count": len(items), "items": items}

    def recent_work_summary(self) -> dict[str, Any]:
        current = task_service.current_task()
        next_task = task_service.next_task()
        sessions = memory_service.list_sessions(limit=3)
        next_steps = self.next_steps().get("items", [])
        return {
            "ok": True,
            "plain_english": "Here is a simple summary of what you were recently doing and what to do next.",
            "next_action": next_steps[0] if next_steps else None,
            "current_task": current if current.get("ok") else None,
            "next_task": next_task if next_task.get("ok") else None,
            "recent_sessions": sessions,
            "suggested_next": next_steps,
        }


quick_actions_service = QuickActionsService()
