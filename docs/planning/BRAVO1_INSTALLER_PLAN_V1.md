# BRAVO-1 Installer Plan v1

## Goal
Ship a real Windows installer later as:
- `BRAVO-1-Setup.exe`

This installer should allow BRAVO-1 to be installed into any user-selected folder with the required runtime pieces.

---

## Installer scope
### Must do
- install BRAVO-1 app files
- let the user choose install location
- create application directories
- create Start Menu shortcut
- create Desktop shortcut (optional)
- write config/bootstrap files
- support uninstall

### Should do
- detect Python presence
- install or verify Python version if missing
- optionally bootstrap runtime dependencies
- expose first-run setup flow
- allow model-path selection

### Later hardening
- signed installer
- upgrade path
- optional auto-update
- runtime dependency checks
- browser/Windows automation dependency installer

---

## Packaging candidates
### Candidate A — PyInstaller + Inno Setup
Pros:
- practical for Python apps
- common Windows path
- can wrap CLI/API/web shell launchers

Cons:
- bigger bundle
- hidden complexity for data/runtime files

### Candidate B — Embedded Python + Inno Setup
Pros:
- more explicit control
- easier to reason about Python runtime layout

Cons:
- more manual setup effort

## Current recommendation
Use:
- **PyInstaller for app bundling**
- **Inno Setup for installer wizard**

Later validate whether embedded Python gives a cleaner operational story.

---

## Installer layout target
```text
BRAVO-1/
├── app bundle
├── runtime profiles
├── config templates
├── data/
│   ├── brain/
│   ├── sessions/
│   ├── summaries/
│   └── runtime/
├── logs/
└── shortcuts
```

---

## First installer milestone
Not to build yet, but to prepare for:
1. stable API entrypoint
2. stable CLI entrypoint
3. stable web shell entrypoint
4. reproducible config bootstrap
5. reproducible runtime validation script
6. pinned dependency strategy

BRAVO-1 is not ready for the full installer pass yet, but v0.5+ should now intentionally keep that destination in view.
