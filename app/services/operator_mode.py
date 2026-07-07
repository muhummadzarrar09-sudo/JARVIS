from typing import Any


class OperatorModeService:
    def _looks_global_path(self, text: str) -> bool:
        lowered = (text or "").strip().lower()
        return (
            lowered.startswith("/")
            or lowered.startswith("\\")
            or (len(lowered) > 2 and lowered[1:3] == ':\\')
            or (len(lowered) > 2 and lowered[1:3] == ':/')
        )

    def __init__(self) -> None:
        self.high_risk_prefixes = [
            "shell:",
            "proc kill:",
            "proc start:",
            "desktop click:",
            "desktop hotkey:",
            "desktop type:",
            "desktop write:",
            "desktop press:",
            "app note:",
        ]
        self.medium_risk_prefixes = [
            "fs write:",
            "fs append:",
            "fs mkdir:",
            "app ensure:",
            "app open:",
            "app recipe:",
            "browser forceclick:",
        ]
        self.high_risk_natural_starts = [
            "write note ",
            "remember this ",
        ]
        self.medium_risk_natural_prefixes = [
            "open browser",
            "open chrome",
            "open edge",
            "open brave",
            "open firefox",
            "open code",
            "open files",
            "open terminal",
            "start coding",
            "continue coding",
            "resume project",
            "resume browser",
            "resume code",
            "start my workday",
            "get me ready to work",
            "set me up to work on this project",
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
                    "reason": "This command can directly control the system, launch arbitrary processes, or write into an active app.",
                    "requires_confirmation": True,
                }

        for prefix in self.high_risk_natural_starts:
            if lowered.startswith(prefix):
                return {
                    "risk": "high",
                    "label": prefix.strip(),
                    "reason": "This command writes into another desktop application and should be explicitly confirmed.",
                    "requires_confirmation": True,
                }

        for prefix in self.medium_risk_prefixes:
            if lowered.startswith(prefix):
                tail = raw[len(prefix):].strip() if raw.lower().startswith(prefix) else ""
                global_write = prefix in {"fs write:", "fs append:"} and self._looks_global_path(tail)
                global_mkdir = prefix == "fs mkdir:" and self._looks_global_path(tail)
                if global_write or global_mkdir:
                    return {
                        "risk": "high",
                        "label": prefix.rstrip(": "),
                        "reason": "This command changes local state outside the main workspace and should be explicitly confirmed.",
                        "requires_confirmation": True,
                    }
                return {
                    "risk": "medium",
                    "label": prefix.rstrip(": "),
                    "reason": "This command changes local state or launches tools/apps.",
                    "requires_confirmation": False,
                }

        for prefix in self.medium_risk_natural_prefixes:
            if lowered.startswith(prefix):
                return {
                    "risk": "medium",
                    "label": prefix,
                    "reason": "This command launches or resumes local tools/apps.",
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
