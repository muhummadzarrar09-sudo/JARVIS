from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ToolSpec:
    name: str
    description: str
    risk: str


class ToolRegistry:
    def __init__(self) -> None:
        self._tools = [
            ToolSpec(name="session.inspect", description="Inspect current session state", risk="low"),
            ToolSpec(name="brain.read_active", description="Read active brain context", risk="low"),
        ]

    def list_tools(self) -> list[ToolSpec]:
        return list(self._tools)

    def execute(self, tool_name: str, **_: Any) -> dict[str, Any]:
        return {
            "ok": False,
            "tool": tool_name,
            "error": "Tool execution is not implemented yet in the Week-1 scaffold.",
        }
