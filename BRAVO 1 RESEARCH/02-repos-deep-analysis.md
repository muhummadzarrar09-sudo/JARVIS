# BRAVO-1 — Repo-by-Repo Deep Analysis

---

## REPO #1: Hermes Agent
**GitHub:** https://github.com/NousResearch/hermes-agent  
**Stars:** 211k | **Forks:** 38.6k | **License:** MIT  
**Language:** Python + TypeScript | **Platform:** Cross-platform  
**Local-First:** YES (zero cloud dependency) | **Active:** YES (14,751 commits)

---

### WHAT MAKES IT THEM?

**The Core Magic:** Hermes Agent is the **definitive implementation of the "operator loop"** — a persistent agent that maintains session context, executes tools, handles multi-channel messaging, and continuously improves through a preference tracking system.

**Specific interaction pattern:**
```
User speaks (voice or text)
  → STT transcription (faster-whisper local)
  → Session context injection (Brain/active.md)
  → Operator reasoning loop
  → Tool execution
  → Session memory update
  → Response (text or TTS)
```

**What makes it addictive:**
1. **Session persistence** — Your work survives restarts. When you `hermes` back in, it knows your project, recent decisions, and active tasks.
2. **Multi-channel routing** — WhatsApp, Telegram, Discord, Email all route to the same agent brain with per-channel session isolation.
3. **Skills hub** — 150+ skills that teach the agent how to use tools. Import from OpenClaw (13,700 community skills).
4. **Voice mode** — Push-to-talk with local faster-whisper STT. No cloud dependency for voice.
5. **Human-like delays** — Response pacing that makes the agent feel natural, not robotic.
6. **YOLO mode** — `--yolo` flag to auto-approve dangerous commands. Power user feature.

**The specific thing you'd lose if it disappeared:**
The **brain/active.md injection pattern** — Every turn, the agent reads `Brain/active.md` which contains: current project, active tasks, recent decisions, user preferences. Without this, you have a generic chatbot. With it, you have a chief-of-staff who knows what matters.

---

### EXTRACTABLE VALUE

**Copy directly (concept):**
- Session lifecycle management (create → maintain → handoff → archive)
- Multi-channel message routing with session isolation
- Brain/active.md context injection pattern
- Skills hub plugin architecture
- Voice mode pipeline (STT → LLM → TTS)
- Quick commands (zero-token shell execution)

**Adapt:**
- MCP server architecture for tool exposure
- Subagent delegation with isolated context
- Provider routing (fallback chains, model switching)
- Context compression (auto-summarize long conversations)
- Honcho cross-session user modeling

**Avoid:**
- Complex messaging platform integrations (Teams, Google Chat) — overkill for WhatsApp-only
- Sampling (server-initiated LLM requests) — adds complexity without clear value for solo user
- Remote SSH terminal backend — not needed for local Windows operation

**Best for:**
- ✅ Operator feel (the #1 reason to study this repo)
- ✅ Session continuity
- ✅ Skills system
- ✅ Multi-channel messaging
- ✅ Voice pipeline
- ❌ Git-native coding workflows (use Aider instead)
- ❌ Enterprise multi-team features

---

### COMMIT HISTORY FINDINGS

**Momentum:** EXPLOSIVE
- 14,751 commits (massive)
- Latest commit: 4 minutes ago (at time of research)
- Active development daily
- 1283 branches, 25 tags

**Commit cadence:** Consistent, daily commits with bursty feature development
- Regular maintenance: CI fixes, dependency updates, bug fixes
- Feature bursts: Messaging platform additions, skill system expansion, voice mode improvements
- PR-driven: Community contributions actively merged (#724: YOLO mode, #52336: Ruff fixes)

**Architecture evolution:** 
- V0.18.0 release (July 2026) shows active versioning
- MCP adapter layer suggests evolving tool architecture
- Multiple provider support (OpenRouter, Groq, Ollama, etc.) indicates flexible runtime design

**Signals of serious engineering:**
- CI timing report retry handling (issue #59818) — obsessive about reliability
- Ruff linting at scale (216 dead f-string prefix fixes) — code quality discipline
- TypeScript rewrite of Open Second Brain — architectural improvement over Python shim
- Security hardening (event_log_append validation, identity blacklist) — production-grade

**Signals of product maturity:**
- Skills hub ecosystem established
- Multi-channel production-ready
- Voice mode with multiple TTS providers
- Context compression at 85% threshold
- Session logging for audit trail

**Verdict:** This is the most actively maintained, production-hardened operator agent in open source. 14,751 commits speaks for itself.

---

### ARCHITECTURE INSIGHTS

**Module boundaries:**
```
hermes-agent/
├── acp_adapter/         # Agent Communication Protocol adapters
├── acp_registry/        # Tool/knowledge registration
├── gateway/             # Webhook server (messaging platforms)
├── cli/                 # Terminal interface
├── memory/              # Memory providers (Obsidian, Honcho)
├── tools/               # MCP tool definitions
├── providers/           # LLM provider abstraction
├── skills/              # Skill loading and execution
└── voice/               # STT/TTS pipelines
```

**Orchestration style:** Event-driven with session context
- Messages come in via gateway (webhooks)
- Session resolver maps message → session
- Agent loop processes with context injection
- Tools execute via MCP or direct subprocess
- Response routed back via same channel

**Tool wiring:**
- MCP servers as first-class citizens
- StdIo servers (subprocess) and HTTP servers (remote)
- Per-server timeout, keepalive, sampling config
- Skills are MCP-compatible tool definitions

**State management:**
- Sessions stored as JSON in `~/.hermes/sessions/`
- Brain files as Markdown in vault
- User modeling via Honcho (SQLite + embeddings)
- No external database dependency

**Complexity concentration:**
- Gateway is the hub — handles all messaging
- Skills system adds extensibility but also complexity
- Multi-provider routing is complex but well-isolated

---

### FIT FOR BRAVO-1: 10/10

**This is the FOUNDATION.** Every core BRAVO-1 promise maps directly to Hermes capabilities:

| BRAVO-1 Promise | Hermes Implementation |
|-----------------|----------------------|
| Calm chat UI | CLI TUI with streaming, tool progress display |
| Chief-of-staff brain | Brain/active.md context injection |
| Real project continuity | Session persistence + Obsidian vault |
| Real browser support | Playwright MCP, Firecrawl integration |
| Low noise | Compact banner mode, tool progress "new" mode |
| Fast resume | Session handoff with active context |
| Local-first | Zero cloud dependency, all local models |
| Strong tool execution | MCP tools, quick commands, shell execution |
| Voice input | faster-whisper STT, local or cloud |
| WhatsApp channel | WhatsApp webhook gateway |

**Risks:**
- Heavy Python dependencies (may conflict with Rust/Tauri UI plans)
- Complex multi-channel architecture if you only need WhatsApp
- Skills system overhead if you're building custom tools

**Mitigation:** Take the session management, context injection, and operator loop. Leave the messaging gateway complexity for later phases.

---

## REPO #2: Browser Use
**GitHub:** https://github.com/browser-use/browser-use  
**Stars:** 103k | **Forks:** 11.4k | **License:** MIT  
**Language:** Python | **Platform:** Cross-platform  
**Local-First:** YES | **Active:** YES (9,800 commits)

---

### WHAT MAKES IT THEM?

**The Core Magic:** Browser Use solves the **vision bottleneck** — instead of requiring expensive vision models to understand screenshots, it converts the browser's DOM (Document Object Model) into a structured text format that ANY LLM can reason about.

**The specific technical insight:**
```python
# Instead of screenshot → vision model → coordinates
# Browser Use does:
browser_page.get_dom()  # Get structured DOM tree
# Converts to:
# [button] Submit [/button]
# [input type="email" placeholder="Enter email"] 
# [a href="/products"] View Products [/a]
# → LLM can reason about this TEXT directly
```

**What makes it powerful:**
1. **83.3% on WebVoyager benchmark** — Using DOM parsing, not vision
2. **Persistent browser sessions** — Cookies, local storage, logged-in state survives
3. **Headful + headless modes** — Visible browser for auth flows, headless for automation
4. **Element reference system** — Instead of coordinates, uses structural element references
5. **LangChain integration** — Easy to swap models, including local Ollama
6. **Skills system** — Claude Code-style skills for browser operations

**The specific thing you'd lose if it disappeared:**
The **accessibility tree extraction + element reference mapping**. Without this, you're doing screenshot-based automation that requires vision models. With it, a 3B Qwen model can drive a real browser on your GTX 1050 Ti.

---

### EXTRACTABLE VALUE

**Copy directly (concept):**
- DOM-to-element extraction pipeline
- Browser session management (persistent contexts)
- Headful/headless mode switching
- Element reference system (structured action output)
- LangChain agent integration pattern

**Adapt:**
- Playwright MCP server pattern
- Browser profile management
- Stealth browser features (proxy rotation, anti-bot)
- Benchmark framework (WebVoyager evaluation)

**Avoid:**
- Cloud Firecrawl dependency (self-host or skip)
- Heavy LangChain dependencies (use lighter orchestration)
- Complex multi-agent browser orchestration

**Best for:**
- ✅ Browser automation architecture
- ✅ DOM-based UI reasoning
- ✅ Session persistence
- ✅ Headful auth flows
- ❌ Screenshot-based UI control (use Windows-Use instead)
- ❌ Heavy enterprise browser features

---

### COMMIT HISTORY FINDINGS

**Momentum:** STRONG
- 9,800 commits
- Latest commit: 7 hours ago
- Active development with 530 branches

**Commit cadence:** Consistent with focused development
- DOM visibility fixes (recent)
- Type checking and linting improvements
- Docker build context fixes
- Skill sync maintenance

**Signals of serious engineering:**
- DOM visibility idempotency testing (strengthened)
- Type checking strictness (pyproject.toml enhancement)
- Lint script reliability improvements
- Benchmark tracking (78% result for BU-Ultra)

**Signals of product maturity:**
- Skills system established
- Docker support production-ready
- Python package well-structured
- Tests covering edge cases

**Verdict:** Active, well-engineered project with clear product direction. The commit on DOM visibility idempotency shows they're fixing real reliability issues, not just adding features.

---

### ARCHITECTURE INSIGHTS

**Module boundaries:**
```
browser_use/
├── browser/              # Playwright wrapper, session management
├── views/                # DOM extraction, element extraction
├── agent/                # LLM agent loop
├── skills/               # Browser operation skills
└── utils/                # Helper functions
```

**Orchestration style:** LangChain agent with custom browser tools
- Task description → Agent reasoning → Tool execution → Browser state → Repeat
- DOM extraction on each step for LLM context
- Element references as action targets

**Tool wiring:**
- Custom Playwright-based tools
- Browser state as shared context
- Element reference as structured output

**State management:**
- Browser session (cookies, local storage, page state)
- DOM snapshot for LLM context
- Action history for planning

**Complexity concentration:**
- Agent loop is the complexity center
- DOM extraction is compute-intensive
- Session management must be reliable

---

### FIT FOR BRAVO-1: 9/10

**Critical for browser automation.** Your stated use case of "switching between tabs and building apps" requires real browser control.

**Key advantage:** DOM-based, not vision-based. This means:
- Qwen 3B can drive it ✅
- GTX 1050 Ti can handle it ✅
- No expensive API calls for page understanding ✅

**Risks:**
- Requires Playwright (heavy dependency)
- DOM extraction can be slow on complex pages
- LangChain overhead may be unnecessary

**Mitigation:** Extract the DOM extraction and element reference system. Build your own lighter agent loop on top.

---

## REPO #3: Open Interpreter
**GitHub:** https://github.com/openinterpreter/open-interpreter  
**Stars:** 64k | **Forks:** 5.6k | **License:** Apache-2.0  
**Language:** Rust + Python | **Platform:** Cross-platform  
**Local-First:** YES | **Active:** YES (8,064 commits)

---

### WHAT MAKES IT THEM?

**The Core Magic:** Open Interpreter is the **definitive "execute real code on your real machine"** agent. It's not sandboxed, not cloud-dependent, not restricted. You ask it to "build me a React app" and it writes Python, JavaScript, Shell — and executes it on your machine.

**The specific interaction pattern:**
```
User: "Download that PDF and extract the text"
↓
Agent writes Python:
  import requests
  import pdfplumber
  response = requests.get(url)
  with open('doc.pdf', 'wb') as f:
      f.write(response.content)
  with pdfplumber.open('doc.pdf') as pdf:
      text = '\n'.join([p.extract_text() for p in pdf.pages])
↓
Code executed locally with confirmation prompt
↓
Result returned
```

**What makes it powerful:**
1. **No sandbox** — Code runs on your real machine, with real filesystem access
2. **Harness system** — Switch between Claude Code harness, native harness, etc.
3. **OS mode** — Screenshot-based desktop control (alternative to Windows-Use)
4. **QA skill** — Built-in testing of web apps and native apps
5. **Multi-language** — Python, JavaScript, Shell, R, AppleScript, etc.

**The specific thing you'd lose if it disappeared:**
The **zero-sandbox execution philosophy**. Every other agent tool either sandboxes code or requires you to manually run commands. Open Interpreter bridges this gap — natural language → real code → real execution.

---

### EXTRACTABLE VALUE

**Copy directly (concept):**
- Code execution framework (write → confirm → execute → return)
- Harness system for swapping agent behaviors
- Tool adapter interface (narrow contract)
- OS mode for desktop control

**Adapt:**
- Multi-language code generation
- Sandbox alternatives (Docker, subprocess isolation)
- Testing/QA workflow integration

**Avoid:**
- Heavy Rust/Python build complexity (Bazel build system)
- Over-engineered for simple use cases
- Complex QA skill system if not needed

**Best for:**
- ✅ Code execution architecture
- ✅ Tool framework design
- ✅ OS mode patterns
- ✅ Harness/behavior swapping
- ❌ Git-native workflows (use Aider instead)
- ❌ Enterprise deployment

---

### COMMIT HISTORY FINDINGS

**Momentum:** STRONG
- 8,064 commits
- Latest commit: 9 hours ago
- Rust rewrite in progress (codex-rs)

**Commit cadence:** Consistent with architectural evolution
- Bazel build system additions
- Rust rewrite progress
- Python version maintenance
- CI workflow updates

**Signals of serious engineering:**
- Bazel build system (enterprise-grade build management)
- Rust rewrite for performance
- Multiple harness implementations
- Comprehensive test coverage

**Signals of product maturity:**
- Multiple platform support (Windows, macOS, Linux)
- Stable Python API
- Documentation comprehensive
- Community established

**Verdict:** Production-grade code execution platform with active development. The Rust rewrite signals long-term investment.

---

### FIT FOR BRAVO-1: 9/10

**Critical for tool execution.** Your "uses my laptop BY ITS OWN SELF" vision requires code execution capability.

**Key advantage:** No sandbox = full system access. This is exactly what you want for an operator that controls your machine.

**Risks:**
- Over-engineered build system (Bazel)
- Rust rewrite may complicate integration
- Confirmation prompts may interrupt autonomous flow

**Mitigation:** Take the harness pattern and code execution framework. Build your own lighter implementation with Windows-Use for GUI control.

---

## REPO #4: Windows-Use
**GitHub:** https://github.com/CursorTouch/Windows-Use  
**Stars:** 968 | **Forks:** N/A | **License:** MIT  
**Language:** Python | **Platform:** Windows-only  
**Local-First:** YES | **Active:** YES

---

### WHAT MAKES IT THEM?

**The Core Magic:** Windows-Use is the **only open-source project that directly controls Windows at the GUI layer using Microsoft UI Automation (UIA)** — not screenshots, not coordinates, not OCR. It reads the Windows control tree and lets the LLM interact with buttons, text fields, menus, and dialogs directly.

**The specific technical insight:**
```python
# Instead of: screenshot → vision model → "click at (453, 821)"
# Windows-Use does:
from windows_use import UIAutomationClient
elements = UIAutomationClient.get_control_tree()
# Returns structured element tree:
# Window "Notepad" → Button "OK", Edit "Type here", Menu "File→Edit→Format"
# → LLM can say: "click the OK button in the About dialog"
# → No coordinates, no vision, just direct control
```

**What makes it powerful:**
1. **UIA-based control** — Works with ANY Windows app that exposes accessibility tree
2. **11 built-in tools** — click, type, scroll, move, shortcut, app control, shell, scrape, desktop, wait, done
3. **Multi-provider LLM support** — Anthropic, OpenAI, Google, Groq, Ollama, Mistral, Cerebras, DeepSeek, Azure, OpenRouter, LiteLLM, NVIDIA, vLLM
4. **Voice input** — STT/TTS configuration built in
5. **CLI interface** — `\llm`, `\key`, `\speech`, `\voice`, `\clear`, `\quit`

**The specific thing you'd lose if it disappeared:**
The **UIA element tree extraction + action schema generation**. This is the foundation of reliable Windows GUI automation. Without it, you're stuck with coordinate-based automation that breaks constantly.

---

### EXTRACTABLE VALUE

**Copy directly (concept):**
- UIA element tree extraction
- Action planning from element tree
- Tool set definition (click, type, scroll, app control, shell)
- Multi-provider LLM support
- CLI interface pattern

**Adapt:**
- Windows virtual desktop control
- Application window management
- Keyboard shortcut composition

**Avoid:**
- Dependency on CursorTouch MCP (build own integration)
- Over-reliance on UIA (some apps don't expose it well)

**Best for:**
- ✅ Windows GUI automation
- ✅ UIA-based control
- ✅ Tool set design
- ✅ Multi-provider routing
- ❌ Cross-platform support
- ❌ Browser automation (use Browser Use instead)

---

### COMMIT HISTORY FINDINGS

**Momentum:** ACTIVE (newer project)
- Regular commits
- Recent documentation updates
- Active issue resolution

**Commit cadence:** Consistent with active maintenance
- README improvements
- Documentation additions
- Issue responses

**Signals of engineering:**
- Clear tool design
- Comprehensive documentation
- Multi-provider support indicates flexible architecture

**Verdict:** Active, focused project with clear Windows-native direction.

---

### ARCHITECTURE INSIGHTS

**Module boundaries:**
```
windows_use/
├── providers/            # LLM provider implementations
├── tools/                # UIA-based automation tools
├── ui_automation/        # Windows UIA client
└── cli/                  # Command-line interface
```

**Orchestration style:** Simple loop with tool execution
- Task description → UIA tree extraction → LLM reasoning → Tool execution → State update

**Tool wiring:**
- UIA tools as first-class citizens
- Element references as action targets
- Shell tool for PowerShell commands

**State management:**
- UIA tree snapshot for context
- Action history for planning

---

### FIT FOR BRAVO-1: 9/10

**Critical for Windows control.** Your "control my computer BY ITS OWN SELF" vision requires direct Windows GUI access.

**Key advantage:** UIA-based = text-based reasoning = works with Qwen 3B on GTX 1050 Ti.

**Synergy with Browser Use:**
- Browser Use handles web browser automation
- Windows-Use handles Windows desktop apps
- Together they cover all automation needs

---

## REPO #5: Aider
**GitHub:** https://github.com/paul-gauthier/aider  
**Stars:** 47k | **Forks:** N/A | **License:** Apache-2.0  
**Language:** Python | **Platform:** Cross-platform  
**Local-First:** YES | **Active:** YES

---

### WHAT MAKES IT THEM?

**The Core Magic:** Aider is the **git-native coding agent** — every change it makes is automatically committed with a descriptive message. This turns AI-assisted work into a reviewable, revertable Git history rather than an opaque blob.

**The specific interaction pattern:**
```
User: "Add rate limiting to the auth endpoints"
↓
Aider proposes changes as a diff
↓
User approves (or auto-approve)
↓
Aider applies changes
↓
Aider commits: "feat: Add rate limiting middleware to auth routes"
↓
Git history shows: 
  a3f1c2d feat: Add input validation to registration form
  b7e4a1f refactor: Extract email parsing into utility module
  c9d2e3a fix: Handle null case in user profile serialization
```

**What makes it special:**
1. **Atomic commits** — Every change is its own commit, fully revertable
2. **Repository map** — Builds a map of your codebase for better LLM context
3. **Architect/Editor dual-model** — Strong model plans, fast/cheap model emits diffs
4. **39 slash commands** — Deep terminal integration
5. **Multi-model support** — Works with any LLM, including local models

**The specific thing you'd lose if it disappeared:**
The **commit-per-change discipline**. This is the key to maintaining project history with AI agents — without it, you have no audit trail, no easy revert, no reviewable history.

---

### EXTRACTABLE VALUE

**Copy directly (concept):**
- Git commit-per-change discipline
- Repository map for LLM context
- Architect/Editor dual-model pattern
- /undo, /diff slash commands

**Adapt:**
- LLM-agnostic edit format
- File change tracking

**Avoid:**
- Full IDE replacement (BRAVO-1 is operator, not editor)
- Complex git operations for simple use cases

**Best for:**
- ✅ Git-native workflow patterns
- ✅ LLM context optimization
- ✅ Atomic commit discipline
- ❌ Primary operator interface

---

### FIT FOR BRAVO-1: 7/10

**Study for patterns, don't copy wholesale.** Aider's git-native approach is valuable, but BRAVO-1 is an operator shell, not a coding agent.

**Key insight:** The architect/editor dual-model pattern could apply to BRAVO-1's operator loop — a reasoning model for planning, a fast model for execution.

---

## REPO #6: Open Second Brain
**GitHub:** https://github.com/itechmeat/open-second-brain  
**Stars:** 113 | **Forks:** 6 | **License:** MIT  
**Language:** TypeScript (Bun) | **Platform:** Cross-platform  
**Local-First:** YES | **Active:** YES (146 commits, recent)

---

### WHAT MAKES IT THEM?

**The Core Magic:** Open Second Brain is the **Obsidian vault integration for AI agents** — it gives any AI agent persistent memory that lives in your Obsidian vault, with session summaries, preference tracking, and project context.

**The specific technical insight:**
```
Agent session starts
  → Read Brain/active.md (current context)
  → Inject into system prompt
  → Agent works
  → Session ends
  → Extract: request, decisions, learnings, next_steps
  → Write session summary to vault
  → Update active.md with next steps
  → Nightly dream pass: turn repeat corrections into confirmed preferences
```

**What makes it special:**
1. **Brain/active.md pattern** — Always-on context injection
2. **Session summaries** — Four-category digest (request, decisions, learnings, next_steps)
3. **Preference tracking** — Nightly dream pass turns corrections into confidence-rated preferences
4. **Multi-agent adapter** — Hermes, Claude Code, Codex, OpenClaw all supported
5. **TypeScript on Bun** — Fast, modern runtime

**The specific thing you'd lose if it disappeared:**
The **vault-structured memory with session lifecycle**. This turns a stateless chatbot into a persistent memory system that survives restarts and compounds knowledge over time.

---

### EXTRACTABLE VALUE

**Copy directly (concept):**
- Vault structure and organization
- Session summary format (4-category)
- Brain/active.md injection pattern
- Preference confidence scoring
- Multi-agent adapter pattern

**Adapt:**
- Nightly dream pass algorithm
- Event log for continuity
- Self-heal mechanisms for index corruption

**Avoid:**
- Heavy Bun dependency (could use Python if needed)
- Complex reindex swap logic (simplify for BRAVO-1)

**Best for:**
- ✅ Obsidian memory integration
- ✅ Session continuity
- ✅ Preference tracking
- ✅ Project context management
- ❌ Complex multi-user scenarios

---

### COMMIT HISTORY FINDINGS

**Momentum:** ACTIVE
- 146 commits
- Latest commit: 12 hours ago
- TypeScript rewrite (v0.7.0) in May 2026

**Commit cadence:** Recent bursty development
- v0.7.0 TypeScript rewrite
- Brain hardening fixes (1.24.0)
- Security fixes (event_log validation, identity blacklist)

**Signals of serious engineering:**
- Security hardening (date traversal rejection, identity blacklist)
- Self-heal mechanisms for data corruption
- Integration testing (176 bun test cases)
- CI validation (OpenClaw bundle diff check)

**Verdict:** Active, security-conscious project with recent architectural improvement.

---

### FIT FOR BRAVO-1: 8/10

**This is your BRAIN implementation.** You've already chosen Obsidian — Open Second Brain is the implementation.

**Key insight:** The nightly dream pass for continuous improvement directly maps to your "evolve like Hermes" goal.

---

## REPO #7: Work Buddy
**GitHub:** https://github.com/KadenMc/work-buddy  
**Stars:** 3 | **Forks:** N/A | **License:** MIT  
**Language:** Python | **Platform:** Windows + cross-platform  
**Local-First:** YES | **Active:** RECENT (July 2026)

---

### WHAT MAKES IT THEM?

**The Core Magic:** Work Buddy is a **personal agent framework built on Claude Code and Obsidian** — it shows how to deeply integrate an AI agent with project memory, workflow automation, and cross-tool coordination.

**What it demonstrates:**
1. **Deep Obsidian integration** — Not just file I/O, but native plugin access (Tasks, Day Planner, Tag Wrangler, Smart Connections, Datacore)
2. **Hindsight memory** — Persistent memory across sessions with semantic search
3. **Telegram bot** — Mobile command center for consent approval and workflow triggering
4. **Chrome extension** — Tab export with semantic clustering
5. **MCP gateway** — 4 tools with dynamic discovery

**The specific thing you'd lose if it disappeared:**
The **integration architecture** — how to connect Claude Code (agent) with Obsidian (memory) with external tools (Telegram, Chrome) into a coherent system.

---

### EXTRACTABLE VALUE

**Copy directly (concept):**
- MCP gateway pattern
- Deep Obsidian plugin integration
- Semantic memory search
- Mobile command center (Telegram)

**Adapt:**
- Telegram → WhatsApp (your primary channel)
- Claude Code → BRAVO-1 operator loop

**Avoid:**
- Heavy Claude Code dependency
- Complex multi-user features

**Best for:**
- ✅ Integration patterns
- ✅ MCP gateway design
- ✅ Memory system architecture
- ❌ Primary implementation (too Claude Code coupled)

---

### FIT FOR BRAVO-1: 6/10

**Study for patterns, not copy.** The integration architecture is valuable, but the Claude Code coupling is too tight.

**Key insight:** The Telegram → WhatsApp swap is straightforward. The MCP gateway pattern is worth stealing.

---

## REPO #8: llama.cpp
**GitHub:** https://github.com/ggml-org/llama.cpp  
**Stars:** 56k | **Forks:** 10k | **License:** MIT  
**Language:** C/C++ | **Platform:** Cross-platform  
**Local-First:** YES | **Active:** YES

---

### WHAT MAKES IT THEM?

**The Core Magic:** llama.cpp is the **de facto standard for local LLM inference** — it's what makes GGUF models run efficiently on CPU (and GPU with CUDA offload), with an OpenAI-compatible API server.

**What it provides:**
1. **GGUF format** — The standard for quantized model files
2. **llama-server** — OpenAI-compatible HTTP API
3. **CUDA/Metal/CPU offload** — Optimized for your hardware
4. **Function calling** — JSON schema-based tool use
5. **Multi-model serving** — Route requests by model name

**The specific thing you'd lose if it disappeared:**
The **runtime foundation** — without llama.cpp, there's no efficient way to run GGUF models locally. Qwen 2.5 3B and 7B on your GTX 1050 Ti only works because of llama.cpp.

---

### EXTRACTABLE VALUE

**Copy directly (concept):**
- llama-server for OpenAI-compatible API
- GGUF model loading and serving
- CUDA offload configuration
- Function calling schema support

**Avoid:**
- Custom quantization (use pre-built GGUF files)
- Complex multi-model routing (simple alias就够了)

**Best for:**
- ✅ Local model runtime
- ✅ OpenAI-compatible API
- ✅ Multi-model serving
- ❌ Training or fine-tuning

---

### FIT FOR BRAVO-1: 10/10

**This is your MODEL RUNTIME.** You've already been using Qwen 2.5 3B and 7B with GGUF — llama.cpp is the engine.

**Key configuration for your hardware:**
```
llama-server \
  -m models/qwen3-3b-q4_k_m.gguf \
  --ctx-size 4096 \
  --n-gpu-layers 20 \  # 4GB VRAM = ~20 layers
  --n-threads 8 \      # i7 7700HQ = 8 threads
  --parallel 4         # Modest parallelism
```

---

## REPO #9: FunASR
**GitHub:** https://github.com/modelscope/FunASR  
**Stars:** 12k | **Forks:** 1.5k | **License:** Apache-2.0  
**Language:** Python | **Platform:** Cross-platform  
**Local-First:** YES | **Active:** YES

---

### WHAT MAKES IT THEM?

**The Core Magic:** FunASR is the **industrial-grade speech recognition toolkit** — it provides multiple models (Paraformer, SenseVoice, Fun-ASR-Nano) with VAD built-in, running faster on CPU than Whisper on GPU.

**What it provides:**
1. **Paraformer** — Low-latency streaming ASR
2. **SenseVoice** — CPU-friendly with emotion and audio event detection
3. **Fun-ASR-Nano** — Flagship LLM-ASR model, 340x realtime with vLLM
4. **VAD built-in** — Voice activity detection integrated
5. **llama.cpp runtime** — Run ASR models as single self-contained binary

**The specific thing you'd lose if it disappeared:**
The **CPU-efficient ASR option** — FunASR runs faster on CPU than Whisper, which matters for your modest hardware.

---

### EXTRACTABLE VALUE

**Copy directly (concept):**
- Fun-ASR-Nano for local STT
- VAD integration
- llama.cpp runtime for edge deployment

**Avoid:**
- Complex vLLM integration (overkill for simple STT)
- Heavy Fun-ASR-Nano model (use smaller models for STT)

**Best for:**
- ✅ Local speech recognition
- ✅ VAD for voice activation
- ✅ CPU-efficient ASR
- ❌ Heavy LLM tasks (use Qwen for that)

---

### FIT FOR BRAVO-1: 8/10

**Alternative to faster-whisper for local STT.** FunASR's SenseVoice model is CPU-friendly and includes emotion detection.

**Key advantage:** llama.cpp runtime means no Python dependency at inference time — could compile to binary.

---

## REPO #10: DeepFace
**GitHub:** https://github.com/serengil/deepface  
**Stars:** 23k | **Forks:** 2k | **License:** MIT  
**Language:** Python | **Platform:** Cross-platform  
**Local-First:** YES | **Active:** YES

---

### WHAT MAKES IT THEM?

**The Core Magic:** DeepFace is the **lightweight face recognition library** — with a few lines of code, you can verify faces, find faces in a database, or analyze facial attributes.

**What it provides:**
1. **Face verification** — `DeepFace.verify(img1, img2)` returns verified: True/False
2. **Face recognition** — `DeepFace.find(img, db_path)` searches a database
3. **Facial attribute analysis** — Age, gender, emotion, race
4. **Multiple backends** — VGG-Face, Facenet, ArcFace, DeepFace, OpenFace
5. **RetinaFace detection** — High-quality face detection

**The specific thing you'd lose if it disappeared:**
The **simplest path to face verification** — DeepFace.verify() is literally 2 lines of code for production-quality face matching.

---

### EXTRACTABLE VALUE

**Copy directly (concept):**
- Face verification for security (camera check)
- ArcFace embeddings for comparison
- Webcam capture integration

**Adapt:**
- Store embeddings for known user
- Verify on camera activation
- Confidence threshold tuning

**Avoid:**
- Heavy emotion analysis (not needed for security)
- Large database face search (single user = simple)

**Best for:**
- ✅ Camera-based identity verification
- ✅ Simple face matching
- ✅ CPU-friendly implementation
- ❌ Liveness detection (need additional anti-spoofing)

---

### FIT FOR BRAVO-1: 7/10

**Critical for your security requirement.** Camera verification that "it's me or someone else" maps directly to DeepFace verification.

**Implementation plan:**
```python
from deepface import DeepFace
import cv2

# Capture frame
camera = cv2.VideoCapture(0)
ret, frame = camera.read()

# Verify against stored reference
result = DeepFace.verify(frame, "my_reference.jpg", model_name="ArcFace")
if result["verified"]:
    # It's me - continue operation
else:
    # Unknown person - lock down, alert via WhatsApp
```

---

## SUMMARY SCORING TABLE

| Repo | UI/UX | Operator Feel | Speed Value | Browser Strategy | Project Continuity | Tool Execution | Local-First | Architecture | Maintainability | Commit Health | Extractable Value | BRAVO-1 Fit | Label |
|------|-------|---------------|-------------|------------------|-------------------|----------------|-------------|--------------|-----------------|---------------|-------------------|-------------|-------|
| Hermes Agent | 8 | 10 | 10 | 7 | 10 | 9 | 10 | 9 | 10 | 10 | 10 | 10 | **STEAL NOW** |
| Browser Use | 7 | 8 | 9 | 10 | 6 | 8 | 9 | 9 | 8 | 9 | 9 | 9 | **STEAL NOW** |
| Open Interpreter | 6 | 8 | 8 | 8 | 5 | 10 | 8 | 8 | 7 | 8 | 8 | 9 | **STEAL NOW** |
| Windows-Use | 7 | 9 | 8 | 9 | 5 | 10 | 10 | 8 | 7 | 7 | 9 | 9 | **STEAL NOW** |
| Aider | 6 | 9 | 9 | 3 | 7 | 8 | 10 | 9 | 9 | 9 | 7 | 7 | **STUDY ONLY** |
| Open Second Brain | 8 | 9 | 8 | 2 | 10 | 6 | 10 | 9 | 8 | 8 | 8 | 8 | **STEAL NOW** |
| Work Buddy | 7 | 8 | 6 | 5 | 10 | 5 | 9 | 7 | 6 | 5 | 6 | 6 | **STUDY ONLY** |
| llama.cpp | 3 | 5 | 10 | 2 | 2 | 8 | 10 | 10 | 10 | 10 | 10 | 10 | **STEAL NOW** |
| FunASR | 5 | 6 | 9 | 2 | 2 | 9 | 10 | 8 | 8 | 8 | 8 | 8 | **STEAL NOW** |
| DeepFace | 5 | 5 | 8 | 1 | 2 | 7 | 10 | 7 | 8 | 7 | 7 | 7 | **STEAL NOW** |

---

## RISKS SUMMARY

| Repo | Key Risk | Mitigation |
|------|----------|------------|
| Hermes Agent | Heavy Python dependencies | Take session/operator patterns, build own lightweight implementation |
| Browser Use | Playwright complexity | Extract DOM extraction only, build own agent loop |
| Open Interpreter | Bazel build system | Use as reference for code execution, implement simply |
| Windows-Use | UIA not universal | Fallback to screenshot when UIA unavailable |
| Open Second Brain | Bun dependency | Could translate to Python or use Hermes memory directly |
| llama.cpp | GPU memory limits | Careful layer offload (20 layers for 4GB) |
| FunASR | Model size | Use small models (SenseVoice small) |
| DeepFace | Liveness detection | Implement simple anti-spoofing (blink detection) |