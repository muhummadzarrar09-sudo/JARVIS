import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.core.config import settings
from app.services.trusted_root_service import trusted_root_service


class WrapperStateService:
    def __init__(self) -> None:
        self.path: Path = settings.wrapper_state_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hygiene_report: dict[str, Any] = {"ok": True, "changed": False, "issues": [], "count": 0}
        self._known_browser_names = {"chrome", "msedge", "brave", "firefox", "playwright_chromium"}

    def _workspace_root(self) -> Path:
        return Path(settings.workspace_root).resolve()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"wrappers": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {"wrappers": {}}
            data.setdefault("wrappers", {})
            return data
        except Exception:
            return {"wrappers": {}}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _extract_markdown_link_target(self, value: str) -> str:
        raw = (value or "").strip()
        match = re.fullmatch(r"\[(.*?)\]\((https?://[^\s)]+)\)", raw, flags=re.IGNORECASE)
        if match:
            return match.group(2).strip()
        return raw

    def _sanitize_url(self, value: Any) -> tuple[str | None, list[str]]:
        issues: list[str] = []
        if not isinstance(value, str):
            return None, issues
        raw = self._extract_markdown_link_target(value).replace("\n", "").replace("\r", "").strip()
        if not raw:
            return None, issues
        parsed = urlparse(raw)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            if raw != value:
                issues.append("normalized_url")
            return raw, issues
        issues.append("dropped_invalid_url")
        return None, issues

    def _sanitize_path(self, value: Any) -> tuple[str | None, list[str]]:
        issues: list[str] = []
        if not isinstance(value, str):
            return None, issues
        raw = self._extract_markdown_link_target(value).replace("\r", "").replace("\n", "").strip()
        if not raw:
            return None, issues

        suspicious_linux = raw.startswith("/home/") or raw.startswith("/mnt/") or raw.startswith("/Users/")
        if suspicious_linux:
            issues.append("replaced_foreign_absolute_path")
            return ".", issues

        policy = trusted_root_service.resolve(raw)
        if not policy.get("ok"):
            issues.append("replaced_untrusted_path")
            return ".", issues

        normalized = policy.get("path") if not policy.get("inside_workspace") else policy.get("relative_to_root")
        normalized = "." if normalized in {None, ""} else str(normalized)
        if normalized != raw:
            issues.append("normalized_trusted_path")
        return normalized, issues

    def _sanitize_browser_name(self, value: Any) -> tuple[str | None, list[str]]:
        issues: list[str] = []
        if not isinstance(value, str):
            return None, issues
        raw = value.strip().lower()
        aliases = {"edge": "msedge", "playwright": "playwright_chromium"}
        normalized = aliases.get(raw, raw)
        if not normalized:
            return None, issues
        if normalized not in self._known_browser_names:
            issues.append("dropped_unknown_browser_name")
            return None, issues
        if normalized != value:
            issues.append("normalized_browser_name")
        return normalized, issues

    def _sanitize_wrapper_state(self, wrapper_name: str, state: dict[str, Any]) -> tuple[dict[str, Any], list[str], bool]:
        sanitized = dict(state or {})
        issues: list[str] = []
        changed = False

        def set_field(key: str, new_value: Any) -> None:
            nonlocal changed
            old_value = sanitized.get(key)
            if new_value is None:
                if key in sanitized and sanitized.get(key) not in {None, ""}:
                    sanitized.pop(key, None)
                    changed = True
                return
            if old_value != new_value:
                sanitized[key] = new_value
                changed = True

        path_keys = {"last_path"}
        project_like_target_keys = {"explorer", "vscode", "terminal"}
        browser_like_target_keys = {"browser"}

        for key in list(sanitized.keys()):
            value = sanitized.get(key)
            if key in path_keys:
                new_value, key_issues = self._sanitize_path(value)
                issues.extend([f"{key}:{item}" for item in key_issues])
                set_field(key, new_value)
            elif key == "last_target":
                if wrapper_name in browser_like_target_keys:
                    new_value, key_issues = self._sanitize_url(value)
                elif wrapper_name in project_like_target_keys:
                    new_value, key_issues = self._sanitize_path(value)
                else:
                    new_value, key_issues = (value if isinstance(value, str) else None), []
                issues.extend([f"{key}:{item}" for item in key_issues])
                set_field(key, new_value)
            elif key == "last_url":
                new_value, key_issues = self._sanitize_url(value)
                issues.extend([f"{key}:{item}" for item in key_issues])
                set_field(key, new_value)
            elif key in {"preferred_browser", "last_browser_name"}:
                new_value, key_issues = self._sanitize_browser_name(value)
                issues.extend([f"{key}:{item}" for item in key_issues])
                set_field(key, new_value)
            elif isinstance(value, str):
                normalized = value.replace("\r", " ").replace("\n", " ").strip()
                if normalized != value:
                    sanitized[key] = normalized
                    issues.append(f"{key}:trimmed_string")
                    changed = True

        return sanitized, issues, changed

    def sanitize_all(self) -> dict[str, Any]:
        data = self._load()
        wrappers = data.setdefault("wrappers", {})
        issues: list[dict[str, Any]] = []
        changed = False

        for wrapper_name, raw_state in list(wrappers.items()):
            if not isinstance(raw_state, dict):
                wrappers[wrapper_name] = {}
                issues.append({"wrapper": wrapper_name, "issues": ["reset_non_dict_state"]})
                changed = True
                continue
            sanitized, wrapper_issues, wrapper_changed = self._sanitize_wrapper_state(wrapper_name, raw_state)
            if wrapper_changed:
                wrappers[wrapper_name] = sanitized
                changed = True
            if wrapper_issues:
                issues.append({"wrapper": wrapper_name, "issues": wrapper_issues})

        if changed:
            self._save(data)

        self._last_hygiene_report = {
            "ok": True,
            "changed": changed,
            "issues": issues,
            "count": len(issues),
            "path": str(self.path),
            "plain_english": "Wrapper remembered state was checked and normalized for the current local workspace.",
        }
        return self._last_hygiene_report

    def hygiene_report(self) -> dict[str, Any]:
        if not self._last_hygiene_report.get("path"):
            return self.sanitize_all()
        return self._last_hygiene_report

    def all_states(self) -> dict[str, Any]:
        self.sanitize_all()
        return self._load().get("wrappers", {})

    def get_state(self, wrapper_name: str) -> dict[str, Any]:
        data = self._load().get("wrappers", {})
        state = data.get(wrapper_name, {})
        if not isinstance(state, dict):
            return {}
        sanitized, _, changed = self._sanitize_wrapper_state(wrapper_name, state)
        if changed:
            data = self._load()
            wrappers = data.setdefault("wrappers", {})
            wrappers[wrapper_name] = sanitized
            self._save(data)
        return sanitized

    def update_state(self, wrapper_name: str, **fields: Any) -> dict[str, Any]:
        data = self._load()
        wrappers = data.setdefault("wrappers", {})
        current = wrappers.get(wrapper_name, {})
        if not isinstance(current, dict):
            current = {}

        cleaned = {k: v for k, v in fields.items() if v is not None}
        current.update(cleaned)
        current["updated_at"] = datetime.now(UTC).isoformat()
        sanitized, _, _ = self._sanitize_wrapper_state(wrapper_name, current)
        wrappers[wrapper_name] = sanitized
        self._save(data)
        return sanitized

    def clear_state(self, wrapper_name: str) -> dict[str, Any]:
        data = self._load()
        wrappers = data.setdefault("wrappers", {})
        existed = wrapper_name in wrappers
        wrappers.pop(wrapper_name, None)
        self._save(data)
        return {"ok": True, "wrapper": wrapper_name, "cleared": existed}

    def clear_all(self) -> dict[str, Any]:
        data = {"wrappers": {}}
        self._save(data)
        return {"ok": True, "cleared_all": True}


wrapper_state_service = WrapperStateService()
