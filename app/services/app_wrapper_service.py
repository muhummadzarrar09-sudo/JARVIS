from pathlib import Path
import shutil
import importlib.util
from typing import Any
from urllib.parse import quote_plus, urlparse

from app.core.config import settings
from app.services.browser_tool import browser_tool
from app.services.desktop_tool import desktop_tool
from app.services.file_tool import file_tool
from app.services.process_tool import process_tool
from app.services.trusted_root_service import trusted_root_service
from app.services.wrapper_state_service import wrapper_state_service


class AppWrapperService:
    def __init__(self) -> None:
        self._wrappers = {
            "notepad": {
                "aliases": ["note", "notes"],
                "title_hint": "Notepad",
                "supports": ["open", "focus", "ensure", "status", "quick_note"],
                "risk": "high",
                "notes": "Simple Windows text scratchpad wrapper.",
            },
            "calculator": {
                "aliases": ["calc"],
                "title_hint": "Calculator",
                "supports": ["open", "focus", "ensure", "status"],
                "risk": "medium",
                "notes": "Windows calculator wrapper.",
            },
            "explorer": {
                "aliases": ["fileexplorer", "files"],
                "title_hint": "File Explorer",
                "supports": ["open", "focus", "ensure", "status", "open_path"],
                "risk": "medium",
                "notes": "Open folders in Windows File Explorer.",
            },
            "vscode": {
                "aliases": ["code", "visualstudiocode"],
                "title_hint": "Visual Studio Code",
                "supports": ["open", "focus", "ensure", "status", "open_path", "open_file"],
                "risk": "medium",
                "notes": "Open folders/files in VS Code if `code` is on PATH.",
            },
            "browser": {
                "aliases": ["web", "chromium"],
                "title_hint": "Chrome",
                "supports": ["open", "focus", "ensure", "status", "open_url", "search", "research", "snapshot_url"],
                "risk": "medium",
                "notes": "Real external browser wrapper by default, with managed Playwright control available when needed.",
            },
            "terminal": {
                "aliases": ["powershell", "shell"],
                "title_hint": "PowerShell",
                "supports": ["open", "focus", "ensure", "status", "open_path", "run_command"],
                "risk": "high",
                "notes": "Open a terminal / PowerShell session.",
            },
        }
        self._recipes = {
            "note.quick": {
                "aliases": ["quicknote", "note"],
                "inputs": ["text"],
                "risk": "high",
                "notes": "Ensure Notepad, focus it, and type a quick note.",
            },
            "explorer.workspace": {
                "aliases": ["workspace", "openfolder"],
                "inputs": ["path?"],
                "risk": "medium",
                "notes": "Open File Explorer at a workspace path.",
            },
            "vscode.project": {
                "aliases": ["project.code", "code.workspace"],
                "inputs": ["path?"],
                "risk": "medium",
                "notes": "Ensure a project folder is open in VS Code and focus it.",
            },
            "vscode.file": {
                "aliases": ["code.file", "openfile"],
                "inputs": ["path"],
                "risk": "medium",
                "notes": "Open a specific file in VS Code and focus the editor.",
            },
            "vscode.readme": {
                "aliases": ["code.readme", "openreadme"],
                "inputs": ["path?"],
                "risk": "medium",
                "notes": "Find and open a README-like file in VS Code.",
            },
            "vscode.resume": {
                "aliases": ["code.resume", "resumefile"],
                "inputs": ["path?"],
                "risk": "medium",
                "notes": "Resume the last remembered VS Code file or project, or fall back to README/project context.",
            },
            "terminal.project": {
                "aliases": ["project.shell", "shellhere"],
                "inputs": ["path?"],
                "risk": "high",
                "notes": "Ensure a PowerShell window rooted at a project path.",
            },
            "terminal.command": {
                "aliases": ["shell.command", "runcommand"],
                "inputs": ["command or path || command"],
                "risk": "high",
                "notes": "Ensure a terminal, optionally at a path, then type a command and press Enter.",
            },
            "browser.search": {
                "aliases": ["search", "web.search"],
                "inputs": ["query"],
                "risk": "medium",
                "notes": "Run a browser search in the real external browser by default.",
            },
            "browser.site_search": {
                "aliases": ["web.site_search", "site.search"],
                "inputs": ["query"],
                "risk": "medium",
                "notes": "Search only within the currently remembered or active site.",
            },
            "browser.research": {
                "aliases": ["research", "web.research"],
                "inputs": ["query"],
                "risk": "medium",
                "notes": "Search the web and pull back a visible text snapshot for quick review.",
            },
            "browser.snapshot": {
                "aliases": ["web.snapshot", "open.snapshot"],
                "inputs": ["url?"],
                "risk": "medium",
                "notes": "Open a URL in controlled browser mode and snapshot visible page text.",
            },
            "browser.resume": {
                "aliases": ["web.resume", "resumebrowser"],
                "inputs": ["url?"],
                "risk": "medium",
                "notes": "Resume the current or last remembered browser page in controlled mode and capture context.",
            },
            "project.inspect": {
                "aliases": ["workspace.inspect", "project.scan"],
                "inputs": ["path?"],
                "risk": "low",
                "notes": "Inspect a workspace path, detect common project files, and remember it for wrappers.",
            },
            "project.review": {
                "aliases": ["workspace.review", "reviewproject"],
                "inputs": ["path?"],
                "risk": "low",
                "notes": "Inspect the project and open or preview the README so you can quickly understand the workspace.",
            },
            "coding.start": {
                "aliases": ["startcoding", "workspace.code"],
                "inputs": ["path?"],
                "risk": "high",
                "notes": "Get ready to code by opening the project in code and terminal flows.",
            },
            "coding.resume": {
                "aliases": ["resumecoding", "continuecoding"],
                "inputs": ["path?"],
                "risk": "high",
                "notes": "Resume the last coding workspace using remembered project and code state.",
            },
            "project.files": {
                "aliases": ["workspace.files", "showfiles"],
                "inputs": ["path?"],
                "risk": "low",
                "notes": "Open or preview the current project folder contents.",
            },
            "browser.page_review": {
                "aliases": ["page.review", "reviewpage"],
                "inputs": ["url?"],
                "risk": "medium",
                "notes": "Review the current or remembered browser page with controlled title/text context.",
            },
            "project.starter": {
                "aliases": ["workspace.start", "project.start"],
                "inputs": ["path?"],
                "risk": "high",
                "notes": "Ensure Explorer, VS Code, and a project terminal for one workspace path.",
            },
            "project.resume": {
                "aliases": ["workspace.resume", "resumeproject"],
                "inputs": ["path?"],
                "risk": "high",
                "notes": "Resume a remembered project path across Explorer, VS Code, and terminal wrappers.",
            },
        }

    def list_wrappers(self) -> dict[str, Any]:
        items = []
        for name, meta in self._wrappers.items():
            items.append(
                {
                    "name": name,
                    "aliases": meta["aliases"],
                    "title_hint": meta["title_hint"],
                    "supports": meta["supports"],
                    "risk": meta["risk"],
                    "notes": meta["notes"],
                }
            )
        return {"ok": True, "count": len(items), "items": items}

    def list_recipes(self) -> dict[str, Any]:
        items = []
        for name, meta in self._recipes.items():
            items.append(
                {
                    "name": name,
                    "aliases": meta["aliases"],
                    "inputs": meta["inputs"],
                    "risk": meta["risk"],
                    "notes": meta["notes"],
                }
            )
        return {"ok": True, "count": len(items), "items": items}

    def _normalize_name(self, name: str) -> str | None:
        raw = name.strip().lower()
        if raw in self._wrappers:
            return raw
        for canonical, meta in self._wrappers.items():
            if raw in meta["aliases"]:
                return canonical
        return None

    def _normalize_recipe(self, name: str) -> str | None:
        raw = name.strip().lower()
        if raw in self._recipes:
            return raw
        for canonical, meta in self._recipes.items():
            if raw in meta["aliases"]:
                return canonical
        return None

    def _quote(self, value: str) -> str:
        return '"' + value.replace('"', '\\"') + '"'

    def _default_path(self, target: str | None = None) -> str:
        cleaned = (target or ".").strip()
        return cleaned or "."

    def _preferred_project_target(self, target: str | None = None) -> str:
        cleaned = (target or "").strip()
        candidate = cleaned if cleaned else None

        if not candidate:
            for wrapper_name in ("vscode", "explorer", "terminal"):
                state = wrapper_state_service.get_state(wrapper_name)
                remembered = state.get("last_path") or state.get("last_target")
                if isinstance(remembered, str) and remembered.strip():
                    candidate = remembered.strip()
                    break

        if not candidate:
            return "."

        try:
            resolved = self._resolve_workspace_path(candidate)
            if not resolved.exists():
                return "."
            if resolved.is_file():
                return str(resolved.parent)
            return str(resolved)
        except Exception:
            return "."

    def _preferred_browser_name(self, explicit: str | None = None) -> str | None:
        cleaned = (explicit or "").strip().lower()
        if cleaned:
            return cleaned
        state = wrapper_state_service.get_state("browser")
        preferred = state.get("preferred_browser") or state.get("last_browser_name")
        if isinstance(preferred, str) and preferred.strip():
            return preferred.strip().lower()
        return None

    def _browser_title_hint(self, browser_name: str | None = None) -> str:
        chosen = self._preferred_browser_name(browser_name) or "chrome"
        mapping = {
            "chrome": "Google Chrome",
            "msedge": "Microsoft Edge",
            "brave": "Brave",
            "firefox": "Firefox",
            "playwright_chromium": "Chromium",
        }
        return mapping.get(chosen, "Chrome")

    def _steps_ok(self, steps: list[dict[str, Any]]) -> bool:
        return all(step.get("result", {}).get("ok") for step in steps)

    def _read_text_preview(self, path: Path, max_chars: int = 500) -> str | None:
        try:
            return path.read_text(encoding="utf-8")[:max_chars]
        except Exception:
            return None

    def _match_title_hint(self, title_hint: str, window_title: str) -> bool:
        return title_hint.lower() in (window_title or "").lower()

    def _remember_wrapper(self, wrapper: str, **fields: Any) -> dict[str, Any]:
        return wrapper_state_service.update_state(wrapper, **fields)

    def _workspace_root(self) -> Path:
        return Path(settings.workspace_root).resolve()

    def _resolve_workspace_path(self, target: str | None = None) -> Path:
        raw = self._default_path(target)
        policy = trusted_root_service.resolve(raw)
        if not policy.get("ok"):
            raise ValueError(policy.get("error") or f"Path is not inside a trusted root: {raw}")
        resolved = policy.get("resolved")
        if not isinstance(resolved, Path):
            raise ValueError(f"Could not resolve trusted path: {raw}")
        return resolved

    def _project_summary(self, target: str | None = None) -> dict[str, Any]:
        try:
            path = self._resolve_workspace_path(target)
        except Exception as e:
            return {"ok": False, "error": str(e)}

        if not path.exists():
            return {"ok": False, "error": f"Path does not exist: {path}"}
        if not path.is_dir():
            return {"ok": False, "error": f"Not a directory: {path}"}

        marker_names = [
            "README.md",
            "README.txt",
            "readme.md",
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            "Cargo.toml",
            ".gitignore",
            "app",
            "src",
            "tests",
        ]
        found = []
        for name in marker_names:
            item = path / name
            if item.exists():
                found.append({"name": name, "is_dir": item.is_dir()})

        files = sorted([p.name for p in path.iterdir() if p.is_file()])[:25]
        dirs = sorted([p.name for p in path.iterdir() if p.is_dir()])[:25]
        readme = self._find_readme(path)

        project_type = []
        if (path / "pyproject.toml").exists() or (path / "requirements.txt").exists():
            project_type.append("python")
        if (path / "package.json").exists():
            project_type.append("javascript")
        if (path / "Cargo.toml").exists():
            project_type.append("rust")
        if not project_type:
            project_type.append("generic")

        return {
            "ok": True,
            "path": str(path),
            "project_type": project_type,
            "markers": found,
            "top_files": files,
            "top_dirs": dirs,
            "readme": str(readme) if readme else None,
            "readme_preview": self._read_text_preview(readme) if readme else None,
        }

    def _find_readme(self, path: Path) -> Path | None:
        candidates = [
            path / "README.md",
            path / "readme.md",
            path / "README.txt",
            path / "Readme.md",
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate
        return None

    def _parse_command_payload(self, payload: str) -> tuple[str | None, str | None]:
        raw = payload.strip()
        if not raw:
            return None, None
        if "||" in raw:
            left, right = raw.split("||", 1)
            path = left.strip() or None
            command = right.strip() or None
            return path, command
        return None, raw

    def _domain_from_url(self, url: str | None) -> str | None:
        if not url:
            return None
        try:
            parsed = urlparse(url)
            host = (parsed.netloc or "").strip().lower()
            if host.startswith("www."):
                host = host[4:]
            return host or None
        except Exception:
            return None

    def _readme_fallback(self, readme_path: str, summary: dict[str, Any], reason: str) -> dict[str, Any]:
        workspace_root = str(self._workspace_root())
        preview_result = file_tool.read_text(readme_path)
        return {
            "ok": True,
            "fallback": "readme_preview",
            "reason": reason,
            "workspace_root": workspace_root,
            "readme": readme_path,
            "summary": summary,
            "preview": preview_result.get("content") if preview_result.get("ok") else summary.get("readme_preview"),
            "preview_ok": preview_result.get("ok", False),
        }

    def _directory_fallback(self, target: str, reason: str) -> dict[str, Any]:
        summary = self._project_summary(target)
        listing = file_tool.list_dir(target)
        return {
            "ok": True,
            "fallback": "directory_listing",
            "reason": reason,
            "target": target,
            "summary": summary if summary.get("ok") else None,
            "listing": listing,
        }

    def _browser_link_fallback(self, url: str, reason: str, query: str | None = None, browser_name: str | None = None) -> dict[str, Any]:
        preferred = (browser_name or "").strip().lower()
        browser_label = {
            "chrome": "Chrome",
            "msedge": "Edge",
            "brave": "Brave",
            "firefox": "Firefox",
        }.get(preferred, "a browser")
        return {
            "ok": True,
            "fallback": "browser_link",
            "reason": reason,
            "plain_english": f"JARVIS could not control {browser_label} here, so it prepared a link you can open manually.",
            "url": url,
            "query": query,
            "browser_name": preferred or None,
            "manual_steps": [
                f"Open {browser_label} on your computer." if preferred else "Open any browser on your computer.",
                f"Paste this URL: {url}",
            ],
            "next_action": f"Open this link manually: {url}",
        }

    def _detect_browser_windows(self) -> dict[str, Any]:
        windows = desktop_tool.list_windows()
        if not windows.get("ok"):
            return {"ok": False, "items": [], "error": windows.get("error")}

        preferred_browser = self._preferred_browser_name()
        signatures = {
            "chrome": ["google chrome", "chrome"],
            "msedge": ["microsoft edge", "edge"],
            "brave": ["brave"],
            "firefox": ["firefox"],
        }
        detected = []
        for item in windows.get("items", []):
            title = (item.get("title") or "").lower()
            for browser_name, fragments in signatures.items():
                if any(fragment in title for fragment in fragments):
                    detected.append({**item, "browser_name": browser_name})
                    break
        active = next((item for item in detected if item.get("is_active")), None)
        preferred_window = next((item for item in detected if item.get("browser_name") == preferred_browser), None)
        running_names = sorted({item.get("browser_name") for item in detected if item.get("browser_name")})
        return {
            "ok": True,
            "items": detected,
            "active": active,
            "count": len(detected),
            "running_browser_names": running_names,
            "preferred_browser": preferred_browser,
            "preferred_window": preferred_window,
            "preferred_running": bool(preferred_window),
        }

    def _workspace_start_fallback(self, path: str, reason: str) -> dict[str, Any]:
        summary = self._project_summary(path)
        listing = file_tool.list_dir(path)
        readme = None
        if summary.get("ok") and summary.get("readme"):
            readme = self._readme_fallback(summary.get("readme"), summary, "JARVIS could not open the coding apps here, so it returned the README preview instead.")
        return {
            "ok": True,
            "fallback": "workspace_start_fallback",
            "reason": reason,
            "target": path,
            "summary": summary if summary.get("ok") else None,
            "listing": listing,
            "readme_preview": readme,
            "manual_steps": [
                f"Open this project folder manually: {path}",
                "If you have VS Code installed, open the folder there.",
                "If you have a terminal available, open it in that folder to continue working.",
            ],
            "next_action": f"Start from this project folder: {path}",
        }

    def current_project_context(self, target: str | None = None) -> dict[str, Any]:
        preferred = self._preferred_project_target(target)
        summary = self._project_summary(preferred)
        if not summary.get("ok") and preferred != ".":
            summary = self._project_summary(".")
        if not summary.get("ok"):
            return summary

        wrapper_states = {
            name: wrapper_state_service.get_state(name)
            for name in ("explorer", "vscode", "terminal", "browser")
        }
        recommended_recipes = [
            "project.inspect",
            "project.starter",
            "project.resume",
            "vscode.readme",
            "terminal.command",
        ]
        if not summary.get("readme"):
            recommended_recipes = [item for item in recommended_recipes if item != "vscode.readme"]
        return {
            "ok": True,
            "path": summary.get("path"),
            "summary": summary,
            "wrapper_states": wrapper_states,
            "recommended_recipes": recommended_recipes,
        }

    def current_browser_context(self) -> dict[str, Any]:
        state = browser_tool.state()
        remembered = wrapper_state_service.get_state("browser")
        available = browser_tool.available_browsers()
        preference = available.get("preference", []) if available.get("ok") else []
        candidates = available.get("items", []) if available.get("ok") else []
        default_candidate = available.get("default_candidate") if available.get("ok") else None
        default_external_candidate = available.get("default_external_candidate") if available.get("ok") else None
        preferred_browser = remembered.get("preferred_browser") or remembered.get("last_browser_name") or ((default_external_candidate or {}).get("name")) or ((default_candidate or {}).get("name"))
        desktop_browser = self._detect_browser_windows()
        running_names = desktop_browser.get("running_browser_names", []) if desktop_browser.get("ok") else []
        preferred_window = desktop_browser.get("preferred_window") if desktop_browser.get("ok") else None
        preferred_running = bool(desktop_browser.get("preferred_running")) if desktop_browser.get("ok") else False
        last_launch_mode = remembered.get("last_launch_mode") or "external"
        label_map = {
            "chrome": "Chrome",
            "msedge": "Edge",
            "brave": "Brave",
            "firefox": "Firefox",
            "playwright_chromium": "Playwright Chromium",
        }

        if not state.get("ok"):
            return state

        if not state.get("started"):
            remembered_url = remembered.get("last_url") or remembered.get("last_target")
            active_browser = desktop_browser.get("active") if desktop_browser.get("ok") else None
            active_title = active_browser.get("title") if active_browser else None
            plain = "JARVIS is set to use your real external browser by default."
            next_action = "Say: open browser"

            if active_title and preferred_running and preferred_browser:
                plain = f"{label_map.get(preferred_browser, preferred_browser)} is already open, and JARVIS can keep using it in external mode."
                next_action = "Say: search for something or open browser to a URL"
            elif active_title:
                plain = "A real browser window is already open, and JARVIS can keep using external mode by default."
                next_action = "Say: search for something, open browser to a URL, or show browser options"
            elif remembered_url:
                plain = "No controlled browser session is open, but JARVIS remembers your last page and can reopen or review it."
                next_action = "Say: open browser or show me the current page"

            return {
                "ok": True,
                "started": False,
                "managed_session_started": False,
                "default_mode": "external",
                "last_launch_mode": last_launch_mode,
                "url": None,
                "title": None,
                "text": None,
                "remembered_url": remembered_url,
                "preferred_browser": preferred_browser,
                "preference": preference,
                "default_candidate": default_candidate,
                "default_external_candidate": default_external_candidate,
                "available_browsers": candidates,
                "detected_browser_windows": desktop_browser.get("items") if desktop_browser.get("ok") else [],
                "active_browser_window": active_browser,
                "preferred_browser_window": preferred_window,
                "running_browser_names": running_names,
                "preferred_browser_running": preferred_running,
                "plain_english": plain,
                "next_action": next_action,
            }

        title = browser_tool.title()
        text = browser_tool.text_snapshot(max_chars=2000)
        selected_browser = title.get("browser_name") or state.get("browser_name")
        return {
            "ok": bool(title.get("ok") and text.get("ok")),
            "started": True,
            "managed_session_started": True,
            "default_mode": "external",
            "last_launch_mode": "playwright_managed",
            "url": title.get("url") or state.get("url"),
            "title": title.get("title") or state.get("title"),
            "text": text.get("text"),
            "text_truncated": text.get("truncated"),
            "remembered_url": remembered.get("last_url") or remembered.get("last_target"),
            "preferred_browser": preferred_browser,
            "selected_browser": selected_browser,
            "selected_launch_mode": "playwright_managed",
            "preference": preference,
            "default_candidate": default_candidate,
            "default_external_candidate": default_external_candidate,
            "available_browsers": candidates,
            "detected_browser_windows": desktop_browser.get("items") if desktop_browser.get("ok") else [],
            "active_browser_window": desktop_browser.get("active") if desktop_browser.get("ok") else None,
            "preferred_browser_window": preferred_window,
            "running_browser_names": running_names,
            "preferred_browser_running": preferred_running,
            "plain_english": "A controlled browser session is currently available." if (title.get("ok") and text.get("ok")) else "A controlled browser session is running, but some page details were unavailable.",
            "next_action": "Say: show me the current page, search for something, or browser text",
        }

    def set_browser_preference(self, browser_name: str | None) -> dict[str, Any]:
        raw = (browser_name or "").strip().lower()
        if raw in {"", "auto", "default", "system"}:
            state = self._remember_wrapper("browser", preferred_browser="")
            return {
                "ok": True,
                "preferred_browser": None,
                "plain_english": "JARVIS will now use the normal browser preference order.",
                "next_action": "Try: show browser options",
                "state": state,
            }

        available = browser_tool.available_browsers()
        candidate_names = {item.get("name") for item in available.get("items", [])}
        aliases = {"edge": "msedge", "chromium": "playwright_chromium"}
        normalized = aliases.get(raw, raw)
        if normalized not in candidate_names and normalized not in {"chrome", "msedge", "brave", "firefox", "playwright_chromium"}:
            return {
                "ok": False,
                "error": f"Unknown browser preference: {browser_name}",
                "available": sorted(candidate_names),
            }

        state = self._remember_wrapper("browser", preferred_browser=normalized)
        return {
            "ok": True,
            "preferred_browser": normalized,
            "plain_english": f"JARVIS will try {normalized} first for future browser actions.",
            "next_action": f"Try: open {normalized if normalized != 'msedge' else 'edge'}",
            "state": state,
        }

    def wrapper_doctor(self, name: str | None = None) -> dict[str, Any]:
        wrappers = [self._normalize_name(name)] if name else list(self._wrappers.keys())
        if name and wrappers[0] is None:
            return {"ok": False, "error": f"Unknown app wrapper: {name}"}

        items = []
        browser_context = self.current_browser_context()
        desktop_info = desktop_tool.screen_info()
        desktop_active = desktop_tool.active_window()

        for canonical in wrappers:
            if canonical is None:
                continue
            state = wrapper_state_service.get_state(canonical)
            tool_status = self.wrapper_status(canonical)
            if canonical == "browser":
                playwright_installed = importlib.util.find_spec("playwright") is not None
                available = browser_tool.available_browsers()
                external_ready = bool(available.get("default_external_candidate")) or settings.allow_browser_tool
                managed_ready = playwright_installed
                items.append(
                    {
                        "name": canonical,
                        "ready": external_ready or managed_ready,
                        "external_ready": external_ready,
                        "managed_ready": managed_ready,
                        "notes": "Defaults to opening the real external browser first. Managed Playwright control is available when installed.",
                        "playwright_installed": playwright_installed,
                        "available_browsers": available.get("items", []),
                        "preference": available.get("preference", []),
                        "default_candidate": available.get("default_candidate"),
                        "default_external_candidate": available.get("default_external_candidate"),
                        "status": tool_status.get("item"),
                        "context": browser_context,
                        "remembered_state": state,
                    }
                )
                continue

            if canonical == "vscode":
                code_path = shutil.which("code")
                items.append(
                    {
                        "name": canonical,
                        "ready": bool(code_path),
                        "notes": "Requires `code` on PATH for app recipes to launch VS Code reliably.",
                        "binary": code_path,
                        "status": tool_status.get("item"),
                        "remembered_state": state,
                    }
                )
                continue

            if canonical == "terminal":
                powershell_path = shutil.which("powershell") or shutil.which("pwsh")
                items.append(
                    {
                        "name": canonical,
                        "ready": bool(powershell_path),
                        "notes": "Requires PowerShell available locally.",
                        "binary": powershell_path,
                        "status": tool_status.get("item"),
                        "remembered_state": state,
                    }
                )
                continue

            items.append(
                {
                    "name": canonical,
                    "ready": desktop_info.get("ok", False) or desktop_active.get("ok", False),
                    "notes": "Depends on Windows desktop control packages and focus/window enumeration.",
                    "status": tool_status.get("item"),
                    "remembered_state": state,
                }
            )

        result = {"ok": True, "count": len(items), "items": items}
        if name:
            result["item"] = items[0] if items else None
        return result

    def reset_wrapper_state(self, name: str | None = None) -> dict[str, Any]:
        if name is None or not name.strip() or name.strip().lower() == "all":
            return wrapper_state_service.clear_all()
        canonical = self._normalize_name(name)
        if not canonical:
            return {"ok": False, "error": f"Unknown app wrapper: {name}"}
        return wrapper_state_service.clear_state(canonical)

    def wrapper_status(self, name: str | None = None) -> dict[str, Any]:
        if name:
            canonical = self._normalize_name(name)
            if not canonical:
                return {"ok": False, "error": f"Unknown app wrapper: {name}"}
            wrappers = [canonical]
        else:
            wrappers = list(self._wrappers.keys())

        desktop_windows = desktop_tool.list_windows()
        active_window = desktop_tool.active_window()
        browser_state = browser_tool.state()
        browser_windows = self._detect_browser_windows()

        items = []
        for canonical in wrappers:
            meta = self._wrappers[canonical]
            state = wrapper_state_service.get_state(canonical)
            title_hint = meta["title_hint"]
            matches: list[dict[str, Any]] = []
            active = False
            running = False
            extra: dict[str, Any] = {"remembered_state": state}

            if canonical == "browser":
                title_hint = self._browser_title_hint(state.get("preferred_browser") or state.get("last_browser_name"))
                running = bool(browser_state.get("started"))
                if browser_windows.get("ok"):
                    matches = browser_windows.get("items", [])
                    running = running or bool(matches)
                    active = browser_windows.get("active") is not None
                    extra["browser_windows"] = matches[:5]
                    extra["running_browser_names"] = browser_windows.get("running_browser_names", [])
                    extra["preferred_browser"] = browser_windows.get("preferred_browser")
                    extra["preferred_running"] = browser_windows.get("preferred_running")
                else:
                    extra["desktop_error"] = browser_windows.get("error")
                extra["browser_state"] = browser_state if browser_state.get("ok") else None
            else:
                if desktop_windows.get("ok"):
                    matches = [item for item in desktop_windows.get("items", []) if self._match_title_hint(title_hint, item.get("title", ""))]
                    running = bool(matches)
                    active = any(item.get("is_active") for item in matches)
                else:
                    extra["desktop_error"] = desktop_windows.get("error")

            if active_window.get("ok") and active_window.get("window"):
                active_title = active_window.get("window", {}).get("title", "")
                if canonical == "browser":
                    if browser_windows.get("active"):
                        active = True
                        running = True
                elif self._match_title_hint(title_hint, active_title):
                    active = True
                    running = True

            items.append(
                {
                    "name": canonical,
                    "title_hint": title_hint,
                    "running": running,
                    "active": active,
                    "match_count": len(matches),
                    "matches": [item.get("title") for item in matches[:5]],
                    **extra,
                }
            )

        if name:
            return {"ok": True, "item": items[0]}
        return {"ok": True, "count": len(items), "items": items}

    def _target_capable(self, canonical: str) -> bool:
        return canonical in {"browser", "explorer", "vscode", "terminal"}

    def open_app(self, name: str, target: str | None = None, browser_name: str | None = None, launch_mode: str | None = None) -> dict[str, Any]:
        canonical = self._normalize_name(name)
        if not canonical:
            return {"ok": False, "error": f"Unknown app wrapper: {name}"}

        if canonical == "browser":
            url = (target or "https://example.com").strip()
            chosen_browser = self._preferred_browser_name(browser_name)
            requested_mode = (launch_mode or "external").strip().lower()
            if requested_mode in {"managed", "controlled", "playwright", "playwright_managed"}:
                result = browser_tool.open_url(url, browser_name=chosen_browser)
                actual_mode = "playwright_managed"
            else:
                result = browser_tool.launch_external_url(url, browser_name=chosen_browser)
                actual_mode = result.get("mode") or "external"
            actual_browser = result.get("browser_name") or result.get("selected_browser") or chosen_browser
            self._remember_wrapper(
                canonical,
                last_action="open",
                last_target=url,
                last_url=url,
                last_browser_name=actual_browser,
                last_launch_mode=actual_mode,
                last_result_ok=result.get("ok"),
            )
            return {
                "ok": result.get("ok", False),
                "wrapper": canonical,
                "target": url,
                "mode": actual_mode,
                "requested_browser": chosen_browser,
                "browser_name": actual_browser,
                "result": result,
                "plain_english": result.get("plain_english"),
                "next_action": result.get("next_action"),
            }

        if canonical == "notepad":
            result = process_tool.start_process("notepad")
        elif canonical == "calculator":
            result = process_tool.start_process("calc")
        elif canonical == "explorer":
            cmd = "explorer"
            if target and target.strip():
                cmd = f'explorer {self._quote(target.strip())}'
            result = process_tool.start_process(cmd)
        elif canonical == "vscode":
            cmd = "code"
            if target and target.strip():
                cmd = f'code {self._quote(target.strip())}'
            result = process_tool.start_process(cmd)
        elif canonical == "terminal":
            cmd = "start powershell"
            if target and target.strip():
                quoted = self._quote(target.strip())
                cmd = f'start powershell -NoExit -Command Set-Location -LiteralPath {quoted}'
            result = process_tool.start_process(cmd)
        else:
            return {"ok": False, "error": f"Wrapper not implemented yet: {canonical}"}

        remembered = {"last_action": "open", "last_result_ok": result.get("ok")}
        if target and target.strip():
            remembered["last_target"] = target.strip()
            if canonical in {"explorer", "vscode", "terminal"}:
                remembered["last_path"] = target.strip()
        self._remember_wrapper(canonical, **remembered)

        return {
            "ok": result.get("ok", False),
            "wrapper": canonical,
            "target": target,
            "title_hint": self._wrappers[canonical]["title_hint"],
            "result": result,
        }

    def focus_app(self, name: str, exact: bool = False) -> dict[str, Any]:
        canonical = self._normalize_name(name)
        if not canonical:
            return {"ok": False, "error": f"Unknown app wrapper: {name}"}
        title_hint = self._wrappers[canonical]["title_hint"]
        result = desktop_tool.focus_window(title_hint, exact=exact)
        self._remember_wrapper(canonical, last_action="focus", last_result_ok=result.get("ok"), last_focus_exact=exact)
        return {
            "ok": result.get("ok", False),
            "wrapper": canonical,
            "title_hint": title_hint,
            "exact": exact,
            "result": result,
        }

    def ensure_app(self, name: str, target: str | None = None, exact: bool = False, browser_name: str | None = None, launch_mode: str | None = None) -> dict[str, Any]:
        canonical = self._normalize_name(name)
        if not canonical:
            return {"ok": False, "error": f"Unknown app wrapper: {name}"}

        state = wrapper_state_service.get_state(canonical)
        if (not target or not target.strip()) and self._target_capable(canonical):
            target = state.get("last_target") or state.get("last_path") or state.get("last_url")
        if not browser_name:
            browser_name = state.get("last_browser_name")

        steps: list[dict[str, Any]] = []
        status_before = self.wrapper_status(canonical)
        steps.append({"step": "status_before", "result": status_before})
        item = status_before.get("item", {})

        if canonical == "browser":
            url = (target or "https://example.com").strip()
            open_result = self.open_url_in_browser(url, browser_name=browser_name, launch_mode=launch_mode)
            steps.append({"step": "open_or_navigate_browser", "result": open_result})
            result = {
                "ok": self._steps_ok(steps),
                "wrapper": canonical,
                "target": url,
                "workflow": "ensure",
                "browser_name": open_result.get("browser_name") or browser_name,
                "mode": open_result.get("mode") or launch_mode or "external",
                "steps": steps,
                "plain_english": open_result.get("plain_english"),
                "next_action": open_result.get("next_action"),
            }
            if open_result.get("fallback"):
                result["fallback"] = open_result.get("fallback")
                result["reason"] = open_result.get("reason")
                result["manual_steps"] = open_result.get("manual_steps")
            self._remember_wrapper(
                canonical,
                last_action="ensure",
                last_result_ok=result.get("ok"),
                last_target=url,
                last_url=url,
                last_browser_name=result.get("browser_name"),
                last_launch_mode=result.get("mode"),
            )
            return result

        if target and self._target_capable(canonical):
            open_result = self.open_app(canonical, target=target, browser_name=browser_name)
            steps.append({"step": "open_targeted_instance", "result": open_result})
            focus_result = self.focus_app(canonical, exact=exact)
            steps.append({"step": "focus_after_open", "result": focus_result})
            result = {"ok": self._steps_ok(steps), "wrapper": canonical, "target": target, "workflow": "ensure", "browser_name": browser_name, "steps": steps}
            self._remember_wrapper(canonical, last_action="ensure", last_result_ok=result.get("ok"), last_target=target, last_browser_name=browser_name)
            return result

        if item.get("running"):
            focus_result = self.focus_app(canonical, exact=exact)
            steps.append({"step": "focus_existing", "result": focus_result})
            result = {"ok": self._steps_ok(steps), "wrapper": canonical, "workflow": "ensure", "browser_name": browser_name, "steps": steps}
            self._remember_wrapper(canonical, last_action="ensure", last_result_ok=result.get("ok"), last_browser_name=browser_name)
            return result

        open_result = self.open_app(canonical, target=target, browser_name=browser_name)
        steps.append({"step": "open_app", "result": open_result})
        focus_result = self.focus_app(canonical, exact=exact)
        steps.append({"step": "focus_after_open", "result": focus_result})
        result = {"ok": self._steps_ok(steps), "wrapper": canonical, "target": target, "workflow": "ensure", "browser_name": browser_name, "steps": steps}
        self._remember_wrapper(canonical, last_action="ensure", last_result_ok=result.get("ok"), last_target=target, last_browser_name=browser_name)
        return result

    def quick_note(self, text: str) -> dict[str, Any]:
        if not text.strip():
            return {"ok": False, "error": "Note text is required."}

        steps = []
        ensure_result = self.ensure_app("notepad")
        steps.append({"step": "ensure_notepad", "result": ensure_result})

        type_result = desktop_tool.type_text(text)
        steps.append({"step": "type_note", "result": type_result})

        result = {
            "ok": self._steps_ok(steps),
            "wrapper": "notepad",
            "workflow": "quick_note",
            "steps": steps,
        }
        self._remember_wrapper("notepad", last_action="quick_note", last_text_preview=text[:120], last_result_ok=result.get("ok"))
        return result

    def open_path_in_explorer(self, target: str) -> dict[str, Any]:
        path = target.strip()
        if not path:
            return {"ok": False, "error": "Path is required."}
        doctor = self.wrapper_doctor("explorer")
        item = doctor.get("item") or {}
        if item and not item.get("ready"):
            fallback = self._directory_fallback(path, "File Explorer is not ready here, so JARVIS returned the folder contents instead.")
            self._remember_wrapper("explorer", last_path=path, last_target=path, last_result_ok=fallback.get("ok"))
            return fallback
        return self.open_app("explorer", target=path)

    def open_path_in_vscode(self, target: str) -> dict[str, Any]:
        path = target.strip()
        if not path:
            return {"ok": False, "error": "Path is required."}
        doctor = self.wrapper_doctor("vscode")
        item = doctor.get("item") or {}
        if item and not item.get("ready"):
            summary = self._project_summary(path)
            readme = summary.get("readme") if summary.get("ok") else None
            if readme:
                fallback = self._readme_fallback(readme, summary, "VS Code is not ready here, so JARVIS returned the project README preview instead.")
                self._remember_wrapper("vscode", last_path=path, last_target=path, last_result_ok=fallback.get("ok"))
                return fallback
            fallback = self._directory_fallback(path, "VS Code is not ready here, so JARVIS returned the project folder contents instead.")
            self._remember_wrapper("vscode", last_path=path, last_target=path, last_result_ok=fallback.get("ok"))
            return fallback
        return self.open_app("vscode", target=path)

    def open_url_in_browser(self, url: str, browser_name: str | None = None, launch_mode: str | None = None) -> dict[str, Any]:
        clean_url = url.strip()
        if not clean_url:
            return {"ok": False, "error": "URL is required."}
        requested_browser = self._preferred_browser_name(browser_name)
        desired_mode = (launch_mode or "external").strip().lower()
        desired_mode = "playwright_managed" if desired_mode in {"managed", "controlled", "playwright", "playwright_managed"} else "external"
        doctor = self.wrapper_doctor("browser")
        item = doctor.get("item") or {}

        if item and desired_mode == "external" and not item.get("external_ready"):
            fallback = self._browser_link_fallback(clean_url, "External browser launch is not ready here, so JARVIS returned a manual link instead.", browser_name=requested_browser)
            fallback["mode"] = desired_mode
            self._remember_wrapper("browser", last_url=clean_url, last_target=clean_url, last_browser_name=requested_browser, last_launch_mode=desired_mode, last_result_ok=fallback.get("ok"))
            return fallback

        if item and desired_mode == "playwright_managed" and not item.get("managed_ready"):
            fallback = self._browser_link_fallback(clean_url, "Controlled browser mode is not ready here, so JARVIS returned a manual link instead.", browser_name=requested_browser)
            fallback["mode"] = desired_mode
            fallback["next_action"] = f"Open this link manually: {clean_url}"
            self._remember_wrapper("browser", last_url=clean_url, last_target=clean_url, last_browser_name=requested_browser, last_launch_mode=desired_mode, last_result_ok=fallback.get("ok"))
            return fallback

        result = self.open_app("browser", target=clean_url, browser_name=requested_browser, launch_mode=desired_mode)
        if result.get("ok"):
            return result

        nested = result.get("result") if isinstance(result.get("result"), dict) else {}
        reason = nested.get("error") or result.get("error") or "Browser launch could not open the page here."
        fallback_reason = (
            f"JARVIS could not open the real browser here ({reason})."
            if desired_mode == "external"
            else f"JARVIS could not start the controlled browser session here ({reason})."
        )
        fallback = self._browser_link_fallback(clean_url, fallback_reason, browser_name=requested_browser)
        fallback["launch_result"] = result
        fallback["mode"] = desired_mode
        self._remember_wrapper("browser", last_url=clean_url, last_target=clean_url, last_browser_name=requested_browser, last_launch_mode=desired_mode, last_result_ok=fallback.get("ok"))
        return fallback

    def run_recipe(self, name: str, target: str | None = None, text: str | None = None) -> dict[str, Any]:
        canonical = self._normalize_recipe(name)
        if not canonical:
            return {"ok": False, "error": f"Unknown app recipe: {name}"}

        payload = (text if text is not None else target or "").strip()
        steps: list[dict[str, Any]] = []

        if canonical == "note.quick":
            if not payload:
                return {"ok": False, "error": "This recipe needs text. Use app recipe: note.quick ::: your text"}
            result = self.quick_note(payload)
            self._remember_wrapper("notepad", last_recipe=canonical, last_result_ok=result.get("ok"))
            return {"ok": result.get("ok", False), "recipe": canonical, "result": result}

        if canonical == "explorer.workspace":
            path = self._default_path(target)
            result = self.ensure_app("explorer", target=path)
            self._remember_wrapper("explorer", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            return {"ok": result.get("ok", False), "recipe": canonical, "target": path, "result": result}

        if canonical == "vscode.project":
            path = self._preferred_project_target(target)
            ensure_result = self.ensure_app("vscode", target=path)
            steps.append({"step": "ensure_vscode_project", "result": ensure_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "target": path, "steps": steps}
            self._remember_wrapper("vscode", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            return result

        if canonical == "vscode.file":
            file_path = payload
            if not file_path:
                return {"ok": False, "error": "This recipe needs a file path. Use app recipe: vscode.file ::: path/to/file"}
            open_result = self.open_app("vscode", target=file_path)
            steps.append({"step": "open_file_in_vscode", "result": open_result})
            focus_result = self.focus_app("vscode")
            steps.append({"step": "focus_vscode", "result": focus_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "target": file_path, "steps": steps}
            self._remember_wrapper("vscode", last_recipe=canonical, last_path=file_path, last_target=file_path, last_result_ok=result.get("ok"))
            return result

        if canonical == "vscode.readme":
            summary = self._project_summary(self._preferred_project_target(target))
            if not summary.get("ok"):
                return summary
            readme = summary.get("readme")
            if not readme:
                return {"ok": False, "error": "No README-like file found in that workspace path.", "summary": summary}

            doctor = self.wrapper_doctor("vscode")
            doctor_item = doctor.get("item") or {}
            if doctor_item and not doctor_item.get("ready"):
                fallback = self._readme_fallback(readme, summary, "VS Code launcher is not ready, so JARVIS showed the README preview instead.")
                self._remember_wrapper("vscode", last_recipe=canonical, last_path=readme, last_target=readme, last_result_ok=fallback.get("ok"))
                return fallback

            open_result = self.open_app("vscode", target=readme)
            steps.append({"step": "open_readme_in_vscode", "result": open_result})
            focus_result = self.focus_app("vscode")
            steps.append({"step": "focus_vscode", "result": focus_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "readme": readme, "summary": summary, "steps": steps}
            if not result.get("ok"):
                fallback = self._readme_fallback(readme, summary, "VS Code could not be opened here, so JARVIS returned the README preview instead.")
                self._remember_wrapper("vscode", last_recipe=canonical, last_path=readme, last_target=readme, last_result_ok=fallback.get("ok"))
                return fallback
            self._remember_wrapper("vscode", last_recipe=canonical, last_path=readme, last_target=readme, last_result_ok=result.get("ok"))
            return result

        if canonical == "vscode.resume":
            vscode_state = wrapper_state_service.get_state("vscode")
            remembered_target = payload or vscode_state.get("last_path") or vscode_state.get("last_target")
            doctor = self.wrapper_doctor("vscode")
            doctor_item = doctor.get("item") or {}
            if remembered_target:
                remembered_path = Path(remembered_target)
                if remembered_path.is_file():
                    if doctor_item and not doctor_item.get("ready"):
                        fallback = self._readme_fallback(str(remembered_path), {"path": str(remembered_path.parent), "readme": str(remembered_path), "readme_preview": self._read_text_preview(remembered_path)}, "VS Code launcher is not ready, so JARVIS showed the remembered file preview instead.")
                        self._remember_wrapper("vscode", last_recipe=canonical, last_path=remembered_target, last_target=remembered_target, last_result_ok=fallback.get("ok"))
                        return fallback
                    open_result = self.open_app("vscode", target=remembered_target)
                    steps.append({"step": "open_remembered_file", "result": open_result})
                    focus_result = self.focus_app("vscode")
                    steps.append({"step": "focus_vscode", "result": focus_result})
                    result = {"ok": self._steps_ok(steps), "recipe": canonical, "target": remembered_target, "steps": steps}
                    self._remember_wrapper("vscode", last_recipe=canonical, last_path=remembered_target, last_target=remembered_target, last_result_ok=result.get("ok"))
                    return result
                project_result = self.run_recipe("vscode.project", target=remembered_target)
                return {"ok": project_result.get("ok", False), "recipe": canonical, "target": remembered_target, "result": project_result}
            readme_result = self.run_recipe("vscode.readme", target=target)
            return {"ok": readme_result.get("ok", False), "recipe": canonical, "result": readme_result}

        if canonical == "terminal.project":
            path = self._preferred_project_target(target)
            ensure_result = self.ensure_app("terminal", target=path)
            steps.append({"step": "ensure_terminal_project", "result": ensure_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "target": path, "steps": steps}
            self._remember_wrapper("terminal", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            return result

        if canonical == "terminal.command":
            path_target, command = self._parse_command_payload(payload)
            terminal_state = wrapper_state_service.get_state("terminal")
            if not path_target:
                path_target = terminal_state.get("last_path") or terminal_state.get("last_target")
            if not command:
                command = terminal_state.get("last_command")
            if not command:
                return {"ok": False, "error": "This recipe needs a command. Use app recipe: terminal.command ::: your command or path || your command"}
            ensure_result = self.ensure_app("terminal", target=path_target)
            steps.append({"step": "ensure_terminal", "result": ensure_result})
            type_result = desktop_tool.type_text(command)
            steps.append({"step": "type_command", "result": type_result})
            enter_result = desktop_tool.press_key("enter")
            steps.append({"step": "submit_command", "result": enter_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "command": command, "path": path_target, "steps": steps}
            self._remember_wrapper("terminal", last_recipe=canonical, last_command=command, last_path=path_target, last_target=path_target, last_result_ok=result.get("ok"))
            return result

        if canonical == "browser.search":
            browser_state = wrapper_state_service.get_state("browser")
            query = payload or browser_state.get("last_query")
            if not query:
                return {"ok": False, "error": "This recipe needs a query. Use app recipe: browser.search ::: your query"}
            url = f"https://duckduckgo.com/?q={quote_plus(query)}"
            open_result = self.ensure_app("browser", target=url, launch_mode="external")
            steps.append({"step": "open_search_results", "result": open_result})
            if open_result.get("fallback") == "browser_link":
                result = {
                    "ok": True,
                    "recipe": canonical,
                    "query": query,
                    "url": url,
                    "fallback": open_result.get("fallback"),
                    "plain_english": open_result.get("plain_english"),
                    "manual_steps": open_result.get("manual_steps"),
                    "next_action": open_result.get("next_action"),
                    "steps": steps,
                }
                self._remember_wrapper("browser", last_recipe=canonical, last_query=query, last_url=url, last_target=url, last_launch_mode="external", last_result_ok=True)
                return result
            if open_result.get("mode") == "external":
                result = {
                    "ok": self._steps_ok(steps),
                    "recipe": canonical,
                    "query": query,
                    "url": url,
                    "mode": "external",
                    "browser_name": open_result.get("browser_name"),
                    "plain_english": open_result.get("plain_english") or "JARVIS opened the search in your real browser.",
                    "next_action": "If you want JARVIS to read the results too, say: research " + query,
                    "steps": steps,
                }
                self._remember_wrapper("browser", last_recipe=canonical, last_query=query, last_url=url, last_target=url, last_launch_mode="external", last_result_ok=result.get("ok"))
                return result
            title_result = browser_tool.title()
            steps.append({"step": "read_browser_title", "result": title_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "query": query, "url": url, "mode": "playwright_managed", "steps": steps}
            self._remember_wrapper("browser", last_recipe=canonical, last_query=query, last_url=url, last_target=url, last_launch_mode="playwright_managed", last_result_ok=result.get("ok"))
            return result

        if canonical == "browser.site_search":
            browser_context = self.current_browser_context()
            base_url = browser_context.get("url") or browser_context.get("remembered_url")
            domain = self._domain_from_url(base_url)
            query = payload or wrapper_state_service.get_state("browser").get("last_query")
            if not domain:
                return {
                    "ok": False,
                    "error": "JARVIS does not know which site to search yet. Open or resume a browser page first.",
                    "next_action": "Try: show me the current page or open browser to a URL first.",
                }
            if not query:
                return {
                    "ok": False,
                    "error": "This recipe needs a query. Use app recipe: browser.site_search ::: your query",
                    "next_action": f"Try: search this site for something on {domain}",
                }
            scoped_query = f"site:{domain} {query}"
            result = self.run_recipe("browser.search", text=scoped_query)
            result["site"] = domain
            result["original_query"] = query
            result["recipe"] = canonical
            return result

        if canonical == "browser.research":
            browser_state = wrapper_state_service.get_state("browser")
            query = payload or browser_state.get("last_query")
            if not query:
                current = browser_tool.state()
                if current.get("ok") and current.get("started"):
                    steps.append({"step": "use_existing_browser_page", "result": current})
                    title_result = browser_tool.title()
                    steps.append({"step": "read_browser_title", "result": title_result})
                    text_result = browser_tool.text_snapshot(max_chars=3000)
                    steps.append({"step": "snapshot_current_page_text", "result": text_result})
                    screenshot_result = browser_tool.screenshot(None)
                    steps.append({"step": "capture_current_page_screenshot", "result": screenshot_result})
                    result = {"ok": self._steps_ok(steps), "recipe": canonical, "query": None, "url": current.get("url"), "steps": steps}
                    self._remember_wrapper("browser", last_recipe=canonical, last_url=current.get("url"), last_result_ok=result.get("ok"))
                    return result
                return {"ok": False, "error": "This recipe needs a query or an already-open browser page."}
            url = f"https://duckduckgo.com/?q={quote_plus(query)}"
            open_result = self.ensure_app("browser", target=url, launch_mode="playwright_managed")
            steps.append({"step": "open_search_results", "result": open_result})
            if open_result.get("fallback") == "browser_link":
                result = {
                    "ok": True,
                    "recipe": canonical,
                    "query": query,
                    "url": url,
                    "fallback": open_result.get("fallback"),
                    "plain_english": open_result.get("plain_english"),
                    "manual_steps": open_result.get("manual_steps"),
                    "next_action": open_result.get("next_action"),
                    "steps": steps,
                }
                self._remember_wrapper("browser", last_recipe=canonical, last_query=query, last_url=url, last_target=url, last_result_ok=True)
                return result
            title_result = browser_tool.title()
            steps.append({"step": "read_browser_title", "result": title_result})
            text_result = browser_tool.text_snapshot(max_chars=3000)
            steps.append({"step": "snapshot_results_text", "result": text_result})
            screenshot_result = browser_tool.screenshot(None)
            steps.append({"step": "capture_results_screenshot", "result": screenshot_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "query": query, "url": url, "steps": steps}
            self._remember_wrapper("browser", last_recipe=canonical, last_query=query, last_url=url, last_target=url, last_result_ok=result.get("ok"))
            return result

        if canonical == "browser.snapshot":
            browser_state = wrapper_state_service.get_state("browser")
            url = payload or browser_state.get("last_url") or browser_state.get("last_target")
            if not url:
                current = browser_tool.state()
                if current.get("ok") and current.get("started") and current.get("url"):
                    url = current.get("url")
                else:
                    return {"ok": False, "error": "This recipe needs a URL. Use app recipe: browser.snapshot ::: https://example.com"}
            open_result = self.ensure_app("browser", target=url, launch_mode="playwright_managed")
            steps.append({"step": "open_url", "result": open_result})
            if open_result.get("fallback") == "browser_link":
                result = {
                    "ok": True,
                    "recipe": canonical,
                    "url": url,
                    "fallback": open_result.get("fallback"),
                    "plain_english": open_result.get("plain_english"),
                    "manual_steps": open_result.get("manual_steps"),
                    "next_action": open_result.get("next_action"),
                    "steps": steps,
                }
                self._remember_wrapper("browser", last_recipe=canonical, last_url=url, last_target=url, last_result_ok=True)
                return result
            title_result = browser_tool.title()
            steps.append({"step": "read_browser_title", "result": title_result})
            text_result = browser_tool.text_snapshot(max_chars=2500)
            steps.append({"step": "snapshot_page_text", "result": text_result})
            screenshot_result = browser_tool.screenshot(None)
            steps.append({"step": "capture_page_screenshot", "result": screenshot_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "url": url, "steps": steps}
            self._remember_wrapper("browser", last_recipe=canonical, last_url=url, last_target=url, last_result_ok=result.get("ok"))
            return result

        if canonical == "browser.resume":
            browser_state = wrapper_state_service.get_state("browser")
            remembered_url = payload or browser_state.get("last_url") or browser_state.get("last_target")
            if remembered_url:
                snapshot_result = self.run_recipe("browser.snapshot", target=remembered_url)
                return {"ok": snapshot_result.get("ok", False), "recipe": canonical, "target": remembered_url, "result": snapshot_result}
            current = browser_tool.state()
            if current.get("ok") and current.get("started"):
                resume_result = self.run_recipe("browser.snapshot", target=current.get("url"))
                return {"ok": resume_result.get("ok", False), "recipe": canonical, "target": current.get("url"), "result": resume_result}
            return {
                "ok": True,
                "fallback": "browser_link",
                "reason": "There is no remembered browser page yet, so JARVIS cannot resume one automatically.",
                "plain_english": "No browser page has been remembered yet. Start with a search or open a page first.",
                "manual_steps": [
                    "Say: open browser to https://example.com",
                    "Or say: search for local ai agents",
                ],
                "next_action": "Try: search for something or open a page first.",
            }

        if canonical == "project.inspect":
            summary = self._project_summary(self._preferred_project_target(target))
            if not summary.get("ok"):
                return summary
            path = summary.get("path")
            self._remember_wrapper("explorer", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=True)
            self._remember_wrapper("vscode", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=True)
            self._remember_wrapper("terminal", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=True)
            return {"ok": True, "recipe": canonical, "summary": summary}

        if canonical == "project.review":
            path = self._preferred_project_target(target)
            inspect_result = self.run_recipe("project.inspect", target=path)
            steps.append({"step": "inspect_project", "result": inspect_result})
            readme_result = self.run_recipe("vscode.readme", target=path)
            steps.append({"step": "review_readme", "result": readme_result})
            return {"ok": self._steps_ok(steps), "recipe": canonical, "target": path, "steps": steps}

        if canonical == "coding.start":
            path = self._preferred_project_target(target)
            code_doctor = self.wrapper_doctor("vscode")
            terminal_doctor = self.wrapper_doctor("terminal")
            code_ready = (code_doctor.get("item") or {}).get("ready", False)
            terminal_ready = (terminal_doctor.get("item") or {}).get("ready", False)

            if not code_ready and not terminal_ready:
                fallback = self._workspace_start_fallback(path, "VS Code and terminal launchers are not ready here, so JARVIS returned a manual project-start pack instead.")
                self._remember_wrapper("vscode", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=fallback.get("ok"))
                self._remember_wrapper("terminal", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=fallback.get("ok"))
                return fallback

            code_result = self.run_recipe("vscode.project", target=path) if code_ready else self._workspace_start_fallback(path, "VS Code is not ready here, so JARVIS returned a project-start pack instead.")
            steps.append({"step": "open_code_workspace", "result": code_result})
            terminal_result = self.run_recipe("terminal.project", target=path) if terminal_ready else self._directory_fallback(path, "The terminal launcher is not ready here, so JARVIS returned the project folder contents instead.")
            steps.append({"step": "open_project_terminal", "result": terminal_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "target": path, "steps": steps}
            self._remember_wrapper("vscode", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            self._remember_wrapper("terminal", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            return result

        if canonical == "coding.resume":
            path = self._preferred_project_target(target)
            vscode_resume = self.run_recipe("vscode.resume", target=path)
            steps.append({"step": "resume_code_workspace", "result": vscode_resume})
            terminal_resume = self.run_recipe("terminal.project", target=path)
            steps.append({"step": "resume_project_terminal", "result": terminal_resume})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "target": path, "steps": steps}
            self._remember_wrapper("vscode", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            self._remember_wrapper("terminal", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            return result

        if canonical == "project.files":
            path = self._preferred_project_target(target)
            result = self.open_path_in_explorer(path)
            return {"ok": result.get("ok", False), "recipe": canonical, "target": path, "result": result}

        if canonical == "browser.page_review":
            snapshot = self.run_recipe("browser.snapshot", target=payload or None)
            return {"ok": snapshot.get("ok", False), "recipe": canonical, "result": snapshot}

        if canonical == "project.starter":
            path = self._preferred_project_target(target)
            explorer_ready = (self.wrapper_doctor("explorer").get("item") or {}).get("ready", False)
            vscode_ready = (self.wrapper_doctor("vscode").get("item") or {}).get("ready", False)
            terminal_ready = (self.wrapper_doctor("terminal").get("item") or {}).get("ready", False)

            steps.append({"step": "ensure_explorer", "result": self.ensure_app("explorer", target=path) if explorer_ready else self._directory_fallback(path, "File Explorer is not ready here, so JARVIS returned the project folder contents instead.")})
            steps.append({"step": "ensure_vscode", "result": self.ensure_app("vscode", target=path) if vscode_ready else self._workspace_start_fallback(path, "VS Code is not ready here, so JARVIS returned a project-start pack instead.")})
            steps.append({"step": "ensure_terminal", "result": self.ensure_app("terminal", target=path) if terminal_ready else self._directory_fallback(path, "The terminal launcher is not ready here, so JARVIS returned the project folder contents instead.")})
            if vscode_ready:
                steps.append({"step": "focus_vscode", "result": self.focus_app("vscode")})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "target": path, "steps": steps}
            self._remember_wrapper("explorer", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            self._remember_wrapper("vscode", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            self._remember_wrapper("terminal", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            return result

        if canonical == "project.resume":
            remembered_path = self._preferred_project_target(target)
            inspect_result = self.run_recipe("project.inspect", target=remembered_path)
            steps.append({"step": "inspect_project", "result": inspect_result})
            starter_result = self.run_recipe("project.starter", target=remembered_path)
            steps.append({"step": "start_project_tools", "result": starter_result})
            return {"ok": self._steps_ok(steps), "recipe": canonical, "target": remembered_path, "steps": steps}

        return {"ok": False, "error": f"Recipe not implemented yet: {canonical}"}


app_wrapper_service = AppWrapperService()
