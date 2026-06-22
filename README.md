# JARVIS Local

A local-first JARVIS-style assistant for Windows 11 + Android handoff.

## Vision

This project is designed around your stated goals:
- 100% local-first operation
- terminal-first MVP
- later browser + desktop control
- always-listening voice layer
- beautiful orb-based UI later
- laptop remains the primary compute node
- Android acts as a companion / handoff interface
- full audit trail + replay-oriented action logs
- personal first, product later

## Recommended phase order

### Phase 0 — Foundation
- bootstrap Python environment
- install local dependencies
- create local data folders
- download starter GGUF model(s)
- launch FastAPI service

### Phase 1 — Brain + Terminal MVP
- local LLM routing
- chat endpoint
- memory store
- audit trail
- shell / terminal tool execution
- task/session management

### Phase 2 — Tooling + Connectors
- filesystem tools
- Git tools
- app/process tools
- local MCP-style tool registry abstraction
- connectors added sequentially

### Phase 3 — Browser + Desktop Control
- browser automation via Playwright
- Windows desktop automation
- screenshots + app state capture
- safer action gating / undo hooks

### Phase 4 — Voice + UI
- always-listening wake-word pipeline
- local STT
- local TTS
- orb UI + subtitles
- human-readable activity timeline

### Phase 5 — Android Handoff
- mobile web / companion UI
- session handoff from laptop to mobile
- local LAN first
- secure remote access later

## Suggested local model strategy for your hardware

Your laptop:
- Windows 11
- i7 7th gen
- 16 GB RAM
- GTX 1050 Ti 4 GB

Best strategy:
- use **small-to-medium GGUF models** via llama.cpp / llama-cpp-python
- route by task instead of forcing one huge model to do everything

Recommended starting models:
- **Fast model**: Qwen 2.5 3B Instruct Q4_K_M
- **Main model**: Qwen 2.5 7B Instruct Q4_K_M
- optional later: a coding-specialized small model if needed

## Recommended speech stack

### STT
- start with **faster-whisper**
- default to `small` or `base` depending on latency
- later add hybrid routing

### TTS
- start with **Piper** or **Kokoro** class lightweight local TTS
- later upgrade to more stylized / cloned voice workflows

## Memory design

This is not just "RAG".

JARVIS memory should have 4 layers:
- short-term session memory
- long-term semantic memory
- episodic memory (what happened)
- operational memory (tools, workflows, permissions, states)

For MVP:
- SQLite for structured memory + audit
- local file storage for artifacts
- vector layer can be added after terminal MVP is stable

## Quick start

### Windows PowerShell
```powershell
cd jarvis-local
.\bootstrap.ps1
```

Notes:
- bootstrap now inspects available Python interpreters and prefers Python 3.11 for the virtual environment
- if an existing `.venv` is on an incompatible Python version, bootstrap can back it up and rebuild it automatically
- `llama-cpp-python` is installed as a best-effort step with an import check afterward
- Playwright browser support is also attempted as a best-effort step
- if optional runtime installs fail, you can still run the project in `mock` mode first

Then:
```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Or run the terminal-first interface:
```powershell
.\.venv\Scripts\Activate.ps1
python -m app.cli repl
```

Convenience scripts:
```powershell
.\scripts\start-api.ps1
.\scripts\start-cli.ps1
.\scripts\install-browser.ps1
.\scripts\install-desktop.ps1
.\scripts\download-models.ps1
.\scripts\validate-runtime.ps1
```

Open:
- API docs: http://127.0.0.1:8000/docs
- health: http://127.0.0.1:8000/health

## Current scaffold

This repo includes:
- FastAPI app skeleton
- terminal CLI / REPL
- config loader
- chat endpoint
- simple orchestrator
- audit log service
- SQLite memory bootstrap
- shell tool service
- filesystem tool service
- browser automation tool service
- process / laptop-control groundwork
- desktop control starter layer
- session checkpoint groundwork for handoff
- task management + session overview endpoints
- PowerShell bootstrap script

## Planning docs
- `docs/MASTER_PLAN_STATUS.md` — single source of truth for status, phase completion, and next steps
- `docs/ROADMAP_V1.md` — current roadmap + status, including desktop app timing
- `docs/PHASE_PLAN.md` — high-level phase sequence
- `docs/CONTROL_PHASES.md` — control/continuity extensions
- `docs/DESKTOP_MODE.md` — desktop control starter commands
- `docs/APP_WRAPPERS.md` — higher-level application wrappers and recipes
- `docs/JARVIS_CONSOLE_UI.md` — terminal UI direction inspired by Claude Code, but JARVIS-specific
- `docs/PHASE5_DESKTOP_SHELL_PLAN.md` — next-phase desktop shell plan
- `docs/USAGE.md` — practical commands and examples

## Next recommended move

1. run the bootstrap script
2. verify the app starts in `mock` mode
3. test `/chat`, terminal CLI, and browser mode
4. switch to `llama_cpp` after GGUF + runtime are ready
5. use shell / filesystem / browser tools for real workflows
6. layer in desktop automation next

## Important reality check

A real JARVIS is built in layers:
- memory
- routing
- tools
- logs
- safety
- session state
- interfaces

Do **not** start by chasing giant models.
Start by building the operating system around the model.
