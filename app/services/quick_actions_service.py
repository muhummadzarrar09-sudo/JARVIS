from difflib import SequenceMatcher
from typing import Any

from app.services.app_wrapper_service import app_wrapper_service


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
                        {"say": "resume project", "does": "Reopen the remembered project flow using wrappers."},
                        {"say": "open readme", "does": "Open the README in VS Code if one exists."},
                    ],
                },
                {
                    "name": "Browser",
                    "items": [
                        {"say": "open browser", "does": "Open the managed browser session."},
                        {"say": "open browser to https://example.com", "does": "Open a specific URL."},
                        {"say": "search for local ai agents", "does": "Search the web."},
                        {"say": "research local ai agents", "does": "Search and capture a text snapshot."},
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
        suggestions = [
            "show my project",
            "open readme",
            "open code here",
            "open terminal here",
            "search for jarvis local assistant",
        ]
        if project.get("ok"):
            summary = project.get("summary", {})
            suggestions = ["show my project", "resume project", "open code here", "open terminal here"]
            if summary.get("readme"):
                suggestions.insert(1, "open readme")
        return {"ok": True, "items": suggestions[:5]}

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


quick_actions_service = QuickActionsService()
