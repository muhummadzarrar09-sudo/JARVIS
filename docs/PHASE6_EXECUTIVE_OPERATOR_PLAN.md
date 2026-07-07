# Phase 6 — Executive Operator + Global Reach Plan

## Goal
Turn the stabilized, polished shell into a real daily-use executive assistant:
- chat-first
- quiet by default
- proactive about what matters now
- able to open and use the real external browser the way the user expects
- able to expand beyond one repo with guardrails

This phase is about making JARVIS feel useful every day, not just technically capable.

---

## Guardrails for this phase
- keep the stack Python-first and modular
- keep Laravel/PHP out of the core runtime path
- defer AirLLM-style layer/offload exploration until after Phase 11
- do not spend this phase on orb polish, STT/TTS expansion, or the JARVISH rename
- optimize for mixed personal + business daily use

---

## 6.1 — External browser first
Status: **complete**
Percent: **100.0%**

### Why
The user explicitly wants "open browser" behavior to open a real external browser window by default, not mainly a managed automation surface.

### Scope
- make external browser launch the default path for open/search/browse intents
- preserve controlled/automation mode as an explicit escalation path
- remember preferred browser cleanly and reliably on Windows
- track last launched browser target, URL, and window context without stale wrapper pollution
- add clear success/fallback messaging when a browser launch fails or downgrades

### Implemented
- default browser wrapper path now launches the real external browser first
- managed Playwright mode is preserved as an explicit controlled-mode path
- natural-language commands now support both external and controlled browser intents
- browser search now opens the real browser by default
- browser research and page snapshot flows now explicitly use controlled mode
- runtime browser validation can now validate external launch mode
- shell/runtime context now reports launch mode and external-browser-first posture
- the UI shell can now open the real browser directly without relying only on typed chat commands
- the shell status strip now makes browser mode more visible during normal use

### Exit criteria
- "open browser" opens a real browser by default
- "search for X" launches the preferred external browser with the query
- the shell clearly shows whether JARVIS used external mode or controlled mode
- stale remembered browser state no longer causes confusing behavior

---

## 6.2 — Executive brief engine
Status: **complete**
Percent: **100.0%**

### Why
The shell already looks calmer. Now it needs to think more like a quiet chief-of-staff.

### Scope
- build a stronger daily executive brief from:
  - tasks
  - current project
  - recent sessions
  - next actions
  - runtime/maintenance blockers when relevant
- improve the "Do this now" recommendation so it picks one grounded priority
- support mixed personal + business framing without cluttering the shell
- add better startup / resume language that tells the user what matters immediately

### Implemented
- executive brief logic is now split into a dedicated modular service
- executive brief now weights active tasks, queued tasks, project context, browser thread memory, recent sessions, and setup blockers
- startup subtitle is now more grounded in local signals instead of generic shell copy
- next-step suggestions are now more context-sensitive and less filler-heavy
- today brief now includes the executive brief as the main top-level guidance object
- brief generation now uses ranked action candidates with confidence, operating mode, re-entry hints, and watchouts
- the shell now renders richer brief guidance without throwing more clutter onto the main surface
- natural-language prompts like "what should i do now" and focus-style prompts now route into the executive brief
- quick-actions routes now expose brief-adjacent focus and recent-work endpoints
- executive-brief replies are now cleaner and less JSON-dumpy in chat-first flows

### Exit criteria
- opening the shell gives one clear primary action
- the brief feels grounded in real local state, not generic filler
- the user can ask "what should I do now" and get a useful answer tied to current context

---

## 6.3 — Project and next-action intelligence
Status: **complete**
Percent: **100.0%**

### Why
The user wants JARVIS to act like CEO/CMO/CTO support, not just a chat box.

### Scope
- strengthen current-project pinning, switching, and recovery
- improve next-action generation from project/task/session context
- reduce stale context drift when moving between projects
- support fast capture of ideas, blockers, and follow-ups into the right project context
- improve "resume work" quality so it restores momentum instead of just showing metadata

### Implemented
- current-project intelligence is now split into a dedicated modular service
- project context now carries source, confidence, re-entry hints, watchouts, and concrete next moves
- shell state now exposes a project-intelligence packet alongside the raw project context
- resume-work quality is stronger via a dedicated resume packet instead of only generic metadata
- fast project-context capture now exists for ideas, blockers, notes, and follow-ups
- natural-language prompts like current project and resume work now route into the stronger project intelligence path

### Exit criteria
- the current project is usually right without babysitting
- next actions feel concrete and actionable
- resuming work feels like continuing a real operating thread

---

## 6.4 — Global reach with guardrails
Status: **complete**
Percent: **100.0%**

### Why
The user wants the assistant to become more global over time, but safely.

### Scope
- expand beyond the single workspace with trusted-root rules
- support guarded open/read/edit/search flows for approved folders
- keep destructive actions behind clear approval gates
- improve audit visibility for cross-folder actions
- make path handling Windows-friendly and resilient

### Implemented
- trusted global roots are now configurable alongside the main workspace root
- file access now supports approved folders beyond the repo through trusted-root resolution
- file policy and trusted-root summary endpoints now exist for guardrail visibility
- writes and mkdir operations outside the main workspace can now be flagged for confirmation and reviewed by scope
- wrapper remembered paths now sanitize against trusted roots instead of only the workspace
- project intelligence and shell state now expose trusted-root-aware project continuity
- shell context now shows trusted roots so the operator can see where JARVIS is allowed to work

### Exit criteria
- JARVIS can work across approved folders beyond the repo
- the user can safely let it open and inspect real working locations
- risky actions remain explicit and reviewable

---

## 6.5 — Real-use speed and bug-kill pass
Status: **complete**
Percent: **100.0%**

### Why
The user already flagged that the system can feel slower than expected. This phase should end with a tighter daily-driver loop.

### Scope
- trim obvious shell and route latency where possible
- improve default model/runtime readiness for repeated daily use
- run a fresh real Windows validation pass against the latest minimal shell
- fix bugs discovered from actual use, not speculative polish
- tighten acceptance criteria around response feel, browser behavior, and project continuity

### Implemented
- shell snapshot responses now include generation timing so performance work is visible instead of guessy
- the UI shell refresh path now uses fewer background requests during normal operation
- acceptance status loading is now lazier so it does not tax every refresh cycle
- the status strip now surfaces shell latency and browser mode more directly
- shell state, project continuity, and trusted-root visibility are now better aligned for real daily-driver use

### Exit criteria
- latest shell is validated on the real Windows machine
- the main daily flows feel faster and less fragile
- any remaining blockers are clearly documented before moving on

---

## Recommended implementation order
1. **6.1 external browser first**
2. **6.2 executive brief engine**
3. **6.3 project and next-action intelligence**
4. **6.4 global reach with guardrails**
5. **6.5 real-use speed and bug-kill pass**

---

## Out of scope for this phase
- full mobile companion / Android handoff
- broad voice pipeline expansion
- floating orb UI
- rebrand from JARVIS Local to JARVISH
- AirLLM-style inference/offload experiments
