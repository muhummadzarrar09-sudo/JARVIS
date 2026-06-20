from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from app.core.config import settings


class BrowserTool:
    def __init__(self) -> None:
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

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

    def start(self, headless: bool | None = None) -> dict[str, Any]:
        if not settings.allow_browser_tool:
            return {"ok": False, "error": "Browser tool is disabled in config."}

        effective_headless = settings.browser_headless if headless is None else headless

        if self._browser and self._page:
            return {
                "ok": True,
                "message": "Browser already running.",
                "headless": effective_headless,
                "url": self._page.url,
                "title": self._page.title() if self._page else None,
            }

        try:
            sync_playwright = self._import_playwright()
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=effective_headless)
            self._context = self._browser.new_context()
            self._page = self._context.new_page()
            self._page.set_default_timeout(settings.browser_default_timeout_ms)
            return {"ok": True, "message": "Browser started.", "headless": effective_headless}
        except Exception as e:
            return {
                "ok": False,
                "error": (
                    f"Failed to start Playwright Chromium: {e}. "
                    "If Playwright is installed, run `python -m playwright install chromium`."
                ),
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
            return {"ok": True, "started": False, "url": None, "title": None}
        try:
            return {
                "ok": True,
                "started": True,
                "url": self._page.url,
                "title": self._page.title(),
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_url(self, url: str, headless: bool | None = None) -> dict[str, Any]:
        if not url.strip():
            return {"ok": False, "error": "URL is required."}

        if self._page is None:
            result = self.start(headless=headless)
            if not result.get("ok"):
                return result

        try:
            assert self._page is not None
            self._page.goto(url, wait_until="domcontentloaded")
            return {"ok": True, "url": self._page.url, "title": self._page.title()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def back(self) -> dict[str, Any]:
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            self._page.go_back(wait_until="domcontentloaded")
            return {"ok": True, "url": self._page.url, "title": self._page.title()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def forward(self) -> dict[str, Any]:
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            self._page.go_forward(wait_until="domcontentloaded")
            return {"ok": True, "url": self._page.url, "title": self._page.title()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def title(self) -> dict[str, Any]:
        ok, result = self._ensure_page()
        if not ok:
            return result or {"ok": False, "error": "Browser unavailable."}
        try:
            assert self._page is not None
            return {"ok": True, "url": self._page.url, "title": self._page.title()}
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
            return {"ok": True, "action": "click", "selector": selector, "force": force, "url": self._page.url}
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
            return {"ok": True, "action": "fill", "selector": selector, "text_length": len(text), "url": self._page.url}
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
            return {"ok": True, "action": "press", "selector": selector, "key": key, "url": self._page.url}
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
            return {"ok": True, "path": str(path), "url": self._page.url, "title": self._page.title()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def close(self) -> dict[str, Any]:
        try:
            if self._context is not None:
                self._context.close()
            if self._browser is not None:
                self._browser.close()
            if self._playwright is not None:
                self._playwright.stop()
        except Exception as e:
            self._playwright = None
            self._browser = None
            self._context = None
            self._page = None
            return {"ok": False, "error": str(e)}

        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        return {"ok": True, "message": "Browser closed."}


browser_tool = BrowserTool()
