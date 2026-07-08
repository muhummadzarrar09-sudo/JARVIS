from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PromptPack:
    prompt_dir: Path

    def read(self, name: str) -> str:
        path = self.prompt_dir / name
        return path.read_text(encoding="utf-8")

    def system_operator(self) -> str:
        return self.read("system_operator.txt")

    def fallback_footer(self) -> str:
        return self.read("fallback_footer.txt")
