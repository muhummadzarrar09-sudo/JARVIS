from pathlib import Path
from typing import Any

from app.core.config import settings


class TrustedRootService:
    def _workspace_root(self) -> Path:
        return Path(settings.workspace_root).resolve()

    def _parse_configured_roots(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in settings.trusted_global_roots.split(","):
            cleaned = raw.strip().strip('"').strip("'")
            if not cleaned:
                continue
            try:
                resolved = Path(cleaned).resolve()
            except Exception:
                continue
            key = str(resolved).lower()
            if key in seen:
                continue
            seen.add(key)
            items.append(
                {
                    "name": f"trusted_{len(items) + 1}",
                    "path": str(resolved),
                    "resolved": resolved,
                    "scope": "trusted_global",
                    "exists": resolved.exists(),
                }
            )
        return items

    def roots(self) -> list[dict[str, Any]]:
        workspace = self._workspace_root()
        roots: list[dict[str, Any]] = [
            {
                "name": "workspace",
                "path": str(workspace),
                "resolved": workspace,
                "scope": "workspace",
                "exists": workspace.exists(),
            }
        ]
        roots.extend(self._parse_configured_roots())
        return roots

    def summary(self) -> dict[str, Any]:
        items = []
        for root in self.roots():
            items.append(
                {
                    "name": root.get("name"),
                    "path": root.get("path"),
                    "scope": root.get("scope"),
                    "exists": root.get("exists"),
                }
            )
        return {
            "ok": True,
            "count": len(items),
            "items": items,
            "workspace_root": str(self._workspace_root()),
            "plain_english": "These are the currently trusted local roots JARVIS is allowed to work inside.",
        }

    def resolve(self, raw_path: str | None = None) -> dict[str, Any]:
        workspace = self._workspace_root()
        raw = (raw_path or ".").strip()
        candidate = (workspace / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()

        for root in self.roots():
            resolved_root = root.get("resolved")
            if not isinstance(resolved_root, Path):
                continue
            try:
                relative = candidate.relative_to(resolved_root)
                return {
                    "ok": True,
                    "raw_path": raw,
                    "path": str(candidate),
                    "resolved": candidate,
                    "scope": root.get("scope"),
                    "root_name": root.get("name"),
                    "root_path": str(resolved_root),
                    "relative_to_root": "." if str(relative) == "." else str(relative),
                    "inside_workspace": root.get("scope") == "workspace",
                    "trusted": True,
                }
            except ValueError:
                continue

        return {
            "ok": False,
            "raw_path": raw,
            "path": str(candidate),
            "resolved": candidate,
            "trusted": False,
            "error": f"Path is outside the workspace and all trusted roots: {raw}",
        }

    def require_confirmation(self, action: str, scope: str | None) -> bool:
        destructive = action in {"write", "append", "mkdir"}
        if not destructive:
            return False
        if scope == "workspace":
            return False
        return settings.global_write_requires_confirmation


trusted_root_service = TrustedRootService()
