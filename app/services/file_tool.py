from pathlib import Path
from typing import Any

from app.core.config import settings


class FileTool:
    def _resolve(self, raw_path: str) -> Path:
        workspace = settings.workspace_root.resolve()
        candidate = (workspace / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path).resolve()
        try:
            candidate.relative_to(workspace)
        except ValueError as e:
            raise ValueError(f"Path escapes workspace root: {raw_path}") from e
        return candidate

    def list_dir(self, raw_path: str = ".") -> dict[str, Any]:
        if not settings.allow_file_tool:
            return {"ok": False, "error": "File tool is disabled in config."}
        try:
            path = self._resolve(raw_path)
            if not path.exists():
                return {"ok": False, "error": f"Path does not exist: {raw_path}"}
            if not path.is_dir():
                return {"ok": False, "error": f"Not a directory: {raw_path}"}
            items = []
            for item in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                items.append(
                    {
                        "name": item.name,
                        "path": str(item.relative_to(settings.workspace_root.resolve())),
                        "is_dir": item.is_dir(),
                    }
                )
            return {"ok": True, "path": str(path), "items": items}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def read_text(self, raw_path: str) -> dict[str, Any]:
        if not settings.allow_file_tool:
            return {"ok": False, "error": "File tool is disabled in config."}
        try:
            path = self._resolve(raw_path)
            if not path.exists():
                return {"ok": False, "error": f"File does not exist: {raw_path}"}
            if not path.is_file():
                return {"ok": False, "error": f"Not a file: {raw_path}"}
            size = path.stat().st_size
            if size > settings.max_file_read_bytes:
                return {
                    "ok": False,
                    "error": f"File too large to read in one shot ({size} bytes > {settings.max_file_read_bytes})",
                }
            content = path.read_text(encoding="utf-8")
            return {"ok": True, "path": str(path), "content": content, "size": size}
        except UnicodeDecodeError:
            return {"ok": False, "error": "File is not valid UTF-8 text."}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def write_text(self, raw_path: str, content: str, append: bool = False) -> dict[str, Any]:
        if not settings.allow_file_tool:
            return {"ok": False, "error": "File tool is disabled in config."}
        try:
            path = self._resolve(raw_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            mode = "a" if append else "w"
            with path.open(mode, encoding="utf-8") as f:
                f.write(content)
            return {"ok": True, "path": str(path), "bytes_written": len(content.encode('utf-8')), "append": append}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def make_dir(self, raw_path: str) -> dict[str, Any]:
        if not settings.allow_file_tool:
            return {"ok": False, "error": "File tool is disabled in config."}
        try:
            path = self._resolve(raw_path)
            path.mkdir(parents=True, exist_ok=True)
            return {"ok": True, "path": str(path)}
        except Exception as e:
            return {"ok": False, "error": str(e)}


file_tool = FileTool()
