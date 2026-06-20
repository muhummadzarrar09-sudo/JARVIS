# Build Audit — JARVIS Console UI Starter

This audit covers the terminal UI pass inspired by the usability of Claude Code, adapted for JARVIS.

## Goals targeted
- make the terminal feel more like a command center
- surface wrapper/tool/session state at startup
- add dashboard-style slash commands
- keep the terminal as a prototype for the future packaged desktop app shell

## Added / expanded behavior

### `app/cli.py`
Added:
- JARVIS console banner
- startup dashboard panels
- wrapper status table
- recipe table
- tool registry table
- slash commands:
  - `/status`
  - `/wrappers`
  - `/recipes`
  - `/tools`
  - `/clear`
- prompt changed to `jarvis>`

### `docs/JARVIS_CONSOLE_UI.md`
Added:
- terminal UI vision
- relationship between terminal UI and future desktop app shell
- Claude-Code-inspired but JARVIS-specific direction

### `README.md`
Updated docs references to include console UI planning

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- CLI module import/compile succeeded

## Remaining gaps
- no live split-pane/event loop UI yet
- no streaming token output yet
- no inline diff/review panel yet
- no desktop-app shell yet; this is the terminal prototype layer
