# BRAVO-1 Architecture v2

## Product shape
BRAVO-1 is a **local-first executive operator shell** for one power user.

It is built around four layers:
1. **Shell** — calm chat-first surface
2. **Operator core** — session, context, action selection, tool routing
3. **Capabilities** — browser, files, terminal, project continuity, memory
4. **Runtime** — local GGUF model serving and process management

---

## Architecture principles
- local-first
- Windows-first real-world usability
- chat-first UX
- low-noise shell
- modular Python core
- minimal hard dependencies at bootstrap
- adapters around external repos/patterns, not framework worship
- rebuild only what gives BRAVO-1 identity

---

## Core module layout

```text
BRAVO-1/
├── app/
│   └── bravo1/
│       ├── config.py
│       ├── cli.py
│       ├── app.py
│       ├── core/
│       │   ├── operator.py
│       │   └── session.py
│       ├── brain/
│       │   └── obsidian.py
│       ├── models/
│       │   └── router.py
│       ├── tools/
│       │   └── registry.py
│       └── channels/
│           └── terminal.py
├── runtime/
├── shell/
├── config/
├── scripts/
├── tests/
└── docs/
```

---

## Layer responsibilities
### 1. Shell layer
Purpose:
- one calm entry point
- one primary action
- minimal noise
- stream status without dashboard clutter

Initial shell modes:
- terminal-first loop
- later thin local web shell
- later packaged desktop wrapper

### 2. Operator core
Purpose:
- load session state
- load project/brain context
- build turn context
- decide action lane
- route to tools or model
- update session + memory after each turn

### 3. Capability layer
Purpose:
- make execution pluggable
- keep repo patterns extractable
- isolate Windows/browser/file concerns from the operator core

Current capabilities:
- file + project continuity
- shell execution
- local model routing/client
- memory/brain integration
- browser adapter bootstrap with remembered external-browser state + text snapshot fetch
- Windows adapter bootstrap with status + Windows window-enumeration path

Later capabilities:
- browser DOM operator
- Windows UIA operator
- voice
- WhatsApp
- camera/verification

### 4. Runtime layer
Purpose:
- own local llama.cpp / llama-server process config
- own model profiles
- own runtime scripts and startup rules
- keep serving concerns separate from agent logic

---

## Session model
Each session should track:
- session id
- current goal
- current project path
- primary action
- recent messages
- last tool results
- last next-step recommendation

Storage phases:
- phase 1: local JSON session state
- phase 2: SQLite + JSON artifacts
- phase 3: richer event/audit timeline

---

## Brain / memory model
Memory is split into:

### Active context
- `brain/active.md`
- current priorities
- current project/thread
- current blockers

### Session summaries
- what happened
- what changed
- what to do next

### Preferences
- user operating preferences
- UX dislikes/likes
- model/runtime defaults

### Project continuity
- current project source/confidence
- recent captures
- resume packet

---

## Model strategy
Runtime path:
- fast model: local GGUF small instruct model
- main model: local GGUF capable instruct model
- routing first, fine-tuning later

Near-term policy:
- optimize prompt/context/tool quality before custom training
- use llama.cpp-compatible serving
- make runtime swappable without rewriting operator code

---

## Tool strategy
All tools should sit behind a narrow interface.

Tool contract:
- name
- description
- validate(args)
- execute(args)
- summarize(result)
- risk level

Initial tool groups:
- session tools
- project tools
- file tools
- shell tools
- model/runtime tools

Later tool groups:
- browser tools
- Windows UIA tools
- voice tools
- channel tools

---

## Phase-1 rebuild target
The first rebuild does **not** aim to recreate the old project.
It aims to stand up the new BRAVO-1 spine.

That means Week 1 is only about:
- package structure
- config loading
- session state
- operator loop skeleton
- brain context file access
- minimal terminal shell
- runtime profile docs/scripts

---

## Repo-synthesis architecture decisions
Borrow patterns from research, but keep BRAVO-1 identity here:

Take from Hermes-style systems:
- operator/session loop
- context injection discipline

Take from Open Second Brain-style systems:
- active brain file
- session summary patterns

Take from Browser Use / Windows-Use later:
- adapter boundaries, not blind codebase worship

Take from Open Interpreter later:
- execution harness pattern

---

## Non-goals for Week 1
- no full web UI
- no browser automation yet
- no Windows control yet
- no WhatsApp yet
- no face verification yet
- no installer yet
- no giant plugin system

---

## Done condition for architecture kickoff
We are ready to build fast when:
- the package imports cleanly
- the CLI loop runs
- the thin web shell runs
- the local API runs
- a session file is created
- `brain/active.md` can be read
- project continuity can be inspected and captured into
- the operator returns a structured response object
- runtime config is documented and scriptable
