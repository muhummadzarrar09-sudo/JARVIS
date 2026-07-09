from __future__ import annotations

import platform
import sys
from pathlib import Path


REQUIRED_PATHS = [
    Path('app/bravo1/cli.py'),
    Path('app/bravo1/web_main.py'),
    Path('app/bravo1/api_main.py'),
    Path('config/bravo1.example.env'),
    Path('runtime/profiles/llama-server-fast.ps1'),
    Path('runtime/profiles/llama-server-main.ps1'),
    Path('scripts/runtime_validation.py'),
]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version.split()[0]}")
    missing = []
    for rel in REQUIRED_PATHS:
        full = root / rel
        exists = full.exists()
        print(f"{'OK ' if exists else 'MISS'} {rel}")
        if not exists:
            missing.append(str(rel))
    if missing:
        print("\nInstaller prereq check failed.")
        sys.exit(1)
    print("\nInstaller prereq check passed.")


if __name__ == '__main__':
    main()
