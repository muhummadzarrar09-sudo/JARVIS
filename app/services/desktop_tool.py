import platform
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from app.core.config import settings


class DesktopTool:
    def _windows(self) -> bool:
        return platform.system().lower().startswith("win")

    def _guard(self, action: str) -> dict[str, Any]:
        profiles = {
            "list_windows": {"risk": "low", "reversible": True, "notes": "Read-only window enumeration."},
            "active_window": {"risk": "low", "reversible": True, "notes": "Read-only active window lookup."},
            "screen_info": {"risk": "low", "reversible": True, "notes": "Read-only screen information."},
            "focus_window": {"risk": "medium", "reversible": True, "notes": "Changes active app focus."},
            "type_text": {"risk": "high", "reversible": False, "notes": "Sends text to the currently focused application."},
            "press_key": {"risk": "medium", "reversible": False, "notes": "Sends a single key to the currently focused application."},
            "hotkey": {"risk": "high", "reversible": False, "notes": "Sends a hotkey combo to the currently focused application."},
            "click": {"risk": "high", "reversible": False, "notes": "Clicks screen coordinates directly."},
            "screenshot": {"risk": "low", "reversible": True, "notes": "Captures desktop pixels only."},
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

    def _window_to_dict(self, win) -> dict[str, Any]:
        return {
            "title": (getattr(win, "title", "") or "").strip(),
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

    def _match_windows(self, title: str, exact: bool = False):
        title_l = title.lower().strip()
        all_windows = self._all_titled_windows()
        if exact:
            matches = [w for w in all_windows if (w.title or "").strip().lower() == title_l]
            return matches

        exact_matches = []
        prefix_matches = []
        contains_matches = []
        for win in all_windows:
            current_title = (win.title or "").strip()
            lower_title = current_title.lower()
            if lower_title == title_l:
                exact_matches.append(win)
            elif lower_title.startswith(title_l):
                prefix_matches.append(win)
            elif title_l in lower_title:
                contains_matches.append(win)
        return exact_matches + prefix_matches + contains_matches

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

    def focus_window(self, title: str, exact: bool = False) -> dict[str, Any]:
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

            win = matches[0]
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

            active = self.active_window()
            selected = self._window_to_dict(win)
            focused_title = (active.get("window") or {}).get("title") if active.get("ok") else None
            success = focused_title is not None and focused_title.lower() == selected["title"].lower()

            return self._with_guard(
                "focus_window",
                {
                    "ok": success,
                    "requested_title": title,
                    "selected_window": selected,
                    "match_count": len(matches),
                    "other_matches": [self._window_to_dict(m)["title"] for m in matches[1:6]],
                    "restore_attempted": restore_attempted,
                    "activation_attempts": activation_attempts,
                    "active_window_after": active.get("window") if active.get("ok") else None,
                    "exact": exact,
                    "error": None if success else "A matching window was found but focus could not be verified.",
                },
            )
        except Exception as e:
            return self._with_guard("focus_window", {"ok": False, "error": str(e), "exact": exact})

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
