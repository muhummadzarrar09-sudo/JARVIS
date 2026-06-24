import platform
import time
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from app.core.config import settings


class DesktopTool:
    def __init__(self) -> None:
        self._focus_history: list[dict[str, Any]] = []

    def _windows(self) -> bool:
        return platform.system().lower().startswith("win")

    def _guard(self, action: str) -> dict[str, Any]:
        profiles = {
            "list_windows": {"risk": "low", "reversible": True, "notes": "Read-only window enumeration."},
            "active_window": {"risk": "low", "reversible": True, "notes": "Read-only active window lookup."},
            "screen_info": {"risk": "low", "reversible": True, "notes": "Read-only screen information."},
            "find_windows": {"risk": "low", "reversible": True, "notes": "Read-only fuzzy window search."},
            "focus_window": {"risk": "medium", "reversible": True, "notes": "Changes active app focus."},
            "focus_handle": {"risk": "medium", "reversible": True, "notes": "Changes active app focus by exact window handle."},
            "undo_focus": {"risk": "low", "reversible": True, "notes": "Attempts to restore previous focus target."},
            "type_text": {"risk": "high", "reversible": False, "notes": "Sends text to the currently focused application."},
            "press_key": {"risk": "medium", "reversible": False, "notes": "Sends a single key to the currently focused application."},
            "hotkey": {"risk": "high", "reversible": False, "notes": "Sends a hotkey combo to the currently focused application."},
            "click": {"risk": "high", "reversible": False, "notes": "Clicks screen coordinates directly."},
            "screenshot": {"risk": "low", "reversible": True, "notes": "Captures desktop pixels only."},
            "preview": {"risk": "low", "reversible": True, "notes": "Dry-run preview of a desktop action."},
            "safety_status": {"risk": "low", "reversible": True, "notes": "Shows desktop guard/undo capability state."},
        }
        return {"action": action, **profiles.get(action, {"risk": "medium", "reversible": False, "notes": "No policy profile found."})}

    def _with_guard(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload["guard"] = self._guard(action)
        return payload

    def _import_pyautogui(self):
        try:
            import pyautogui  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "pyautogui is not installed. Run `pip install -r requirements-desktop.txt`."
            ) from e
        pyautogui.PAUSE = settings.desktop_action_pause_seconds
        pyautogui.FAILSAFE = True
        return pyautogui

    def _import_pygetwindow(self):
        try:
            import pygetwindow as gw  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "pygetwindow is not installed. Run `pip install -r requirements-desktop.txt`."
            ) from e
        return gw

    def _import_imagegrab(self):
        try:
            from PIL import ImageGrab  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "Pillow is not installed. Run `pip install -r requirements-desktop.txt`."
            ) from e
        return ImageGrab

    def _artifact_path(self, raw_path: str | None = None) -> Path:
        base = settings.workspace_root.resolve()
        if raw_path:
            candidate = (base / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path).resolve()
        else:
            ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
            artifact_root = settings.desktop_artifact_dir
            artifact_root = (base / artifact_root).resolve() if not artifact_root.is_absolute() else artifact_root.resolve()
            candidate = (artifact_root / f"desktop-{ts}.png").resolve()

        try:
            candidate.relative_to(base)
        except ValueError as e:
            raise ValueError(f"Artifact path escapes workspace root: {candidate}") from e

        candidate.parent.mkdir(parents=True, exist_ok=True)
        return candidate

    def _window_handle(self, win) -> int | None:
        handle = getattr(win, "_hWnd", None)
        try:
            return int(handle) if handle is not None else None
        except Exception:
            return None

    def _window_to_dict(self, win) -> dict[str, Any]:
        return {
            "title": (getattr(win, "title", "") or "").strip(),
            "handle": self._window_handle(win),
            "left": getattr(win, "left", None),
            "top": getattr(win, "top", None),
            "width": getattr(win, "width", None),
            "height": getattr(win, "height", None),
            "is_active": getattr(win, "isActive", False),
            "is_minimized": getattr(win, "isMinimized", False),
            "is_maximized": getattr(win, "isMaximized", False),
        }

    def _all_titled_windows(self):
        gw = self._import_pygetwindow()
        items = []
        for win in gw.getAllWindows():
            title = (win.title or "").strip()
            if not title:
                continue
            items.append(win)
        return items

    def _normalize_title(self, text: str) -> str:
        return " ".join("".join(ch.lower() if ch.isalnum() else " " for ch in (text or "")).split())

    def _score_window_match(self, needle: str, current_title: str, exact: bool = False) -> float:
        title_l = self._normalize_title(current_title)
        needle_l = self._normalize_title(needle)
        if not needle_l:
            return 0.0
        if exact:
            return 100.0 if title_l == needle_l else 0.0
        if title_l == needle_l:
            return 100.0
        if title_l.startswith(needle_l):
            return 85.0
        if needle_l in title_l:
            return 65.0
        words = needle_l.split()
        if words and all(word in title_l for word in words):
            return 55.0
        return 0.0

    def _titles_equivalent(self, expected: str, actual: str) -> bool:
        expected_n = self._normalize_title(expected)
        actual_n = self._normalize_title(actual)
        if not expected_n or not actual_n:
            return False
        if expected_n == actual_n:
            return True
        if len(expected_n) >= 8 and expected_n in actual_n:
            return True
        if len(actual_n) >= 8 and actual_n in expected_n:
            return True
        return self._score_window_match(expected_n, actual_n, exact=False) >= 65.0 and self._score_window_match(actual_n, expected_n, exact=False) >= 65.0

    def _match_windows(self, title: str, exact: bool = False):
        scored = []
        for win in self._all_titled_windows():
            current_title = (win.title or "").strip()
            score = self._score_window_match(title, current_title, exact=exact)
            if score > 0:
                priority = score
                if getattr(win, "isActive", False):
                    priority += 6.0
                if not getattr(win, "isMinimized", False):
                    priority += 2.0
                scored.append((priority, score, win))
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [win for _, _, win in scored]

    def _verify_focus(self, selected_window: dict[str, Any], attempts: int = 5, pause_seconds: float = 0.15) -> dict[str, Any]:
        checks = []
        selected_handle = selected_window.get("handle")
        selected_title = selected_window.get("title") or ""

        for attempt in range(1, attempts + 1):
            active = self.active_window()
            active_window = active.get("window") if active.get("ok") else None
            verified_by = None

            if active_window:
                active_handle = active_window.get("handle")
                active_title = active_window.get("title") or ""
                if selected_handle is not None and active_handle == selected_handle:
                    verified_by = "handle"
                elif self._titles_equivalent(selected_title, active_title):
                    verified_by = "title"

            checks.append({
                "attempt": attempt,
                "active_window": active_window,
                "verified_by": verified_by,
            })

            if verified_by:
                return {
                    "ok": True,
                    "verified_by": verified_by,
                    "attempt_count": attempt,
                    "checks": checks,
                    "final_active_window": active_window,
                }

            if attempt < attempts:
                time.sleep(pause_seconds)

        return {
            "ok": False,
            "verified_by": None,
            "attempt_count": attempts,
            "checks": checks,
            "final_active_window": checks[-1].get("active_window") if checks else None,
        }

    def _find_window_by_handle(self, handle: int):
        for win in self._all_titled_windows():
            if self._window_handle(win) == handle:
                return win
        return None

    def _record_focus_history(self, previous_window: dict[str, Any] | None, next_window: dict[str, Any] | None) -> None:
        self._focus_history.append(
            {
                "ts": datetime.now(UTC).isoformat(),
                "previous_window": previous_window,
                "next_window": next_window,
            }
        )
        self._focus_history = self._focus_history[-20:]

    def screen_info(self) -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("screen_info", {"ok": False, "error": "Desktop tool is disabled in config."})
        try:
            pyautogui = self._import_pyautogui()
            size = pyautogui.size()
            position = pyautogui.position()
            return self._with_guard(
                "screen_info",
                {
                    "ok": True,
                    "width": size.width,
                    "height": size.height,
                    "mouse_x": position.x,
                    "mouse_y": position.y,
                    "failsafe": bool(getattr(pyautogui, "FAILSAFE", True)),
                },
            )
        except Exception as e:
            return self._with_guard("screen_info", {"ok": False, "error": str(e)})

    def active_window(self) -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("active_window", {"ok": False, "error": "Desktop tool is disabled in config."})
        if not self._windows():
            return self._with_guard("active_window", {"ok": False, "error": "Desktop active window lookup currently targets Windows first."})
        try:
            gw = self._import_pygetwindow()
            win = gw.getActiveWindow()
            if not win:
                return self._with_guard("active_window", {"ok": True, "active": False, "window": None})
            return self._with_guard("active_window", {"ok": True, "active": True, "window": self._window_to_dict(win)})
        except Exception as e:
            return self._with_guard("active_window", {"ok": False, "error": str(e)})

    def list_windows(self) -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("list_windows", {"ok": False, "error": "Desktop tool is disabled in config."})
        if not self._windows():
            return self._with_guard("list_windows", {"ok": False, "error": "Desktop window control currently targets Windows first."})

        try:
            windows = [self._window_to_dict(win) for win in self._all_titled_windows()]
            active = self.active_window()
            return self._with_guard(
                "list_windows",
                {
                    "ok": True,
                    "count": len(windows),
                    "items": windows[:200],
                    "active_window": active.get("window") if active.get("ok") else None,
                },
            )
        except Exception as e:
            return self._with_guard("list_windows", {"ok": False, "error": str(e)})

    def find_windows(self, title: str, exact: bool = False) -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("find_windows", {"ok": False, "error": "Desktop tool is disabled in config."})
        if not self._windows():
            return self._with_guard("find_windows", {"ok": False, "error": "Desktop find currently targets Windows first."})
        if not title.strip():
            return self._with_guard("find_windows", {"ok": False, "error": "Window title is required."})

        try:
            items = []
            for win in self._all_titled_windows():
                current_title = (win.title or "").strip()
                score = self._score_window_match(title, current_title, exact=exact)
                if score > 0:
                    payload = self._window_to_dict(win)
                    payload["score"] = score
                    items.append(payload)
            items.sort(key=lambda item: item.get("score", 0), reverse=True)
            return self._with_guard(
                "find_windows",
                {
                    "ok": True,
                    "requested_title": title,
                    "exact": exact,
                    "count": len(items),
                    "items": items[:20],
                },
            )
        except Exception as e:
            return self._with_guard("find_windows", {"ok": False, "error": str(e), "exact": exact})

    def focus_window(self, title: str, exact: bool = False, match_index: int = 0) -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("focus_window", {"ok": False, "error": "Desktop tool is disabled in config."})
        if not self._windows():
            return self._with_guard("focus_window", {"ok": False, "error": "Desktop focus currently targets Windows first."})
        if not title.strip():
            return self._with_guard("focus_window", {"ok": False, "error": "Window title is required."})

        try:
            matches = self._match_windows(title, exact=exact)
            if not matches:
                available_titles = [self._window_to_dict(win)["title"] for win in self._all_titled_windows()[:20]]
                return self._with_guard(
                    "focus_window",
                    {
                        "ok": False,
                        "error": f"No window matched title: {title}",
                        "available_title_samples": available_titles,
                        "exact": exact,
                    },
                )

            if match_index < 0 or match_index >= len(matches):
                return self._with_guard(
                    "focus_window",
                    {
                        "ok": False,
                        "error": f"match_index {match_index} is out of range for {len(matches)} match(es).",
                        "candidate_titles": [self._window_to_dict(m)["title"] for m in matches[:10]],
                        "exact": exact,
                    },
                )

            previous = self.active_window().get("window")
            win = matches[match_index]
            restore_attempted = False
            activation_attempts = []

            try:
                if getattr(win, "isMinimized", False):
                    win.restore()
                    restore_attempted = True
            except Exception as e:
                activation_attempts.append(f"restore_failed: {e}")

            try:
                win.activate()
                activation_attempts.append("activate")
            except Exception as e:
                activation_attempts.append(f"activate_failed: {e}")
                try:
                    win.minimize()
                    win.restore()
                    win.activate()
                    activation_attempts.append("minimize_restore_activate")
                except Exception as e2:
                    activation_attempts.append(f"fallback_failed: {e2}")

            selected = self._window_to_dict(win)
            verification = self._verify_focus(selected)
            success = verification.get("ok", False)
            active_after = verification.get("final_active_window")

            if success:
                self._record_focus_history(previous_window=previous, next_window=selected)

            return self._with_guard(
                "focus_window",
                {
                    "ok": success,
                    "requested_title": title,
                    "selected_window": selected,
                    "match_count": len(matches),
                    "match_index": match_index,
                    "candidate_titles": [self._window_to_dict(m)["title"] for m in matches[:6]],
                    "other_matches": [self._window_to_dict(m)["title"] for m in matches[1:6]],
                    "restore_attempted": restore_attempted,
                    "activation_attempts": activation_attempts,
                    "focus_verification": verification,
                    "active_window_after": active_after,
                    "exact": exact,
                    "error": None if success else "A matching window was found but focus could not be verified after multiple checks.",
                },
            )
        except Exception as e:
            return self._with_guard("focus_window", {"ok": False, "error": str(e), "exact": exact})

    def focus_handle(self, handle: int) -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("focus_handle", {"ok": False, "error": "Desktop tool is disabled in config."})
        if not self._windows():
            return self._with_guard("focus_handle", {"ok": False, "error": "Desktop focus currently targets Windows first."})
        try:
            previous = self.active_window().get("window")
            win = self._find_window_by_handle(handle)
            if not win:
                return self._with_guard("focus_handle", {"ok": False, "error": f"No window found for handle {handle}"})
            try:
                if getattr(win, "isMinimized", False):
                    win.restore()
            except Exception:
                pass
            win.activate()
            selected = self._window_to_dict(win)
            verification = self._verify_focus(selected)
            success = verification.get("ok", False)
            if success:
                self._record_focus_history(previous_window=previous, next_window=selected)
            return self._with_guard(
                "focus_handle",
                {
                    "ok": success,
                    "requested_handle": handle,
                    "selected_window": selected,
                    "focus_verification": verification,
                    "active_window_after": verification.get("final_active_window"),
                    "error": None if success else "Window handle was found but focus could not be verified after multiple checks.",
                },
            )
        except Exception as e:
            return self._with_guard("focus_handle", {"ok": False, "error": str(e)})

    def safety_status(self) -> dict[str, Any]:
        return self._with_guard(
            "safety_status",
            {
                "ok": True,
                "focus_history_entries": len(self._focus_history),
                "undo_focus_supported": True,
                "high_risk_actions": ["type_text", "hotkey", "click"],
                "guarded_actions": [
                    "focus_window",
                    "focus_handle",
                    "type_text",
                    "press_key",
                    "hotkey",
                    "click",
                    "screenshot",
                ],
            },
        )

    def preview_action(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        active = self.active_window()
        screen = self.screen_info()
        preview = {
            "ok": True,
            "requested_action": action,
            "payload": payload,
            "active_window": active.get("window") if active.get("ok") else None,
            "screen": {
                "width": screen.get("width"),
                "height": screen.get("height"),
                "mouse_x": screen.get("mouse_x"),
                "mouse_y": screen.get("mouse_y"),
            },
        }
        if action == "click":
            x = payload.get("x")
            y = payload.get("y")
            width = screen.get("width") or 0
            height = screen.get("height") or 0
            preview["inside_screen"] = isinstance(x, int) and isinstance(y, int) and 0 <= x < width and 0 <= y < height
        return self._with_guard("preview", preview)

    def undo_last_focus(self) -> dict[str, Any]:
        if not self._focus_history:
            return self._with_guard("undo_focus", {"ok": False, "error": "No focus history available to undo."})
        last = self._focus_history.pop()
        previous = last.get("previous_window") or {}
        handle = previous.get("handle")
        title = previous.get("title")
        if handle is not None:
            result = self.focus_handle(int(handle))
            result["undo_source"] = last
            return self._with_guard("undo_focus", result)
        if title:
            result = self.focus_window(title, exact=False)
            result["undo_source"] = last
            return self._with_guard("undo_focus", result)
        return self._with_guard("undo_focus", {"ok": False, "error": "Previous focus target had no recoverable handle or title."})

    def type_text(self, text: str) -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("type_text", {"ok": False, "error": "Desktop tool is disabled in config."})
        if not text:
            return self._with_guard("type_text", {"ok": False, "error": "Text is required."})
        try:
            active_before = self.active_window()
            pyautogui = self._import_pyautogui()
            pyautogui.write(text, interval=settings.desktop_key_interval_seconds)
            active_after = self.active_window()
            return self._with_guard(
                "type_text",
                {
                    "ok": True,
                    "action": "type",
                    "text_length": len(text),
                    "target_window_before": active_before.get("window"),
                    "target_window_after": active_after.get("window"),
                },
            )
        except Exception as e:
            return self._with_guard("type_text", {"ok": False, "error": str(e)})

    def press_key(self, key: str) -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("press_key", {"ok": False, "error": "Desktop tool is disabled in config."})
        if not key.strip():
            return self._with_guard("press_key", {"ok": False, "error": "Key is required."})
        try:
            active_before = self.active_window()
            pyautogui = self._import_pyautogui()
            pyautogui.press(key)
            active_after = self.active_window()
            return self._with_guard(
                "press_key",
                {
                    "ok": True,
                    "action": "press",
                    "key": key,
                    "target_window_before": active_before.get("window"),
                    "target_window_after": active_after.get("window"),
                },
            )
        except Exception as e:
            return self._with_guard("press_key", {"ok": False, "error": str(e)})

    def hotkey(self, keys: list[str]) -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("hotkey", {"ok": False, "error": "Desktop tool is disabled in config."})
        clean_keys = [k.strip() for k in keys if k and k.strip()]
        if not clean_keys:
            return self._with_guard("hotkey", {"ok": False, "error": "At least one hotkey key is required."})
        try:
            active_before = self.active_window()
            pyautogui = self._import_pyautogui()
            pyautogui.hotkey(*clean_keys)
            active_after = self.active_window()
            return self._with_guard(
                "hotkey",
                {
                    "ok": True,
                    "action": "hotkey",
                    "keys": clean_keys,
                    "target_window_before": active_before.get("window"),
                    "target_window_after": active_after.get("window"),
                },
            )
        except Exception as e:
            return self._with_guard("hotkey", {"ok": False, "error": str(e)})

    def click(self, x: int | None, y: int | None, button: str = "left") -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("click", {"ok": False, "error": "Desktop tool is disabled in config."})
        if x is None or y is None:
            return self._with_guard("click", {"ok": False, "error": "x and y coordinates are required."})
        try:
            pyautogui = self._import_pyautogui()
            size = pyautogui.size()
            if x < 0 or y < 0 or x >= size.width or y >= size.height:
                return self._with_guard(
                    "click",
                    {
                        "ok": False,
                        "error": "Coordinates are outside the screen bounds.",
                        "x": x,
                        "y": y,
                        "screen_width": size.width,
                        "screen_height": size.height,
                    },
                )

            active_before = self.active_window()
            pyautogui.click(x=x, y=y, button=button)
            active_after = self.active_window()
            return self._with_guard(
                "click",
                {
                    "ok": True,
                    "action": "click",
                    "x": x,
                    "y": y,
                    "button": button,
                    "target_window_before": active_before.get("window"),
                    "target_window_after": active_after.get("window"),
                },
            )
        except Exception as e:
            return self._with_guard("click", {"ok": False, "error": str(e)})

    def screenshot(self, raw_path: str | None = None) -> dict[str, Any]:
        if not settings.allow_desktop_tool:
            return self._with_guard("screenshot", {"ok": False, "error": "Desktop tool is disabled in config."})
        try:
            ImageGrab = self._import_imagegrab()
            path = self._artifact_path(raw_path)
            image = ImageGrab.grab()
            image.save(path)
            active = self.active_window()
            return self._with_guard(
                "screenshot",
                {
                    "ok": True,
                    "path": str(path),
                    "message": "Desktop screenshot captured.",
                    "active_window": active.get("window") if active.get("ok") else None,
                },
            )
        except Exception as e:
            return self._with_guard("screenshot", {"ok": False, "error": str(e)})


desktop_tool = DesktopTool()
