from __future__ import annotations

import json
from pathlib import Path


def collect_files(root: Path) -> list[str]:
    items: list[str] = []
    for path in sorted(root.rglob('*')):
        if path.is_dir():
            continue
        rel = path.relative_to(root)
        items.append(str(rel))
    return items


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest_dir = root / 'installer'
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / 'build-manifest.json'
    manifest = {
        'project': 'BRAVO-1',
        'entrypoints': {
            'cli': 'python -m bravo1.cli',
            'web': 'python -m bravo1.web_main',
            'api': 'python -m bravo1.api_main',
            'validate_runtime': 'python scripts/runtime_validation.py',
        },
        'included_files': collect_files(root / 'app') + collect_files(root / 'config') + collect_files(root / 'runtime') + collect_files(root / 'shell') + collect_files(root / 'scripts'),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"\nSaved installer build manifest to: {manifest_path}")


if __name__ == '__main__':
    main()
