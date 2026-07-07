# BRAVO-1 — Synthesis Plan

---

## THE SYNTHESIS MISSION

Combine the best parts of these repos into ONE superior local-first executive operator shell:

| Source | What to Steal | Why |
|--------|---------------|-----|
| Hermes Agent | Operator loop, session management, multi-channel, voice, skills | #1 operator feel |
| Browser Use | DOM-based browser automation, session persistence | Real browser control |
| Windows-Use | UIA-based Windows GUI control, tool set | Native Windows control |
| Open Interpreter | Code execution framework, harness system | Tool execution |
| Open Second Brain | Obsidian brain, session summaries, preferences | Persistent memory |
| llama.cpp | GGUF runtime, OpenAI-compatible API | Model orchestration |
| FunASR | Speech recognition, VAD | Voice input |
| DeepFace | Face verification | Security layer |

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│                           BRAVO-1                                    │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   Chat UI   │  │  Voice I/O  │  │   Camera    │  │  WhatsApp   │ │
│  │  (Claude-   │  │  (FunASR +  │  │  (DeepFace) │  │  (Webhook)  │ │
│  │   style)    │  │   Kokoro)   │  │             │  │             │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                │                │                │        │
│         └────────────────┼────────────────┼────────────────┘        │
│                          │                │                         │
│                    ┌─────▼─────┐    ┌─────▼─────┐                   │
│                    │  Security │    │   Input   │                   │
│                    │  Verifier │    │  Router   │                   │
│                    │ (Face +   │    │           │                   │
│                    │  Voice)   │    │           │                   │
│                    └─────┬─────┘    └─────┬─────┘                   │
│                          │                │                         │
│                    ┌─────▼────────────────▼─────┐                   │
│                    │      OPERATOR CORE         │                   │
│                    │  ┌─────────────────────┐   │                   │
│                    │  │  Session Manager    │   │                   │
│                    │  │  • Context injection│   │                   │
│                    │  │  • Memory update    │   │                   │
│                    │  │  • Handoff logic    │   │                   │
│                    │  └─────────────────────┘   │                   │
│                    │  ┌─────────────────────┐   │                   │
│                    │  │   Agent Loop        │   │                   │
│                    │  │  • Reasoning        │   │                   │
│                    │  │  • Tool planning    │   │                   │
│                    │  │  • Execution        │   │                   │
│                    │  └─────────────────────┘   │                   │
│                    │  ┌─────────────────────┐   │                   │
│                    │  │  Obsidian Brain     │   │                   │
│                    │  │  • active.md        │   │                   │
│                    │  │  • Session summaries│   │                   │
│                    │  │  • Preferences      │   │                   │
│                    │  └─────────────────────┘   │                   │
│                    └─────────────┬─────────────┘                   │
│                                  │                                 │
│         ┌────────────────────────┼────────────────────────┐        │
│         │                        │                        │        │
│    ┌────▼────┐            ┌─────▼─────┐           ┌─────▼─────┐   │
│    │ Browser │            │  Windows  │           │   Code    │   │
│    │  Use    │            │   UIA     │           │ Execution │   │
│    │         │            │  Control  │           │   (Shell) │   │
│    └────┬────┘            └─────┬─────┘           └─────┬─────┘   │
│         │                       │                       │         │
│         │            ┌──────────┴──────────┐            │         │
│         │            │                     │            │         │
│    ┌────▼────┐  ┌────▼────┐          ┌────▼────┐  ┌────▼────┐   │
│    │Playwright│  │  PyWinauto│          │  Shell  │  │  Git    │   │
│    │         │  │          │          │ Command │  │  Commit │   │
│    └─────────┘  └──────────┘          └─────────┘  └─────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    MODEL RUNTIME (llama.cpp)                    │ │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐                    │ │
│  │  │ Qwen 3B   │  │ Qwen 7B   │  │ Whisper   │  ← GGUF models    │ │
│  │  │ (fast)    │  │ (capable) │  │ (STT)     │                    │ │
│  │  └───────────┘  └───────────┘  └───────────┘                    │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## WHAT TO TAKE FROM WHERE

### FROM: Hermes Agent
**Take:** Session lifecycle management + context injection
```
bravo-1/
├── sessions/           # Session storage
│   ├── active.json     # Current session state
│   └── archive/        # Completed sessions
├── brain/
│   ├── active.md       # Injected into every turn
│   ├── sessions/       # Session summaries
│   └── decisions/      # Decision log
└── tools/
    └── *.md            # Skills
```

**Take:** Multi-channel routing
- WhatsApp webhook gateway
- CLI interface
- Session isolation per contact

**Take:** Voice pipeline
- faster-whisper STT (or FunASR)
- TTS with personality hints
- Push-to-talk mode

### FROM: Browser Use
**Take:** DOM extraction + element reference system
```python
class BrowserTool:
    def get_page_context(self) -> PageContext:
        """Returns structured DOM for LLM reasoning"""
        
    def execute_action(self, element_ref: str, action: str):
        """Execute on element by reference, not coordinates"""
```

**Take:** Session persistence
```python
class BrowserSession:
    def launch(headful: bool = False) -> BrowserSession:
        """Launch with profile for persistent auth"""
        
    def save_state(self):
        """Save cookies, localStorage for resume"""
        
    def restore_state(self):
        """Restore auth state after restart"""
```

### FROM: Windows-Use
**Take:** UIA element tree extraction
```python
class WindowsControl:
    def get_control_tree() -> ControlTree:
        """Get Windows UIA tree for LLM reasoning"""
        
    def execute(self, element: str, action: str):
        """Click, type, scroll, etc. by element name"""
```

**Take:** Tool set definition
- click_tool (left, right, middle, hover)
- type_tool (text input)
- scroll_tool (vertical, horizontal)
- move_tool (drag-drop)
- shortcut_tool (ctrl+c, alt+tab)
- app_tool (launch, switch, resize)
- shell_tool (PowerShell commands)
- wait_tool (pause)
- done_tool (finalize)

### FROM: Open Interpreter
**Take:** Code execution harness
```python
class ExecutionHarness:
    def plan(self, task: str) -> ExecutionPlan:
        """Generate code to execute"""
        
    def execute(self, plan: ExecutionPlan) -> Result:
        """Run code with confirmation"""
        
    def verify(self, result: Result) -> bool:
        """Verify execution succeeded"""
```

**Take:** Tool adapter interface
```python
class ToolAdapter(ABC):
    @abstractmethod
    def execute(self, tool: str, args: dict) -> ToolResult:
        pass
    
    @abstractmethod
    def validate(self, tool: str, args: dict) -> bool:
        pass
```

### FROM: Open Second Brain
**Take:** Vault structure
```
vault/
├── brain/
│   ├── active.md       # Current context
│   ├── sessions/       # Session summaries
│   ├── decisions/      # Decision log
│   └── preferences/    # With confidence scores
├── projects/
│   └── [project]/
│       ├── context.md
│       ├── TODO.md
│       └── architecture/
└── memory/
    └── [semantic search index]
```

**Take:** Session summary format
```markdown
---
title: Session YYYYMMDD_HHMMSS
type: session-summary
request:
decisions:
learnings:
next_steps:
---
```

**Take:** Nightly dream pass
```python
def nightly_dream():
    """Review corrections, elevate confidence"""
    corrections = get_corrections_24h()
    for pattern in corrections:
        if count_same_correction(pattern) >= 3:
            elevate_confidence(pattern)
```

### FROM: llama.cpp
**Take:** Model runtime configuration
```python
llama-server \
  --model models/qwen3-3b-q4_k_m.gguf \
  --ctx-size 4096 \
  --n-gpu-layers 20 \     # GTX 1050 Ti = ~20 layers
  --n-threads 8 \         # i7 7700HQ = 8 threads
  --parallel 4
```

**Take:** Function calling schema
```python
def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "browser_navigate",
                "description": "Navigate to URL in browser",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"}
                    }
                }
            }
        }
    ]
```

### FROM: FunASR
**Take:** VAD + streaming STT
```python
class VoiceInput:
    def __init__(self):
        self.vad = VoiceActivityDetector()
        self.asr = FunASR(model="paraformer")
        
    async def listen(self):
        audio = self.vad.detect()
        if audio.has_speech():
            text = await self.asr.transcribe(audio)
            return text
```

### FROM: DeepFace
**Take:** Face verification for security
```python
class SecurityVerifier:
    def __init__(self, reference_image):
        self.embedding = DeepFace.represent(reference_image)
        
    def verify(self, frame) -> bool:
        frame_embedding = DeepFace.represent(frame)
        distance = cosine_distance(self.embedding, frame_embedding)
        return distance < 0.4  # Threshold
```

---

## WHAT TO COMBINE

### Combination 1: Hermes + Open Second Brain = Operator Brain
**The combo:**
- Hermes's session management + operator loop
- Open Second Brain's vault structure + memory patterns

**Result:** An operator that remembers everything, resumes perfectly, and continuously improves.

### Combination 2: Browser Use + Windows-Use = Full Automation
**The combo:**
- Browser Use's DOM extraction for web
- Windows-Use's UIA extraction for desktop apps

**Result:** Universal automation — any web page, any Windows app, controlled by text-based reasoning.

### Combination 3: FunASR + DeepFace = Voice + Vision Security
**The combo:**
- FunASR for speech recognition
- DeepFace for face verification
- Kokoro/Spark-TTS for voice output

**Result:** Natural voice interaction with biometric security.

### Combination 4: llama.cpp + Open Interpreter = Local Tool Execution
**The combo:**
- llama.cpp for model serving
- Open Interpreter's code execution framework

**Result:** Local model that can execute real code on your real machine.

---

## WHAT TO REJECT

### Reject: OpenHands
**Why:** Enterprise-grade over-engineering. Multi-team features, Docker sandboxing, RBAC — all unnecessary for solo power user.

### Reject: UI-TARS
**Why:** Requires 16GB+ VRAM. Your 4GB GTX 1050 Ti can't run it. Also requires specialized model, not general-purpose.

### Reject: Cloud Firecrawl
**Why:** You're local-first. Self-host or use basic Playwright scraping.

### Reject: Heavy LangChain
**Why:** Browser Use uses LangChain, but we can extract just the DOM extraction + agent loop without the LangChain overhead.

### Reject: Enterprise multi-user features
**Why:** This is a SOLO power user tool. No multi-team, no RBAC, no audit trails across users.

---

## WHAT TO BUILD OURSELVES

### Build 1: Calm Chat UI
**Not from any repo:**
- Minimal, Claude-style chat interface
- Session info in compact header
- Tool progress as subtle indicators
- Streaming output

### Build 2: WhatsApp Integration
**From Hermes, but adapted:**
- Simple webhook server
- Per-contact session isolation
- Voice note transcription
- Text/TTS responses

### Build 3: Battery Monitor + Shutdown
**Custom:**
- Power loss detection
- State preservation
- WhatsApp notification
- Graceful shutdown

### Build 4: Proactive Loop
**Custom:**
- Monitor for tasks
- Surface work without prompting
- Weekly digest via WhatsApp
- Pattern learning from corrections

---

## IMPLEMENTATION ORDER

### Phase 1: Foundation (MVP)
```
1. llama.cpp server with Qwen 3B/7B GGUF
2. Simple chat UI (terminal or web)
3. Basic session management (context injection)
4. Shell command execution
5. Obsidian vault integration (active.md)
```

**Outcome:** Functional operator shell with memory and tool execution.

### Phase 2: Automation (Alpha)
```
6. Browser automation (Browser Use DOM extraction)
7. Windows control (Windows-Use UIA)
8. Code execution harness
9. Session summaries (Open Second Brain pattern)
```

**Outcome:** Can browse web and control Windows apps.

### Phase 3: Voice + Security (Beta)
```
10. FunASR speech recognition
11. DeepFace camera verification
12. Voice mode (push-to-talk)
13. WhatsApp integration
```

**Outcome:** Voice-controlled with biometric security.

### Phase 4: Proactive Intelligence
```
14. Proactive task monitoring
15. Preference learning (dream pass)
16. Battery shutdown with state preservation
17. Weekly digest
```

**Outcome:** True autonomous operator that evolves.

---

## CRITICAL DECISIONS

### Decision 1: UI Shell
**Options:**
- Terminal TUI (simple, fast)
- Web UI (more polished, requires server)
- Desktop app (best UX, most complex)

**Recommendation:** Start with terminal TUI, add web UI in later phase.

### Decision 2: Model Routing
**Options:**
- Qwen 3B for fast tasks
- Qwen 7B for complex tasks
- Both running simultaneously

**Recommendation:** Qwen 3B for most tasks, Qwen 7B for planning/complex reasoning.

### Decision 3: Browser Implementation
**Options:**
- Browser Use (DOM extraction, well-tested)
- Playwright MCP (simpler, more flexible)
- Custom (full control, more work)

**Recommendation:** Browser Use DOM extraction + custom agent loop.

### Decision 4: Windows Control Implementation
**Options:**
- Windows-Use (UIA-based, production-ready)
- PyAutoGUI (coordinate-based, simple)
- Custom (full control, more work)

**Recommendation:** Windows-Use UIA extraction + custom agent loop + PyAutoGUI fallback.