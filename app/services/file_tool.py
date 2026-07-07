from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.trusted_root_service import trusted_root_service


class FileTool:
    def _resolve(self, raw_path: str) -> dict[str, Any]:
        info = trusted_root_service.resolve(raw_path)
        if not info.get("ok"):
            raise ValueError(info.get("error") or f"Invalid path: {raw_path}")
        return info

    def roots_summary(self) -> dict[str, Any]:
        return trusted_root_service.summary()

    def policy(self, raw_path: str, action: str = "read") -> dict[str, Any]:
        info = trusted_root_service.resolve(raw_path)
        if not info.get("ok"):
            return info
        return {
            "ok": True,
            "path": info.get("path"),
            "scope": info.get("scope"),
            "root_name": info.get("root_name"),
            "root_path": info.get("root_path"),
            "relative_to_root": info.get("relative_to_root"),
            "inside_workspace": info.get("inside_workspace"),
            "requires_confirmation": trusted_root_service.require_confirmation(action, info.get("scope")),
            "plain_english": "This is the path policy decision for the requested local file operation.",
        }

    def _item_display_path(self, item: Path, info: dict[str, Any]) -> str:
        root_path = Path(info.get("root_path") or info.get("path"))
        try:
            relative = item.relative_to(root_path)
            rel_text = "." if str(relative) == "." else str(relative)
        except Exception:
            rel_text = item.name
        scope = info.get("scope") or "trusted"
        if scope == "workspace":
            return rel_text
        return f"{info.get('root_name')}:{rel_text}"

    def list_dir(self, raw_path: str = ".") -> dict[str, Any]:
        if not settings.allow_file_tool:
            return {"ok": False, "error": "File tool is disabled in config."}
        try:
            info = self._resolve(raw_path)
            path = info.get("resolved")
            assert isinstance(path, Path)
            if not path.exists():
                return {"ok": False, "error": f"Path does not exist: {raw_path}"}
            if not path.is_dir():
                return {"ok": False, "error": f"Not a directory: {raw_path}"}
            items = []
            for item in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                items.append(
                    {
                        "name": item.name,
                        "path": str(item),
                        "display_path": self._item_display_path(item, info),
                        "is_dir": item.is_dir(),
                    }
                )
            return {
                "ok": True,
                "path": str(path),
                "scope": info.get("scope"),
                "root_name": info.get("root_name"),
                "relative_to_root": info.get("relative_to_root"),
                "items": items,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def read_text(self, raw_path: str) -> dict[str, Any]:
        if not settings.allow_file_tool:
            return {"ok": False, "error": "File tool is disabled in config."}
        try:
            info = self._resolve(raw_path)
            path = info.get("resolved")
            assert isinstance(path, Path)
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
            return {
                "ok": True,
                "path": str(path),
                "scope": info.get("scope"),
                "root_name": info.get("root_name"),
                "relative_to_root": info.get("relative_to_root"),
                "content": content,
                "size": size,
            }
        except UnicodeDecodeError:
            return {"ok": False, "error": "File is not valid UTF-8 text."}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def write_text(self, raw_path: str, content: str, append: bool = False) -> dict[str, Any]:
        if not settings.allow_file_tool:
            return {"ok": False, "error": "File tool is disabled in config."}
        try:
            info = self._resolve(raw_path)
            path = info.get("resolved")
            assert isinstance(path, Path)
            path.parent.mkdir(parents=True, exist_ok=True)
            mode = "a" if append else "w"
            with path.open(mode, encoding="utf-8") as f:
                f.write(content)
            return {
                "ok": True,
                "path": str(path),
                "scope": info.get("scope"),
                "root_name": info.get("root_name"),
                "relative_to_root": info.get("relative_to_root"),
                "bytes_written": len(content.encode("utf-8")),
                "append": append,
                "requires_confirmation": trusted_root_service.require_confirmation("append" if append else "write", info.get("scope")),
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def make_dir(self, raw_path: str) -> dict[str, Any]:
        if not settings.allow_file_tool:
            return {"ok": False, "error": "File tool is disabled in config."}
        try:
            info = self._resolve(raw_path)
            path = info.get("resolved")
            assert isinstance(path, Path)
            path.mkdir(parents=True, exist_ok=True)
            return {
                "ok": True,
                "path": str(path),
                "scope": info.get("scope"),
                "root_name": info.get("root_name"),
                "relative_to_root": info.get("relative_to_root"),
                "requires_confirmation": trusted_root_service.require_confirmation("mkdir", info.get("scope")),
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}


file_tool = FileTool()
