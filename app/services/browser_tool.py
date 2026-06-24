import os
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings


class BrowserTool:
    def __init__(self) -> None:
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._current_browser_name: str | None = None
        self._current_engine: str | None = None

    def _import_playwright(self):
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "Playwright is not installed. Run `pip install -r requirements-browser.txt` "
                "and `python -m playwright install chromium`."
            ) from e
        return sync_playwright

    def _artifact_path(self, raw_path: str | None = None) -> Path:
        base = settings.workspace_root.resolve()
        if raw_path:
            candidate = (base / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path).resolve()
        else:
            ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
            artifact_root = settings.browser_artifact_dir
            artifact_root = (base / artifact_root).resolve() if not artifact_root.is_absolute() else artifact_root.resolve()
            candidate = (artifact_root / f"browser-{ts}.png").resolve()

        try:
            candidate.relative_to(base)
        except ValueError as e:
            raise ValueError(f"Artifact path escapes workspace root: {candidate}") from e

        candidate.parent.mkdir(parents=True, exist_ok=True)
        return candidate

    def _windows(self) -> bool:
        return os.name == "nt"

    def _display_name(self, name: str) -> str:
        mapping = {
            "chrome": "Google Chrome",
            "msedge": "Microsoft Edge",
            "brave": "Brave",
            "firefox": "Firefox",
            "chromium": "Chromium",
            "playwright_chromium": "Playwright Chromium",
        }
        return mapping.get(name, name)

    def _normalize_browser_name(self, raw: str | None) -> str | None:
        name = (raw or "").strip().lower()
        aliases = {
            "": None,
            "auto": None,
            "default": None,
            "system": None,
            "edge": "msedge",
            "playwright": "playwright_chromium",
            "bundle": "playwright_chromium",
        }
        return aliases.get(name, name)

    def _preference_list(self) -> list[str]:
        items: list[str] = []
        seen: set[str] = set()
        for raw in settings.browser_channel_preference.split(","):
            normalized = self._normalize_browser_name(raw)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            items.append(normalized)
        return items

    def _candidate_from_path(self, name: str, engine: str, raw_path: str) -> dict[str, Any] | None:
        path = Path(raw_path)
        if path.exists() and path.is_file():
            return {
                "name": name,
                "engine": engine,
                "executable_path": str(path),
                "source": "system",
            }
        return None

    def _which_candidate(self, name: str, engine: str, executable_names: list[str]) -> dict[str, Any] | None:
        for executable in executable_names:
            found = shutil.which(executable)
            if found:
                return {
                    "name": name,
                    "engine": engine,
                    "executable_path": found,
                    "source": "path",
                }
        return None

    def _detect_candidates(self) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []

        def add(candidate: dict[str, Any] | None) -> None:
            if not candidate:
                return
            if any(existing["name"] == candidate["name"] for existing in candidates):
                return
            candidates.append(candidate)

        if self._windows():
            local = os.environ.get("LOCALAPPDATA", "")
            program_files = os.environ.get("PROGRAMFILES", "")
            program_files_x86 = os.environ.get("PROGRAMFILES(X86)", "")

            add(self._candidate_from_path("chrome", "chromium", os.path.join(local, "Google", "Chrome", "Application", "chrome.exe")))
            add(self._candidate_from_path("chrome", "chromium", os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe")))
            add(self._candidate_from_path("chrome", "chromium", os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe")))

            add(self._candidate_from_path("msedge", "chromium", os.path.join(program_files, "Microsoft", "Edge", "Application", "msedge.exe")))
            add(self._candidate_from_path("msedge", "chromium", os.path.join(program_files_x86, "Microsoft", "Edge", "Application", "msedge.exe")))

            add(self._candidate_from_path("brave", "chromium", os.path.join(local, "BraveSoftware", "Brave-Browser", "Application", "brave.exe")))
            add(self._candidate_from_path("brave", "chromium", os.path.join(program_files, "BraveSoftware", "Brave-Browser", "Application", "brave.exe")))
            add(self._candidate_from_path("brave", "chromium", os.path.join(program_files_x86, "BraveSoftware", "Brave-Browser", "Application", "brave.exe")))

            add(self._candidate_from_path("firefox", "firefox", os.path.join(program_files, "Mozilla Firefox", "firefox.exe")))
            add(self._candidate_from_path("firefox", "firefox", os.path.join(program_files_x86, "Mozilla Firefox", "firefox.exe")))
        else:
            add(self._which_candidate("chrome", "chromium", ["google-chrome", "google-chrome-stable", "chrome"]))
            add(self._which_candidate("msedge", "chromium", ["microsoft-edge", "microsoft-edge-stable", "msedge"]))
            add(self._which_candidate("brave", "chromium", ["brave-browser", "brave"]))
            add(self._which_candidate("firefox", "firefox", ["firefox"]))
            add(self._which_candidate("chromium", "chromium", ["chromium", "chromium-browser"]))

        candidates.append(
            {
                "name": "playwright_chromium",
                "engine": "chromium",
                "executable_path": None,
                "source": "playwright_bundle",
            }
        )
        return candidates

    def available_browsers(self) -> dict[str, Any]:
        detected = self._detect_candidates()
        preference = self._preference_list()
        ordered = self._ordered_candidates()
        default_candidate = ordered[0] if ordered else None
        items = []
        for candidate in detected:
            name = candidate["name"]
            item = {
                **candidate,
                "display_name": self._display_name(name),
                "available": bool(candidate.get("executable_path")) or name == "playwright_chromium",
                "is_fallback": name == "playwright_chromium",
                "preference_rank": (preference.index(name) + 1) if name in preference else None,
                "selected_by_default": bool(default_candidate and default_candidate.get("name") == name),
            }
            items.append(item)
        return {
            "ok": True,
            "preference": preference,
            "items": items,
            "count": len(items),
            "default_candidate": default_candidate,
        }

    def _ordered_candidates(self, preferred_browser: str | None = None) -> list[dict[str, Any]]:
        detected = self._detect_candidates()
        by_name = {item["name"]: item for item in detected}
        ordered: list[dict[str, Any]] = []
        seen: set[str] = set()

        requested_names: list[str] = []
        preferred = self._normalize_browser_name(preferred_browser)
        if preferred:
            requested_names.append(preferred)

        requested_names.extend(self._preference_list())

        for name in requested_names:
            candidate = by_name.get(name)
            if candidate and name not in seen:
                ordered.append(candidate)
                seen.add(name)

        for candidate in detected:
            if candidate["name"] not in seen:
                ordered.append(candidate)
                seen.add(candidate["name"])
        return ordered

    def _engine_launcher(self, engine_name: str):
        assert self._playwright is not None
        if engine_name == "firefox":
            return self._playwright.firefox
        return self._playwright.chromium

    def _reset_runtime(self) -> None:
        self._browser = None
        self._context = None
        self._page = None
        self._current_browser_name = None
        self._current_engine = None

    def _close_browser_runtime(self, stop_playwright: bool = False) -> None:
        try:
            if self._context is not None:
                self._context.close()
        except Exception:
            pass
        try:
            if self._browser is not None:
                self._browser.close()
        except Exception:
            pass
        finally:
            self._browser = None
            self._context = None
            self._page = None
            self._current_browser_name = None
            self._current_engine = None

        if stop_playwright:
            try:
                if self._playwright is not None:
                    self._playwright.stop()
            except Exception:
                pass
            finally:
                self._playwright = None

    def start(self, headless: bool | None = None, browser_name: str | None = None) -> dict[str, Any]:
        if not settings.allow_browser_tool:
            return {"ok": False, "error": "Browser tool is disabled in config."}

        effective_headless = settings.browser_headless if headless is None else headless
        requested_browser = self._normalize_browser_name(browser_name)

        if self._browser and self._page:
            if requested_browser and requested_browser != self._current_browser_name:
                self.close()
            else:
                return {
                    "ok": True,
                    "message": "Browser already running.",
                    "headless": effective_headless,
                    "url": self._page.url,
                    "title": self._page.title() if self._page else None,
                    "browser_name": self._current_browser_name,
                    "selected_browser": self._current_browser_name,
                    "requested_browser": requested_browser,
                    "engine": self._current_engine,
                    "attempted_candidates": [self._current_browser_name] if self._current_browser_name else [],
                }

        errors: list[dict[str, Any]] = []
        ordered_candidates = self._ordered_candidates(preferred_browser=requested_browser)
        attempted_candidates: list[str] = []
        try:
            sync_playwright = self._import_playwright()
            self._playwright = sync_playwright().start()

            for position, candidate in enumerate(ordered_candidates, start=1):
                attempted_candidates.append(candidate["name"])
                self._close_browser_runtime(stop_playwright=False)
                try:
                    launcher = self._engine_launcher(candidate["engine"])
                    launch_kwargs: dict[str, Any] = {"headless": effective_headless}
                    if candidate.get("executable_path"):
                        launch_kwargs["executable_path"] = candidate["executable_path"]
                    self._browser = launcher.launch(**launch_kwargs)
                    self._context = self._browser.new_context()
                    self._page = self._context.new_page()
                    self._page.set_default_timeout(settings.browser_default_timeout_ms)
                    self._current_browser_name = candidate["name"]
                    self._current_engine = candidate["engine"]
                    return {
                        "ok": True,
                        "message": "Browser started.",
                        "headless": effective_headless,
                        "browser_name": self._current_browser_name,
                        "selected_browser": self._current_browser_name,
                        "requested_browser": requested_browser,
                        "engine": self._current_engine,
                        "source": candidate.get("source"),
                        "attempted_candidates": attempted_candidates,
                        "selected_candidate_rank": position,
                        "fallback_used": bool(requested_browser and requested_browser != self._current_browser_name),
                    }
                except Exception as e:
                    errors.append(
                        {
                            "candidate": candidate["name"],
                            "engine": candidate.get("engine"),
                            "source": candidate.get("source"),
                            "error": str(e),
                        }
                    )
                    self._close_browser_runtime(stop_playwright=False)

            self._close_browser_runtime(stop_playwright=True)
            return {
                "ok": False,
                "error": "No configured browser candidate could be launched.",
                "requested_browser": requested_browser,
                "attempted_candidates": attempted_candidates,
                "candidates": ordered_candidates,
                "errors": errors,
            }
        except Exception as e:
            self._close_browser_runtime(stop_playwright=True)
            return {
                "ok": False,
                "error": (
                    f"Failed to start Playwright browser runtime: {e}. "
                    "If Playwright is installed, run `python -m playwright install chromium`."
                ),
                "requested_browser": requested_browser,
                "attempted_candidates": attempted_candidates,
            }

    def _ensure_page(self) -> tuple[bool, dict[str, Any] | None]:
        if self._page is not None:
            return True, None
        result = self.start()
        return bool(result.get("ok")), result

    def _locator_diagnostics(self, selector: str) -> dict[str, Any]:
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}

        try:
            assert self._page is not None
            locator = self._page.locator(selector)
            count = locator.count()
            info: dict[str, Any] = {
                "ok": True,
                "selector": selector,
                "count": count,
                "url": self._page.url,
                "title": self._page.title(),
                "samples": [],
            }
            max_samples = min(count, 3)
            for i in range(max_samples):
                sample = locator.nth(i)
                item: dict[str, Any] = {
                    "index": i,
                    "visible": sample.is_visible(),
                    "enabled": sample.is_enabled(),
                }
                try:
                    item["text"] = sample.inner_text(timeout=1000)[:200]
                except Exception:
                    item["text"] = None
                try:
                    item["html"] = sample.evaluate("el => el.outerHTML.slice(0, 300)")
                except Exception:
                    item["html"] = None
                info["samples"].append(item)
            return info
        except Exception as e:
            return {"ok": False, "error": str(e), "selector": selector}

    def state(self) -> dict[str, Any]:
        if not self._page:
            return {
                "ok": True,
                "started": False,
                "url": None,
                "title": None,
                "browser_name": self._current_browser_name,
                "engine": self._current_engine,
            }
        try:
            return {
                "ok": True,
                "started": True,
                "url": self._page.url,
                "title": self._page.title(),
                "browser_name": self._current_browser_name,
                "engine": self._current_engine,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_url(self, url: str, headless: bool | None = None, browser_name: str | None = None) -> dict[str, Any]:
        if not url.strip():
            return {"ok": False, "error": "URL is required."}

        requested_browser = self._normalize_browser_name(browser_name)
        if requested_browser and self._page is not None and requested_browser != self._current_browser_name:
            self.close()

        if self._page is None:
            result = self.start(headless=headless, browser_name=requested_browser)
            if not result.get("ok"):
                return result

        try:
            assert self._page is not None
            self._page.goto(url, wait_until="domcontentloaded")
            return {
                "ok": True,
                "url": self._page.url,
                "title": self._page.title(),
                "browser_name": self._current_browser_name,
                "selected_browser": self._current_browser_name,
                "requested_browser": requested_browser,
                "engine": self._current_engine,
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "requested_browser": requested_browser,
                "browser_name": self._current_browser_name,
            }

    def back(self) -> dict[str, Any]:
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            self._page.go_back(wait_until="domcontentloaded")
            return {"ok": True, "url": self._page.url, "title": self._page.title(), "browser_name": self._current_browser_name, "engine": self._current_engine}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def forward(self) -> dict[str, Any]:
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            self._page.go_forward(wait_until="domcontentloaded")
            return {"ok": True, "url": self._page.url, "title": self._page.title(), "browser_name": self._current_browser_name, "engine": self._current_engine}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def title(self) -> dict[str, Any]:
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            return {"ok": True, "url": self._page.url, "title": self._page.title(), "browser_name": self._current_browser_name, "engine": self._current_engine}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def text_snapshot(self, max_chars: int = 4000) -> dict[str, Any]:
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            body = self._page.locator("body").inner_text()
            return {
                "ok": True,
                "url": self._page.url,
                "title": self._page.title(),
                "text": body[:max_chars],
                "truncated": len(body) > max_chars,
                "browser_name": self._current_browser_name,
                "engine": self._current_engine,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def inspect(self, selector: str) -> dict[str, Any]:
        if not selector.strip():
            return {"ok": False, "error": "Selector is required."}
        return self._locator_diagnostics(selector)

    def click(self, selector: str, force: bool = False) -> dict[str, Any]:
        if not selector.strip():
            return {"ok": False, "error": "Selector is required."}
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            locator = self._page.locator(selector).first
            try:
                locator.scroll_into_view_if_needed(timeout=3000)
            except Exception:
                pass
            locator.click(force=force)
            return {"ok": True, "action": "click", "selector": selector, "force": force, "url": self._page.url, "browser_name": self._current_browser_name, "engine": self._current_engine}
        except Exception as e:
            diagnostics = self._locator_diagnostics(selector)
            return {
                "ok": False,
                "error": str(e),
                "selector": selector,
                "force": force,
                "diagnostics": diagnostics,
                "hint": "If the element exists but is hidden, try browser inspect or browser forceclick. For Google search, filling the search box and pressing Enter is usually more reliable.",
            }

    def fill(self, selector: str, text: str) -> dict[str, Any]:
        if not selector.strip():
            return {"ok": False, "error": "Selector is required."}
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            self._page.locator(selector).first.fill(text)
            return {"ok": True, "action": "fill", "selector": selector, "text_length": len(text), "url": self._page.url, "browser_name": self._current_browser_name, "engine": self._current_engine}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def press(self, selector: str, key: str = "Enter") -> dict[str, Any]:
        if not selector.strip():
            return {"ok": False, "error": "Selector is required."}
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            self._page.locator(selector).first.press(key)
            return {"ok": True, "action": "press", "selector": selector, "key": key, "url": self._page.url, "browser_name": self._current_browser_name, "engine": self._current_engine}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def screenshot(self, raw_path: str | None = None) -> dict[str, Any]:
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            path = self._artifact_path(raw_path)
            self._page.screenshot(path=str(path), full_page=True)
            return {"ok": True, "path": str(path), "url": self._page.url, "title": self._page.title(), "browser_name": self._current_browser_name, "engine": self._current_engine}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def close(self) -> dict[str, Any]:
        self._close_browser_runtime(stop_playwright=True)
        return {"ok": True, "message": "Browser closed."}


browser_tool = BrowserTool()
