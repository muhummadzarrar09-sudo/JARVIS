from typing import Any


class OperatorModeService:
    def __init__(self) -> None:
        self.high_risk_prefixes = [
            "shell:",
            "proc kill:",
            "desktop click:",
            "desktop hotkey:",
            "desktop type:",
            "desktop write:",
            "app note:",
        ]
        self.medium_risk_prefixes = [
            "fs write:",
            "fs append:",
            "proc start:",
            "app ensure:",
            "app open:",
            "app recipe:",
            "browser forceclick:",
            "desktop press:",
        ]

    def classify_command(self, text: str) -> dict[str, Any]:
        raw = text.strip()
        lowered = raw.lower()
        if not raw:
            return {
                "risk": "low",
                "label": "empty",
                "reason": "No command provided.",
                "requires_confirmation": False,
            }

        for prefix in self.high_risk_prefixes:
            if lowered.startswith(prefix):
                return {
                    "risk": "high",
                    "label": prefix.rstrip(": "),
                    "reason": "This command can directly control the system or write into an active app.",
                    "requires_confirmation": True,
                }

        for prefix in self.medium_risk_prefixes:
            if lowered.startswith(prefix):
                return {
                    "risk": "medium",
                    "label": prefix.rstrip(": "),
                    "reason": "This command changes local state or launches tools/apps.",
                    "requires_confirmation": False,
                }

        return {
            "risk": "low",
            "label": "general",
            "reason": "Read-oriented or conversational command.",
            "requires_confirmation": False,
        }

    def palette(self) -> list[dict[str, Any]]:
        return [
            {
                "category": "Project",
                "commands": [
                    "app project",
                    "app recipe: project.inspect ::: .",
                    "app recipe: project.resume",
                    "app recipe: vscode.readme ::: .",
                ],
            },
            {
                "category": "Browser",
                "commands": [
                    "browser open: https://example.com",
                    "app recipe: browser.search ::: jarvis local assistant",
                    "app recipe: browser.research ::: local ai agents",
                    "app recipe: browser.resume",
                ],
            },
            {
                "category": "Desktop",
                "commands": [
                    "desktop windows",
                    "desktop active",
                    "desktop screenshot",
                    "app doctor",
                ],
            },
            {
                "category": "Terminal",
                "commands": [
                    "app ensure: terminal ::: .",
                    "app recipe: terminal.command ::: . || python --version",
                    "task list",
                    "session overview",
                ],
            },
        ]


operator_mode_service = OperatorModeService()
