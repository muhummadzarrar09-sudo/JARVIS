from typing import Any


class ProgressService:
    def __init__(self) -> None:
        self.phase4_sections = [
            {
                "name": "Desktop control primitives",
                "items": [
                    {"id": "desktop_windows", "label": "Desktop window listing", "done": True},
                    {"id": "desktop_active", "label": "Active-window inspection", "done": True},
                    {"id": "desktop_screen", "label": "Screen-state inspection", "done": True},
                    {"id": "desktop_focus", "label": "Focus by title", "done": True},
                    {"id": "desktop_type", "label": "Keyboard typing starter", "done": True},
                    {"id": "desktop_hotkey_click", "label": "Hotkey + coordinate click starter", "done": True},
                    {"id": "desktop_screenshot", "label": "Desktop screenshots", "done": True},
                    {"id": "desktop_exact_focus", "label": "Exact activation hardening beyond title matching", "done": True},
                    {"id": "desktop_safety", "label": "Richer desktop safety / undo policies", "done": True},
                ],
            },
            {
                "name": "Wrappers and recipes",
                "items": [
                    {"id": "wrappers_base", "label": "App wrapper starter", "done": True},
                    {"id": "recipes_base", "label": "Workflow recipe starter", "done": True},
                    {"id": "wrapper_memory", "label": "Wrapper remembered state", "done": True},
                    {"id": "workspace_flows", "label": "Workspace-aware wrapper flows", "done": True},
                    {"id": "browser_multi_candidate", "label": "Browser candidate detection + preference support", "done": True},
                    {"id": "browser_live_branching", "label": "Deeper live branching from actual browser/window state", "done": True},
                    {"id": "workflow_breadth", "label": "Broader app-specific workflow coverage", "done": True},
                ],
            },
            {
                "name": "Command-center UX",
                "items": [
                    {"id": "command_panels", "label": "Command-center panels in terminal", "done": True},
                    {"id": "starter_shortcuts", "label": "Beginner-friendly natural commands + /do shortcut", "done": True},
                    {"id": "timeline_replay", "label": "Timeline / replay / operator surfaces", "done": True},
                    {"id": "project_context_panel", "label": "Project-context panels", "done": True},
                    {"id": "browser_panel", "label": "Browser panel and browser option visibility", "done": True},
                    {"id": "desktop_shell_prep", "label": "Desktop app shell preparation layer", "done": True},
                ],
            },
        ]

    def phase4_status(self) -> dict[str, Any]:
        completed = 0
        total = 0
        sections = []

        for section in self.phase4_sections:
            items = section["items"]
            done_count = sum(1 for item in items if item["done"])
            section_total = len(items)
            completed += done_count
            total += section_total
            sections.append(
                {
                    "name": section["name"],
                    "completed": done_count,
                    "total": section_total,
                    "percent": round((done_count / section_total) * 100, 1) if section_total else 0.0,
                    "items": items,
                }
            )

        percent = round((completed / total) * 100, 1) if total else 0.0
        remaining = [
            item["label"]
            for section in self.phase4_sections
            for item in section["items"]
            if not item["done"]
        ]
        return {
            "ok": True,
            "phase": 4,
            "name": "Desktop Control + Wrappers",
            "completed": completed,
            "total": total,
            "percent": percent,
            "sections": sections,
            "remaining": remaining,
            "plain_english": f"Phase 4 is about {percent}% complete based on the current implementation checklist.",
            "next_action": remaining[0] if remaining else None,
        }


progress_service = ProgressService()
