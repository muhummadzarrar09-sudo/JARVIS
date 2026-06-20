from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from app.core.config import settings
from app.services.browser_tool import browser_tool
from app.services.desktop_tool import desktop_tool
from app.services.process_tool import process_tool
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
                "notes": "Automation-managed browser session wrapper via Playwright.",
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
                "notes": "Run a browser search using a direct DuckDuckGo results URL.",
            },
            "browser.research": {
                "aliases": ["research", "web.research"],
                "inputs": ["query"],
                "risk": "medium",
                "notes": "Search the web and pull back a visible text snapshot for quick review.",
            },
            "browser.snapshot": {
                "aliases": ["web.snapshot", "open.snapshot"],
                "inputs": ["url"],
                "risk": "medium",
                "notes": "Open a URL in the managed browser and snapshot visible page text.",
            },
            "project.inspect": {
                "aliases": ["workspace.inspect", "project.scan"],
                "inputs": ["path?"],
                "risk": "low",
                "notes": "Inspect a workspace path, detect common project files, and remember it for wrappers.",
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

    def _steps_ok(self, steps: list[dict[str, Any]]) -> bool:
        return all(step.get("result", {}).get("ok") for step in steps)

    def _match_title_hint(self, title_hint: str, window_title: str) -> bool:
        return title_hint.lower() in (window_title or "").lower()

    def _remember_wrapper(self, wrapper: str, **fields: Any) -> dict[str, Any]:
        return wrapper_state_service.update_state(wrapper, **fields)

    def _workspace_root(self) -> Path:
        return Path(settings.workspace_root).resolve()

    def _resolve_workspace_path(self, target: str | None = None) -> Path:
        base = self._workspace_root()
        raw = self._default_path(target)
        candidate = (base / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
        try:
            candidate.relative_to(base)
        except ValueError as e:
            raise ValueError(f"Path escapes workspace root: {raw}") from e
        return candidate

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

        items = []
        for canonical in wrappers:
            meta = self._wrappers[canonical]
            title_hint = meta["title_hint"]
            state = wrapper_state_service.get_state(canonical)
            matches = []
            active = False
            running = False
            extra: dict[str, Any] = {"remembered_state": state}

            if canonical == "browser":
                running = bool(browser_state.get("started"))
                if desktop_windows.get("ok"):
                    matches = [item for item in desktop_windows.get("items", []) if self._match_title_hint(title_hint, item.get("title", ""))]
                    running = running or bool(matches)
                    active = any(item.get("is_active") for item in matches)
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
                if self._match_title_hint(title_hint, active_title):
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

    def open_app(self, name: str, target: str | None = None) -> dict[str, Any]:
        canonical = self._normalize_name(name)
        if not canonical:
            return {"ok": False, "error": f"Unknown app wrapper: {name}"}

        if canonical == "browser":
            url = (target or "https://example.com").strip()
            result = browser_tool.open_url(url)
            self._remember_wrapper(canonical, last_action="open", last_target=url, last_url=url, last_result_ok=result.get("ok"))
            return {
                "ok": result.get("ok", False),
                "wrapper": canonical,
                "target": url,
                "mode": "playwright_managed",
                "result": result,
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

    def ensure_app(self, name: str, target: str | None = None, exact: bool = False) -> dict[str, Any]:
        canonical = self._normalize_name(name)
        if not canonical:
            return {"ok": False, "error": f"Unknown app wrapper: {name}"}

        state = wrapper_state_service.get_state(canonical)
        if (not target or not target.strip()) and self._target_capable(canonical):
            target = state.get("last_target") or state.get("last_path") or state.get("last_url")

        steps: list[dict[str, Any]] = []
        status_before = self.wrapper_status(canonical)
        steps.append({"step": "status_before", "result": status_before})
        item = status_before.get("item", {})

        if canonical == "browser":
            url = (target or "https://example.com").strip()
            open_result = self.open_url_in_browser(url)
            steps.append({"step": "open_or_navigate_browser", "result": open_result})
            result = {"ok": self._steps_ok(steps), "wrapper": canonical, "target": url, "workflow": "ensure", "steps": steps}
            self._remember_wrapper(canonical, last_action="ensure", last_result_ok=result.get("ok"), last_target=url, last_url=url)
            return result

        if target and self._target_capable(canonical):
            open_result = self.open_app(canonical, target=target)
            steps.append({"step": "open_targeted_instance", "result": open_result})
            focus_result = self.focus_app(canonical, exact=exact)
            steps.append({"step": "focus_after_open", "result": focus_result})
            result = {"ok": self._steps_ok(steps), "wrapper": canonical, "target": target, "workflow": "ensure", "steps": steps}
            self._remember_wrapper(canonical, last_action="ensure", last_result_ok=result.get("ok"), last_target=target)
            return result

        if item.get("running"):
            focus_result = self.focus_app(canonical, exact=exact)
            steps.append({"step": "focus_existing", "result": focus_result})
            result = {"ok": self._steps_ok(steps), "wrapper": canonical, "workflow": "ensure", "steps": steps}
            self._remember_wrapper(canonical, last_action="ensure", last_result_ok=result.get("ok"))
            return result

        open_result = self.open_app(canonical, target=target)
        steps.append({"step": "open_app", "result": open_result})
        focus_result = self.focus_app(canonical, exact=exact)
        steps.append({"step": "focus_after_open", "result": focus_result})
        result = {"ok": self._steps_ok(steps), "wrapper": canonical, "target": target, "workflow": "ensure", "steps": steps}
        self._remember_wrapper(canonical, last_action="ensure", last_result_ok=result.get("ok"), last_target=target)
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
        return self.open_app("explorer", target=path)

    def open_path_in_vscode(self, target: str) -> dict[str, Any]:
        path = target.strip()
        if not path:
            return {"ok": False, "error": "Path is required."}
        return self.open_app("vscode", target=path)

    def open_url_in_browser(self, url: str) -> dict[str, Any]:
        clean_url = url.strip()
        if not clean_url:
            return {"ok": False, "error": "URL is required."}
        return self.open_app("browser", target=clean_url)

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
            path = self._default_path(target)
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
            summary = self._project_summary(target)
            if not summary.get("ok"):
                return summary
            readme = summary.get("readme")
            if not readme:
                return {"ok": False, "error": "No README-like file found in that workspace path.", "summary": summary}
            open_result = self.open_app("vscode", target=readme)
            steps.append({"step": "open_readme_in_vscode", "result": open_result})
            focus_result = self.focus_app("vscode")
            steps.append({"step": "focus_vscode", "result": focus_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "readme": readme, "summary": summary, "steps": steps}
            self._remember_wrapper("vscode", last_recipe=canonical, last_path=readme, last_target=readme, last_result_ok=result.get("ok"))
            return result

        if canonical == "terminal.project":
            path = self._default_path(target)
            ensure_result = self.ensure_app("terminal", target=path)
            steps.append({"step": "ensure_terminal_project", "result": ensure_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "target": path, "steps": steps}
            self._remember_wrapper("terminal", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            return result

        if canonical == "terminal.command":
            path_target, command = self._parse_command_payload(payload)
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
            query = payload
            if not query:
                return {"ok": False, "error": "This recipe needs a query. Use app recipe: browser.search ::: your query"}
            url = f"https://duckduckgo.com/?q={quote_plus(query)}"
            open_result = self.ensure_app("browser", target=url)
            steps.append({"step": "open_search_results", "result": open_result})
            title_result = browser_tool.title()
            steps.append({"step": "read_browser_title", "result": title_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "query": query, "url": url, "steps": steps}
            self._remember_wrapper("browser", last_recipe=canonical, last_query=query, last_url=url, last_target=url, last_result_ok=result.get("ok"))
            return result

        if canonical == "browser.research":
            query = payload
            if not query:
                return {"ok": False, "error": "This recipe needs a query. Use app recipe: browser.research ::: your query"}
            url = f"https://duckduckgo.com/?q={quote_plus(query)}"
            open_result = self.ensure_app("browser", target=url)
            steps.append({"step": "open_search_results", "result": open_result})
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
            url = payload
            if not url:
                return {"ok": False, "error": "This recipe needs a URL. Use app recipe: browser.snapshot ::: https://example.com"}
            open_result = self.ensure_app("browser", target=url)
            steps.append({"step": "open_url", "result": open_result})
            title_result = browser_tool.title()
            steps.append({"step": "read_browser_title", "result": title_result})
            text_result = browser_tool.text_snapshot(max_chars=2500)
            steps.append({"step": "snapshot_page_text", "result": text_result})
            screenshot_result = browser_tool.screenshot(None)
            steps.append({"step": "capture_page_screenshot", "result": screenshot_result})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "url": url, "steps": steps}
            self._remember_wrapper("browser", last_recipe=canonical, last_url=url, last_target=url, last_result_ok=result.get("ok"))
            return result

        if canonical == "project.inspect":
            summary = self._project_summary(target)
            if not summary.get("ok"):
                return summary
            path = summary.get("path")
            self._remember_wrapper("explorer", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=True)
            self._remember_wrapper("vscode", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=True)
            self._remember_wrapper("terminal", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=True)
            return {"ok": True, "recipe": canonical, "summary": summary}

        if canonical == "project.starter":
            path = self._default_path(target)
            steps.append({"step": "ensure_explorer", "result": self.ensure_app("explorer", target=path)})
            steps.append({"step": "ensure_vscode", "result": self.ensure_app("vscode", target=path)})
            steps.append({"step": "ensure_terminal", "result": self.ensure_app("terminal", target=path)})
            steps.append({"step": "focus_vscode", "result": self.focus_app("vscode")})
            result = {"ok": self._steps_ok(steps), "recipe": canonical, "target": path, "steps": steps}
            self._remember_wrapper("explorer", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            self._remember_wrapper("vscode", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            self._remember_wrapper("terminal", last_recipe=canonical, last_path=path, last_target=path, last_result_ok=result.get("ok"))
            return result

        if canonical == "project.resume":
            remembered_path = target or wrapper_state_service.get_state("vscode").get("last_path") or wrapper_state_service.get_state("explorer").get("last_path") or wrapper_state_service.get_state("terminal").get("last_path") or "."
            result = self.run_recipe("project.starter", target=remembered_path)
            return {"ok": result.get("ok", False), "recipe": canonical, "target": remembered_path, "result": result}

        return {"ok": False, "error": f"Recipe not implemented yet: {canonical}"}


app_wrapper_service = AppWrapperService()
