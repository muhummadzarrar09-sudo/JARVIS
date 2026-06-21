from difflib import SequenceMatcher
from typing import Any

from app.services.app_wrapper_service import app_wrapper_service
from app.services.memory import memory_service
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
                        {"say": "open readme", "does": "Open the README in VS Code if one exists."},
                        {"say": "show my project files", "does": "Open or preview the project folder contents."},
                    ],
                },
                {
                    "name": "Do this for me",
                    "items": [
                        {"say": "set me up to work on this project", "does": "Open project tools like code, files, and terminal."},
                        {"say": "start coding", "does": "Open code and terminal flows for the current project."},
                        {"say": "help me continue where I left off", "does": "Resume the remembered project flow."},
                        {"say": "show me what to do next", "does": "Suggest the next beginner-friendly actions."},
                        {"say": "show me today's focus", "does": "Show the most important thing to work on right now."},
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
                        {"say": "open browser", "does": "Open the managed browser session."},
                        {"say": "open browser to https://example.com", "does": "Open a specific URL."},
                        {"say": "search for local ai agents", "does": "Search the web."},
                        {"say": "research local ai agents", "does": "Search and capture a text snapshot."},
                        {"say": "show me the current page", "does": "Resume the current or remembered browser page."},
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
        project = app_wrapper_service.current_project_context(None)
        task = task_service.next_task()
        suggestions = [
            "show my project",
            "open readme",
            "open code here",
            "open terminal here",
            "search for jarvis local assistant",
        ]
        if project.get("ok"):
            summary = project.get("summary", {})
            suggestions = ["show my project", "review this project", "resume project", "open code here", "open terminal here"]
            if summary.get("readme"):
                suggestions.insert(1, "open readme")
        if task.get("ok") and task.get("title"):
            if task.get("status") == "in_progress":
                suggestions.insert(0, "complete current task")
                suggestions.insert(1, "what am i doing now")
            else:
                suggestions.insert(0, "work on next task")
        else:
            suggestions.insert(0, "start my workday")
        deduped = []
        for item in suggestions:
            if item not in deduped:
                deduped.append(item)
        return {"ok": True, "items": deduped[:5]}

    def focus(self) -> dict[str, Any]:
        current = task_service.current_task()
        next_task = task_service.next_task()
        project = app_wrapper_service.current_project_context(None)

        if current.get("ok"):
            headline = f"Current focus: {current.get('title')}"
            status = current.get("status")
        elif next_task.get("ok"):
            headline = f"Next focus: {next_task.get('title')}"
            status = next_task.get("status")
        else:
            headline = "No active task focus found"
            status = None

        return {
            "ok": True,
            "headline": headline,
            "status": status,
            "current_task": current if current.get("ok") else None,
            "next_task": next_task if next_task.get("ok") else None,
            "project_path": project.get("path") if project.get("ok") else None,
            "recommended": self.next_steps().get("items", []),
        }

    def today_brief(self) -> dict[str, Any]:
        focus = self.focus()
        project = app_wrapper_service.current_project_context(None)
        browser = app_wrapper_service.current_browser_context()
        sessions = memory_service.list_sessions(limit=3)
        tasks = task_service.task_summary()
        return {
            "ok": True,
            "headline": focus.get("headline"),
            "focus": focus,
            "project": project if project.get("ok") else None,
            "browser": browser,
            "recent_sessions": sessions,
            "task_summary": tasks,
            "next_steps": self.next_steps().get("items", []),
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
            "current_task": current if current.get("ok") else None,
            "next_task": next_task if next_task.get("ok") else None,
            "recent_sessions": sessions,
            "suggested_next": next_steps,
        }


quick_actions_service = QuickActionsService()
