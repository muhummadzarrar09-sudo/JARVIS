# BRAVO-1 — Recommended Starting Stack

---

## STACK OVERVIEW

Given your hardware (GTX 1050 Ti 4GB + 8GB DDR4 + i7 7700HQ) and constraints (Windows-only, local-first, no cloud), here's the recommended technology stack.

---

## 1. UI SHELL APPROACH

### Recommendation: Terminal TUI → Web UI (later)

**Phase 1 (MVP):** Simple terminal interface
```
Why: Fast to build, works everywhere, minimal dependencies
Tools: Rich (Python TUI library) or Textual
```

**Phase 2+:** Web interface
```
Why: Better UX, accessible from phone, more polished
Tools: FastAPI backend + vanilla HTML/CSS or React
```

**NOT:** Electron/Tauri desktop app (too heavy for MVP)

### Implementation: Chat UI Pattern
```python
# MVP: Simple streaming terminal
from rich.console import Console
from rich.markdown import Markdown

console = Console()

async def chat_loop():
    while True:
        user_input = await get_input()  # voice or text
        
        # Stream response
        with console.status("[bold green]Thinking..."):
            async for chunk in operator.process(user_input):
                console.print(chunk, end="")
        
        console.print()  # Newline after response
```

---

## 2. BACKEND ARCHITECTURE

### Recommendation: Python FastAPI + SQLite

**Why:**
- Hermes Agent is Python — easy to integrate patterns
- FastAPI is lightweight, async, well-supported
- SQLite is local, zero-config, sufficient for session storage

**NOT:** Django (too heavy), PostgreSQL (requires setup)

### Structure
```
bravo-1/
├── core/
│   ├── operator.py         # Main agent loop
│   ├── session.py          # Session management
│   ├── memory.py           # Memory/brain system
│   └── tools.py            # Tool registry
├── adapters/
│   ├── browser.py          # Browser automation
│   ├── windows.py          # Windows UIA control
│   ├── execution.py        # Code execution
│   └── voice.py            # STT/TTS
├── channels/
│   ├── cli.py              # Terminal interface
│   ├── whatsapp.py         # WhatsApp webhook
│   └── web.py              # Web UI
├── brain/
│   └── vault/              # Obsidian vault
└── models/
    └── runtime.py          # llama.cpp server
```

---

## 3. ORCHESTRATION STRUCTURE

### Recommendation: Event-Driven with Session Context

**Core Loop:**
```python
class Operator:
    def __init__(self):
        self.session_manager = SessionManager()
        self.tool_registry = ToolRegistry()
        self.memory = ObsidianBrain()
        
    async def process(self, input: Input) -> Response:
        # 1. Verify security (face + voice)
        if not await self.security.verify(input):
            return Response("Identity not verified.")
        
        # 2. Get session context
        context = await self.session_manager.get_context()
        
        # 3. Inject memory
        context = await self.memory.inject(context)
        
        # 4. Reason + plan
        plan = await self.reason(input, context)
        
        # 5. Execute tools
        result = await self.execute(plan)
        
        # 6. Update memory
        await self.memory.update(result)
        
        # 7. Return response
        return self.format(result)
```

---

## 4. BROWSER ARCHITECTURE

### Recommendation: Browser Use DOM Extraction + Custom Agent

**Why:** DOM-based (not vision) = works with Qwen 3B on GTX 1050 Ti

**Implementation:**
```python
class BrowserAdapter:
    def __init__(self):
        self.playwright = Playwright()
        self.context = None
        
    async def launch(self, headful: bool = False):
        """Launch browser with persistent profile"""
        self.context = await self.playwright.launch_persistent_context(
            headless=not headful,
            storage_state="browser_state.json"
        )
        
    async def get_page_context(self) -> PageContext:
        """Extract DOM as structured text for LLM"""
        dom = await self.context.evaluate("""
            () => {
                // Extract element tree with refs
            }
        """)
        return PageContext(dom=dom)
        
    async def act(self, element_ref: str, action: str, **kwargs):
        """Execute action on element by reference"""
        # Map element_ref to selector
        # Execute action (click, type, scroll)
        # Return result
```

**Fallback:** Screenshot + Qwen VL when DOM extraction fails

---

## 5. PROJECT CONTINUITY STRUCTURE

### Recommendation: Obsidian Vault + SQLite Index

**Why:** You've already decided on Obsidian. Open Second Brain pattern.

**Vault Structure:**
```
vault/
├── brain/
│   ├── active.md           # Injected into every turn
│   ├── sessions/           # Session summaries
│   │   └── YYYYMMDD_HHMMSS.md
│   ├── decisions/          # Decision log
│   │   └── YYYYMMDD_decision.md
│   └── preferences/        # With confidence scores
│       ├── confidence_0.8/
│       └── confidence_0.3/
├── projects/
│   └── resume-builder/
│       ├── context.md
│       ├── TODO.md
│       └── architecture/
└── memory/
    └── search_index.db     # SQLite FTS
```

**Session Summary Format:**
```markdown
---
title: Session 20260707_143200
date: 2026-07-07T14:32:00
type: session-summary
project: resume-builder
---

## Request
User asked to build skills section

## Decisions
- Use React for frontend
- Deploy to Vercel
- Use specific color scheme

## Learnings
- User prefers concise bullet points
- Project uses TypeScript

## Next Steps
1. Create React project structure
2. Document CLI automation work
3. Update education timeline
```

---

## 6. MODEL/RUNTIME STRUCTURE

### Recommendation: llama-server + Qwen 2.5 GGUF

**Hardware-aware configuration:**
```bash
# GTX 1050 Ti 4GB VRAM, 8GB RAM, 8 threads

llama-server \
  --model models/qwen3-3b-q4_k_m.gguf \
  --ctx-size 4096 \
  --n-gpu-layers 20 \
  --n-threads 8 \
  --n-batch 256 \
  --parallel 4 \
  --port 8080
```

**Dual model setup:**
```bash
# Fast model (3B) for quick tasks
llama-server --model qwen3-3b-q4_k_m.gguf --port 8080

# Capable model (7B) for complex tasks  
llama-server --model qwen3-7b-q4_k_m.gguf --port 8081
```

**Routing:**
```python
async def get_model(task_type: str):
    if task_type in ["quick", "tool_call", "simple"]:
        return "http://localhost:8080/v1/chat/completions"
    else:
        return "http://localhost:8081/v1/chat/completions"
```

---

## 7. PACKAGING DIRECTION

### Recommendation: Python package + installer script

**Phase 1:** Python package with setup.py
```
bravo-1/
├── bravo1/
│   ├── __init__.py
│   ├── core/
│   ├── adapters/
│   └── ...
├── setup.py
├── requirements.txt
└── README.md

pip install -e .
bravo-1 start
```

**Phase 2:** Windows installer (NSIS or WiX)
```
bravo-1-setup.exe
├── Install Python if needed
├── Download models
├── Create shortcuts
└── Register autostart
```

**NOT:** Electron/Tauri (too heavy), Docker (unnecessary complexity)

---

## 8. SPEECH/VOICE STRUCTURE

### Recommendation: FunASR (Paraformer) + Kokoro TTS

**Why:**
- FunASR runs faster on CPU than Whisper
- Kokoro is open-source, high quality
- Both are local, no API costs

**STT Pipeline:**
```python
class VoiceInput:
    def __init__(self):
        self.vad = SileroVAD()  # Lightweight VAD
        self.asr = FunASR(model="paraformer")
        
    async def listen(self):
        # 1. Detect speech with VAD
        audio_chunk = await self.vad.detect()
        
        # 2. Transcribe with FunASR
        text = await self.asr.transcribe(audio_chunk)
        
        return text
```

**TTS Pipeline:**
```python
class VoiceOutput:
    def __init__(self):
        self.tts = KokoroTTS()
        
    async def speak(self, text: str):
        audio = await self.tts.synthesize(text)
        await self.play_audio(audio)
```

---

## 9. SECURITY/CAMERA STRUCTURE

### Recommendation: DeepFace ArcFace + simple anti-spoofing

**Enrollment:**
```python
class SecurityVerifier:
    def enroll(self, reference_image_path: str):
        embedding = DeepFace.represent(
            reference_image_path,
            model_name="ArcFace"
        )
        self.store_embedding(embedding)
```

**Verification:**
```python
    def verify(self, frame) -> bool:
        embedding = DeepFace.represent(frame, model_name="ArcFace")
        distance = cosine_distance(
            embedding,
            self.stored_embedding
        )
        # Threshold ~0.4 for ArcFace
        return distance < 0.4
```

**Anti-spoofing (simple):**
```python
def check_liveness(frame1, frame2):
    # Simple blink detection
    # Two frames, 200ms apart
    # If eyes closed→open→closed in sequence = blink = real
```

---

## 10. WINDOWS CONTROL STRUCTURE

### Recommendation: Windows-Use UIA + PyAutoGUI fallback

**Primary: UIA-based**
```python
class WindowsControl:
    def get_elements(self) -> list[UIAElement]:
        # Use pywinauto UIA backend
        tree = self.app.connect(handle=self.hwnd)
        return tree.descendants()
        
    def click(self, element_name: str):
        # Find element by name
        # Click via UIA (no coordinates)
```

**Fallback: PyAutoGUI**
```python
    def click_coordinates(self, x: int, y: int):
        # Only when UIA unavailable
        pyautogui.click(x, y)
```

---

## COMPLETE STACK SUMMARY

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| Language | Python 3.11+ | - |
| Web Framework | FastAPI | - |
| Database | SQLite | - |
| UI | Terminal TUI (Rich/Textual) | Web (later) |
| Model Runtime | llama.cpp (llama-server) | - |
| Models | Qwen 2.5 3B + 7B GGUF | - |
| Browser | Playwright + Browser Use DOM | - |
| Windows Control | pywinauto UIA + Windows-Use | PyAutoGUI |
| Speech STT | FunASR (Paraformer) | faster-whisper |
| Speech TTS | Kokoro | Edge TTS |
| Face Verification | DeepFace (ArcFace) | - |
| Memory | Obsidian vault + SQLite FTS | - |
| Messaging | WhatsApp Cloud API | - |
| Packaging | pip + installer script | - |

---

## INSTALLATION ORDER

```bash
# 1. Core dependencies
pip install fastapi uvicorn rich textual
pip install llama-cpp-python[server]

# 2. Models
huggingface-cli download Qwen/Qwen2.5-3B-Instruct-GGUF qwen2.5-3b-q4_k_m.gguf
huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF qwen2.5-7b-q4_k_m.gguf

# 3. Browser automation
pip install playwright
playwright install chromium

# 4. Windows automation
pip install pywinauto pyautogui

# 5. Speech
pip install funasr kokoro

# 6. Face verification
pip install deepface

# 7. Start server
python -m bravo1.core.operator
```