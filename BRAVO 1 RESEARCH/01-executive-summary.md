# BRAVO-1 — Executive Research Summary

**Project:** Local-first autonomous executive operator shell  
**Research Date:** 2026-07-07  
**Hardware Target:** GTX 1050 Ti 4GB + 8GB DDR4 + i7 7700HQ (Windows)

---

## TOP 10 REPOS TO STUDY

| # | Repo | Stars | Category | Why Study |
|---|------|-------|----------|-----------|
| 1 | **Hermes Agent** (NousResearch/hermes-agent) | 211k | CLI/Chat Operator | Multi-channel (WhatsApp, Telegram, Discord), voice mode, session continuity, skills hub, proactive agent loop |
| 2 | **Browser Use** (browser-use/browser-use) | 103k | Browser Automation | LLM-native browser control, real browser session management, accessibility tree parsing, headful/headless modes |
| 3 | **Open Interpreter** (openinterpreter/open-interpreter) | 64k | Code Execution + OS Control | Executes code on real machine, OS mode for GUI control, harness system (Claude Code, native, etc.) |
| 4 | **Windows-Use** (CursorTouch/Windows-Use) | 968 | Windows GUI Automation | UIA-based Windows control, screenshot + UIA hybrid, multi-provider LLM support, built on Windows-MCP |
| 5 | **Aider** (paul-gauthier/aider) | 47k | Terminal Coding Agent | Git-native workflow, architect/editor dual-model pattern, repository map, automatic commits |
| 6 | **Open Second Brain** (itechmeat/open-second-brain) | 113 | Memory/Project Continuity | Obsidian vault integration, session summaries, preference tracking, adapter for Hermes/Claude/Codex |
| 7 | **Work Buddy** (KadenMc/work-buddy) | 3 | Obsidian + Claude Integration | Deep vault access via plugin, Hindsight memory, Telegram bot, Chrome extension, MCP gateway |
| 8 | **llama.cpp** (ggml-org/llama.cpp) | 56k | Local Model Runtime | GGUF format, OpenAI-compatible server, multi-model support, CUDA/CPU offload, function calling |
| 9 | **FunASR** (modelscope/FunASR) | 12k | Speech Recognition | Paraformer/SenseVoice models, CPU-efficient, VAD built-in, llama.cpp runtime for edge deployment |
| 10 | **DeepFace** (serengil/deepface) | 23k | Face Recognition | Lightweight face verification, ArcFace/VGG-Face models, CPU-friendly, webcam integration |

---

## TOP 5 MOST RELEVANT REPOS

### 1. Hermes Agent — THE OPERATOR BACKBONE
**Why #1:** Every single core promise of BRAVO-1 maps to something Hermes does:
- Proactive agent loop with next-action intelligence ✅
- Multi-channel messaging (WhatsApp primary for you) ✅
- Voice mode with faster-whisper local STT ✅
- Skills hub for extensibility ✅
- Session continuity and memory ✅
- Local-first with zero cloud dependency ✅

**Verdict:** Steal the agent loop architecture, message routing, session management, skills system, and voice pipeline.

### 2. Browser Use — REAL BROWSER CONTROL
**Why #2:** Your hardware can't run vision models fast enough, but Browser Use uses DOM accessibility trees — which are TEXT and fast. This means a 3B Qwen model can drive a real browser.

**Key insight:** Browser Use achieves 83.3% on WebVoyager using DOM parsing, NOT screenshots. This is perfect for your 1050 Ti setup.

**Verdict:** Steal the browser session management, accessibility tree extraction, and the LLM-loop that interprets it.

### 3. Open Interpreter — REAL MACHINE EXECUTION
**Why #3:** You want no sandboxing, full system access. Open Interpreter is built exactly for this — it executes code on your real machine with confirmation prompts.

**Key insight:** Their "harness" system lets you swap between Claude Code harness, native harness, etc. This is a pattern BRAVO-1 needs for tool execution.

**Verdict:** Steal the tool execution framework, harness system, and the OS mode architecture.

### 4. Windows-Use — WINDOWS GUI NATIVE
**Why #4:** This is the ONLY open-source repo that directly controls Windows at the GUI layer using UIA (not screenshots). It's what your "control my computer BY ITS OWN SELF" vision needs.

**Key insight:** Uses MS UI Automation API — which means control over any Windows app without coordinate-based clicking. Works with your GTX 1050 Ti because it's all text-based reasoning.

**Verdict:** Steal the UIA-based Windows control layer, the tool set (click, type, scroll, app control, shell), and the Windows-native integration.

### 5. Open Second Brain — PROJECT MEMORY
**Why #5:** You've already decided on Obsidian for the "brain." Open Second Brain is THE implementation of Hermes + Obsidian together. It handles session summaries, preference tracking, project context, and vault management.

**Key insight:** The nightly dream pass that turns repeat corrections into confirmed preferences with confidence scores — this is the "continuous improvement" loop you want.

**Verdict:** Steal the vault structure, session-handoff pattern, and the brain feedback loop.

---

## TOP 3 REPOS WITH STRONGEST "CORE MAGIC"

### 🔮 Magic #1: Hermes Agent — "The Session-is-Everything Loop"
**What makes it magic:** Hermes treats EVERYTHING as a session — CLI sessions, WhatsApp sessions, Telegram sessions, subagent sessions. Each session has memory, context, tools, and continuity. The magic is in how it handles session handoff: when you close the CLI and reopen it, it has your project context, active work, and recent decisions.

**The specific thing you'd lose:** The `Brain/active.md` pattern where the agent injects current context into every turn. Without this, you have generic chat. With it, you have a chief-of-staff.

**Extractable pattern:** Session lifecycle management → Context injection at turn boundaries → Handoff documentation → Multi-channel session isolation with shared memory.

### 🔮 Magic #2: Browser Use — "DOM as Language"
**What makes it magic:** Instead of treating the browser as a visual canvas (requiring vision models), Browser Use converts the DOM into a structured text format that any LLM can reason about. The agent sees: `[button] Submit [/button]`, `[input] Email address [/input]` — and can interact with them directly.

**The specific thing you'd lose:** The accessibility tree → element reference mapping. Without it, the agent sees screenshots and guesses. With it, the agent sees actionable UI elements.

**Extractable pattern:** Browser session management → DOM-to-element extraction → Action schema generation → Screenshot fallback for verification.

### 🔮 Magic #3: Windows-Use — "UIA as the Universal Interface"
**What makes it magic:** Windows-Use uses Microsoft UI Automation (UIA) to inspect every Windows control — buttons, text fields, menus, dialogs — and exposes them as structured data. This means: no OCR, no screenshot analysis, no coordinate guessing. Just direct control.

**The specific thing you'd lose:** The ability to interact with ANY Windows app reliably. Without UIA, you're doing coordinate-based automation that breaks constantly.

**Extractable pattern:** UIA element tree extraction → Action planning → Execution with verification → Fallback to screenshot when needed.

---

## TOP 3 DANGEROUS DISTRACTIONS

### ⚠️ Distraction #1: OpenHands (76k stars)
**Why dangerous:** OpenHands is enterprise-grade — sandboxed Docker execution, RBAC, multi-user support, Jira/Linear/Slack integrations. It does EVERYTHING but nothing simply. For a solo power user on a 1050 Ti, it's over-engineered and requires significant infrastructure.

**Anti-pattern to avoid:** Don't build multi-team orchestration when you're building a personal operator.

### ⚠️ Distraction #2: UI-TARS (Alibaba)
**Why dangerous:** UI-TARS requires 16GB+ VRAM for the 7B model. Your 4GB GTX 1050 Ti can't run it. Even if you had the hardware, it's a specialized model, not a general operator.

**Anti-pattern to avoid:** Don't chase specialized fine-tuned models when general models work fine with good tool design.

### ⚠️ Distraction #3: BrowserOS (browseros-ai/BrowserOS)
**Why dangerous:** BrowserOS is a full Chromium fork with a Go/Bun agent platform. It's a browser OS, not an operator shell. Building on it means your product IS a browser, not that your product HAS browser capability.

**Anti-pattern to avoid:** Don't build around browser infrastructure when you just need browser integration.

---

## SCORING MATRIX

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

## FINAL VERDICT

**Steal Now (7 repos):**
1. Hermes Agent — operator loop, session management, multi-channel, voice, skills
2. Browser Use — browser automation architecture, DOM extraction, session management
3. Open Interpreter — code execution harness, OS mode, tool framework
4. Windows-Use — Windows GUI control, UIA integration, tool set
5. Open Second Brain — Obsidian brain, session summaries, preference tracking
6. llama.cpp — GGUF runtime, OpenAI-compatible server, model orchestration
7. FunASR — speech recognition, VAD, local STT pipeline

**Study Only (2 repos):**
- Aider — git-native workflow patterns, architect/editor dual-model pattern
- Work Buddy — deep Obsidian integration patterns, MCP gateway

**Avoid (1 repo):**
- OpenHands — over-engineered for solo power user use case

---

## THE SYNTHESIS MISSION

BRAVO-1 needs to combine:
- **Hermes Agent's** operator brain + session management + multi-channel
- **Browser Use's** real browser control using DOM (not vision)
- **Windows-Use's** Windows GUI control using UIA
- **Open Interpreter's** tool execution framework
- **Open Second Brain's** Obsidian memory brain
- **llama.cpp's** GGUF runtime for your 3B/7B Qwen models
- **FunASR's** speech recognition pipeline
- **DeepFace's** face verification for security

The result: An autonomous operator that sees your screen, hears your voice, knows your projects, controls your Windows machine, browses the web, and notifies you via WhatsApp — all running locally on your modest hardware.