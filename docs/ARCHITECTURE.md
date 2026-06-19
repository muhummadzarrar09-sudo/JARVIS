# JARVIS Local Architecture v1

## 1. Product shape

JARVIS is a **local AI operating layer** for your laptop, later extended to a mobile companion.

### Core principles
- local-first
- stateful
- tool-using
- multi-model
- auditable
- replayable
- modular over time

## 2. High-level system

```text
[User: terminal / desktop UI / voice / mobile companion]
                |
                v
         [API + WebSocket Layer]
                |
                v
        [Orchestrator / Router Core]
         /        |         |      \
        /         |         |       \
   [Memory]   [LLM Router] [Tools] [Audit]
                 |
                 v
         [llama.cpp-compatible runtime]
```

## 3. Main modules

### A. Interface layer
Different ways to talk to JARVIS:
- terminal CLI
- local web/desktop UI
- voice pipeline
- Android companion

### B. API layer
Use FastAPI for:
- REST endpoints
- websocket events
- task submission
- session management
- health and diagnostics

### C. Orchestrator core
This is the real brain of the product.

Responsibilities:
- classify user intent
- choose model/tool path
- build context
- query memory
- run steps
- store results
- emit logs/events

### D. LLM router
Instead of one giant model, use multiple local models.

#### Planned routing
- quick replies / classification -> small model
- planning / reasoning -> 7B class model
- summarization -> small model
- code helper -> route later

### E. Memory system
#### 1. Short-term memory
- active chat window
- current objective
- current task state
- current tool chain

#### 2. Semantic memory
- notes
- docs
- project files
- indexed knowledge
- user preferences

#### 3. Episodic memory
- what JARVIS did
- summaries of sessions
- checkpoints for handoff

#### 4. Operational memory
- permissions
- tool policies
- automation recipes
- app state patterns

## 4. Why not only RAG?

RAG is useful for retrieval, but JARVIS also needs:
- continuity
- task state
- action history
- checkpoint restoration
- tool policies

So the correct design is:
- structured store + episodic memory + retrieval layer

## 5. Data stack recommendation for this hardware

### Phase 1 choice
- **SQLite** for structured storage
- local JSONL logs for event streams
- local artifacts folder for screenshots/files

### Later extensions
- SQLite + vector index
- optional Postgres when the project grows
- optional graph layer for relationships later

## 6. Tooling roadmap

### Tool Layer 1 — Terminal
- shell commands
- file creation
- file edits
- process listing
- project scaffolding

### Tool Layer 2 — Browser
- Playwright automation
- search
- dashboards
- logins/forms (with explicit policy)

### Tool Layer 3 — Desktop GUI
- window focus
- click/type
- app controls
- screenshots
- safe action wrappers

### Tool Layer 4 — Connectors / MCP-style registry
- file/index tools
- Git tools
- docs/notes tools
- calendar/email later
- app-specific connectors later

## 7. Autonomy design

User chose near-max autonomy.

That means the product must include:
- audit trails
- replay logs
- undo-oriented operations where possible
- trusted tool zones
- policy labels on tools

### Risk labels
- low: read files, summarize, search local docs
- medium: create/edit files, run normal shell commands
- high: delete files, install packages, system config changes

## 8. Session continuity + mobile handoff

### Desired behavior
- laptop is primary compute host
- phone does not run the heavy models
- when user leaves room, session continues via phone
- when user returns, laptop becomes primary again

### Phase plan
#### Local phase
- mobile web companion on same LAN
- session state served from laptop
- active task timeline synced by websocket

#### Later phase
- secure remote access via VPN / overlay network
- paired device auth
- resumable session tokens

### Checkpoint contents
- active goal
- recent conversation summary
- pending tool actions
- current file/app context
- last generated response
- memory references

## 9. Voice architecture

### Wake flow
- always-listening hotword detector
- speech chunk capture
- STT pipeline
- intent routing
- response generation
- TTS output

### Practical starting recommendation
Because of your hardware:
- begin with text + push/manual voice test mode
- then move to always-listening after core stability

That said, architecture will still support always-listening.

## 10. Model recommendations for your hardware

### Good starter set
#### Fast/router model
- Qwen 2.5 3B Instruct Q4_K_M GGUF

#### Main model
- Qwen 2.5 7B Instruct Q4_K_M GGUF

### Why these
- decent reasoning per size
- practical on 16 GB RAM
- better fit than trying to force huge models

### What not to do first
- don't start with 14B+ expecting smooth real-time use
- don't rely on constant fine-tuning
- don't treat model size as the whole product

## 11. Agent design

Start simple, then split into specialized agents.

### Phase 1 logical roles
- **Conductor**: handles top-level requests
- **Planner**: breaks tasks into steps
- **Executor**: uses tools
- **Memory Keeper**: retrieves/stores context
- **Auditor**: records every action

### Phase 1 implementation detail
These can all live inside one Python codebase first.
Later, you split them into services/modules if needed.

## 12. Local API contract (initial)

### Endpoints
- `GET /health`
- `POST /chat`
- `POST /tools/shell`
- `GET /sessions/current`
- `GET /audit/recent`

### Future endpoints
- `POST /voice/transcribe`
- `POST /voice/speak`
- `POST /handoff/checkpoint`
- `POST /desktop/action`
- `POST /browser/action`

## 13. Recommended build phases

### Phase A — bootstrap + API shell
Goal:
- app runs
- chat endpoint works
- memory DB initializes
- logs recorded

### Phase B — real local LLM
Goal:
- connect llama.cpp runtime
- load GGUF from config
- add model routing

### Phase C — terminal agent
Goal:
- run commands safely
- track stdout/stderr
- store actions in audit

### Phase D — browser/desktop tools
Goal:
- usable automation
- screenshots
- state tracking

### Phase E — voice
Goal:
- local STT/TTS
- subtitles
- orb UX

### Phase F — mobile handoff
Goal:
- companion view
- session resume
- room-exit logic later

## 14. Strategic advice

To make this feel like a real JARVIS, optimize in this order:
1. continuity
2. memory
3. tool reliability
4. action visibility
5. latency
6. voice polish
7. fancy UI

The illusion of intelligence comes from **context + continuity + reliable tools**, not just a bigger model.
