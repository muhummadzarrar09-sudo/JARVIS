from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, UTC
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


def collect_report(attempt_browser_starts: bool, focus_title: str | None) -> dict[str, Any]:
    report: dict[str, Any] = {
        "ts": datetime.now(UTC).isoformat(),
        "validation_report": validation_service.report(),
        "phase4": progress_service.phase4_status(),
        "browser_available": browser_tool.available_browsers(),
        "browser_doctor": app_wrapper_service.wrapper_doctor("browser"),
        "desktop_safety": desktop_tool.safety_status(),
        "desktop_active": desktop_tool.active_window(),
        "desktop_windows": desktop_tool.list_windows(),
    }

    if focus_title:
        report["desktop_find"] = desktop_tool.find_windows(focus_title, exact=False)

    if attempt_browser_starts:
        start_results = []
        candidates = report["browser_available"].get("items", []) if report["browser_available"].get("ok") else []
        for candidate in candidates:
            name = candidate.get("name")
            result = browser_tool.start(browser_name=name)
            start_results.append({"candidate": name, "result": result})
            browser_tool.close()
        report["browser_start_attempts"] = start_results

    return _serialize(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="JARVIS local runtime validation")
    parser.add_argument("--attempt-browser-starts", action="store_true", help="Try launching detected browser candidates.")
    parser.add_argument("--focus-title", default=None, help="Optional window title to test fuzzy desktop finding.")
    parser.add_argument("--output", default=None, help="Optional path for JSON output.")
    args = parser.parse_args()

    report = collect_report(args.attempt_browser_starts, args.focus_title)

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
