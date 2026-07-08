from __future__ import annotations

import json
from pathlib import Path

from bravo1.app import build_operator


def main() -> None:
    operator = build_operator()
    report = {
        "runtime": operator.runtime.status(),
        "browser": operator.browser.status(),
        "windows": operator.windows.status(),
        "project": operator.project.inspect(),
    }
    out_dir = Path("data") / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "validation-report.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nSaved runtime validation report to: {out_path}")


if __name__ == "__main__":
    main()
