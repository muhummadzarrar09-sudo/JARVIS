from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.acceptance_service import acceptance_service


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Phase 5.11.5 acceptance sweep")
    parser.add_argument("--deep", action="store_true", help="Include browser and desktop active-window validation actions.")
    args = parser.parse_args()
    result = acceptance_service.run(deep=args.deep)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
