from typing import Any


class ToolRegistry:
    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "shell",
                "category": "system",
                "phase": 1,
                "risk": "medium",
                "commands": ["shell: <command>"],
                "notes": "Runs terminal commands locally.",
            },
            {
                "name": "filesystem",
                "category": "system",
                "phase": 1,
                "risk": "medium",
                "commands": [
                    "fs list: <path>",
                    "fs read: <path>",
                    "fs write: <path> ::: <content>",
                    "fs append: <path> ::: <content>",
                    "fs mkdir: <path>",
                ],
                "notes": "Workspace-bounded file operations.",
            },
            {
                "name": "browser",
                "category": "web",
                "phase": 3,
                "risk": "medium",
                "commands": [
                    "browser open: <url>",
                    "browser inspect: <selector>",
                    "browser click: <selector>",
                    "browser forceclick: <selector>",
                    "browser fill: <selector> ::: <text>",
                    "browser press: <selector> ::: <key>",
                    "browser screenshot: <path>",
                ],
                "notes": "Playwright-backed Chromium automation.",
            },
            {
                "name": "app_wrappers",
                "category": "desktop",
                "phase": 4,
                "risk": "medium",
                "commands": [
                    "app wrappers",
                    "app recipes",
                    "app status[: <name>]",
                    "app open: <name> [::: target]",
                    "app ensure: <name> [::: target]",
                    "app focus: <name>",
                    "app focusexact: <name>",
                    "app recipe: <name> [::: payload]",
                    "app note: <text>",
                    "app explore: <path>",
                    "app code: <path>",
                    "app browse: <url>",
                ],
                "notes": "Higher-level wrappers, status awareness, and reusable recipes for Notepad, Explorer, VS Code, browser, and terminal workflows.",
            },
            {
                "name": "process",
                "category": "desktop",
                "phase": 2,
                "risk": "high",
                "commands": [
                    "proc list",
                    "proc list: <name>",
                    "proc windows",
                    "proc start: <command>",
                    "proc kill: <pid-or-image>",
                ],
                "notes": "Laptop-control groundwork for managing apps and processes.",
            },
            {
                "name": "desktop",
                "category": "desktop",
                "phase": 4,
                "risk": "high",
                "commands": [
                    "desktop windows",
                    "desktop active",
                    "desktop screen",
                    "desktop focus: <title>",
                    "desktop focusexact: <title>",
                    "desktop type: <text>",
                    "desktop press: <key>",
                    "desktop hotkey: ctrl+shift+t",
                    "desktop click: x,y [::: right]",
                    "desktop screenshot[: <path>]",
                ],
                "notes": "Desktop-control starter with focus awareness, guard metadata, hotkeys, clicks, and screenshots.",
            },
            {
                "name": "checkpoint",
                "category": "continuity",
                "phase": 2,
                "risk": "low",
                "commands": [
                    "checkpoint create",
                    "checkpoint create: <note>",
                    "checkpoint get",
                ],
                "notes": "Stores session handoff snapshots locally.",
            },
            {
                "name": "tasks",
                "category": "productivity",
                "phase": 1,
                "risk": "low",
                "commands": [
                    "task create: <title>",
                    "task list",
                    "task done: <id>",
                    "task reopen: <id>",
                ],
                "notes": "Phase-1 task/session management layer.",
            },
        ]


tool_registry = ToolRegistry()
