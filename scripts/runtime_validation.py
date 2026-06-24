from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.app_wrapper_service import app_wrapper_service
from app.services.browser_tool import browser_tool
from app.services.desktop_tool import desktop_tool
from app.services.progress_service import progress_service
from app.services.validation_service import validation_service
from app.services.model_service import model_service


def _serialize(obj: Any) -> Any:
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        if isinstance(obj, dict):
            return {str(k): _serialize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_serialize(v) for v in obj]
        return str(obj)


def _requested_browser_names(raw_values: list[str] | None, available: list[dict[str, Any]]) -> list[str]:
    if not raw_values:
        return [item.get("name") for item in available if item.get("name")]

    names = []
    for raw in raw_values:
        parts = [part.strip() for part in raw.split(",") if part.strip()]
        names.extend(parts)
    deduped = []
    for name in names:
        if name not in deduped:
            deduped.append(name)
    return deduped


def collect_report(
    attempt_browser_starts: bool,
    attempt_browser_opens: bool,
    browser_url: str,
    focus_title: str | None,
    focus_match_index: int,
    requested_browsers: list[str] | None,
) -> dict[str, Any]:
    validation = validation_service.report()
    browser_available = browser_tool.available_browsers()
    available_items = browser_available.get("items", []) if browser_available.get("ok") else []

    report: dict[str, Any] = {
        "ts": datetime.now(UTC).isoformat(),
        "validation_report": validation,
        "phase4": progress_service.phase4_status(),
        "phase5": progress_service.phase5_status(),
        "browser_available": browser_available,
        "browser_context": app_wrapper_service.current_browser_context(),
        "browser_doctor": app_wrapper_service.wrapper_doctor("browser"),
        "model_status": model_service.status(),
        "desktop_safety": desktop_tool.safety_status(),
        "desktop_active": desktop_tool.active_window(),
        "desktop_windows": desktop_tool.list_windows(),
        "shell_launcher": validation.get("shell_launcher"),
    }

    if focus_title:
        report["desktop_find"] = desktop_tool.find_windows(focus_title, exact=False)
        report["desktop_focus_attempt"] = desktop_tool.focus_window(focus_title, exact=False, match_index=focus_match_index)
        if report["desktop_focus_attempt"].get("ok"):
            report["desktop_focus_undo"] = desktop_tool.undo_last_focus()

    if attempt_browser_starts or attempt_browser_opens:
        names = _requested_browser_names(requested_browsers, available_items)
        browser_checks = []
        for name in names:
            entry: dict[str, Any] = {"candidate": name}
            start_result = browser_tool.start(browser_name=name)
            entry["start"] = start_result
            if attempt_browser_opens and start_result.get("ok"):
                entry["open_url"] = browser_tool.open_url(browser_url, browser_name=name)
                entry["state_after_open"] = browser_tool.state()
                entry["title_after_open"] = browser_tool.title()
            browser_checks.append(entry)
            browser_tool.close()
        report["browser_start_attempts"] = browser_checks

    return _serialize(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="JARVIS local runtime validation")
    parser.add_argument("--attempt-browser-starts", action="store_true", help="Try launching detected browser candidates.")
    parser.add_argument("--attempt-browser-opens", action="store_true", help="Try launching detected browser candidates and opening a URL.")
    parser.add_argument("--browser-url", default="https://example.com", help="URL to use when browser open validation is requested.")
    parser.add_argument("--browser", action="append", default=None, help="Specific browser name(s) to validate, repeat or comma-separate values.")
    parser.add_argument("--focus-title", default=None, help="Optional window title to test fuzzy desktop finding and focus.")
    parser.add_argument("--focus-match-index", type=int, default=0, help="Match index to use when testing desktop focus.")
    parser.add_argument("--output", default=None, help="Optional path for JSON output.")
    args = parser.parse_args()

    report = collect_report(
        attempt_browser_starts=args.attempt_browser_starts,
        attempt_browser_opens=args.attempt_browser_opens,
        browser_url=args.browser_url,
        focus_title=args.focus_title,
        focus_match_index=args.focus_match_index,
        requested_browsers=args.browser,
    )

    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path("data/validation")
        output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        output_path = output_dir / f"runtime-validation-{stamp}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved validation report to: {output_path}")


if __name__ == "__main__":
    main()
