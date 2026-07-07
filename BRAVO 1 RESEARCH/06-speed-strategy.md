# BRAVO-1 — Speed Strategy

---

## THE PRINCIPLE: Move Fast on What Matters

Not all parts of BRAVO-1 are equal. Some parts give 10x product improvement with 1x effort. Others give 1x improvement with 10x effort.

**Goal:** Maximum product feel per unit of work.

---

## PHASE 1: MVP — Fastest Path to "Wow"

### What to Build First (Week 1-2)

**Priority 1: Basic Operator + Memory**
```
✅ llama-server with Qwen 3B
✅ Simple chat interface (terminal)
✅ Session context injection
✅ Obsidian vault integration (active.md)
✅ Basic shell command execution
```

**Why first:** This gives you the CORE FEEL — an operator that remembers, reasons, and executes. Everything else is enhancement.

**Effort:** ~2 weeks  
**Impact:** 80% of the "wow" factor

**Don't build yet:**
- Voice mode
- Camera verification
- WhatsApp integration
- Browser automation
- Windows control

### Why This Order?

The "chief-of-staff" feel comes from:
1. **Memory** — It knows your projects
2. **Context** — It resumes where you left off
3. **Execution** — It can actually do things

Voice, camera, WhatsApp are channels — important, but secondary to the core brain.

---

## PHASE 2: Alpha — Automation Power

### What to Build Next (Week 3-4)

**Priority 2: Browser + Windows Control**
```
✅ Browser DOM extraction (Browser Use pattern)
✅ Basic web navigation (go to URL, click, type)
✅ Windows UIA control (Windows-Use pattern)
✅ Persistent browser sessions
```

**Why second:** Your stated use case is "switching between tabs and building apps." Browser + Windows control is the automation layer that makes this real.

**Effort:** ~2 weeks  
**Impact:** Adds the "does things on my machine" power

**Don't build yet:**
- Multi-channel (WhatsApp only, CLI is fine for now)
- Voice mode
- Camera verification

### Technical Approach

**Browser:** Extract Browser Use's DOM parsing, build lighter agent loop
```python
class BrowserAgent:
    async def task(self, goal: str) -> Result:
        context = await self.browser.get_context()
        plan = await self.reason(goal, context)
        for step in plan:
            await self.browser.act(step)
            context = await self.browser.get_context()
        return result
```

**Windows:** Take Windows-Use's UIA tools directly
```python
# Direct copy of Windows-Use tool set
TOOLS = [
    "click",      # left, right, middle, hover
    "type",       # text input
    "scroll",     # vertical, horizontal
    "move",       # drag-drop
    "shortcut",   # ctrl+c, alt+tab
    "app",        # launch, switch, resize
    "shell",      # PowerShell
    "wait",       # pause
    "done",       # finalize
]
```

---

## PHASE 3: Beta — Voice + Security

### What to Build Third (Week 5-6)

**Priority 3: Voice Input + Camera Verification**
```
✅ FunASR speech recognition
✅ Push-to-talk voice mode
✅ DeepFace camera verification
✅ Simple TTS response
```

**Why third:** Voice + camera transform the UX from "chat tool" to "assistant." The camera verification also addresses your security concern.

**Effort:** ~2 weeks  
**Impact:** Adds the "feels like a person" factor

**Don't build yet:**
- WhatsApp integration (CLI voice is fine for MVP)
- Proactive monitoring
- Nightly dream pass

### Implementation Sequence

1. **STT first:** Get voice working with FunASR
2. **Camera second:** Verify "it's me" before activation
3. **TTS third:** Let it speak responses
4. **Security last:** Anti-spoofing, alerts

---

## PHASE 4: Polish — Communication

### What to Build Fourth (Week 7-8)

**Priority 4: WhatsApp + Proactive Features**
```
✅ WhatsApp webhook integration
✅ Battery shutdown with state preservation
✅ Session summaries auto-generated
✅ Weekly digest via WhatsApp
```

**Why fourth:** By now you have a working operator. WhatsApp just makes it accessible. Proactive features make it feel alive.

**Effort:** ~2 weeks  
**Impact:** Adds the "always available" factor

---

## VALIDATION FIRST

### Validate on Real Machine Immediately

**Don't:** Build in isolation, then test on target hardware.

**Do:** Test every component on GTX 1050 Ti as you build:

```bash
# Week 1: Test model performance
llama-server --model qwen3-3b-q4_k_m.gguf --n-gpu-layers 20
# Should respond in <5 seconds for simple tasks

# Week 2: Test context window
# With 4096 ctx, how many project files can you load?

# Week 3: Test browser automation
# DOM extraction + LLM reasoning cycle time?

# Week 4: Test Windows control
# UIA tree extraction speed?
```

### Validation Checklist

- [ ] Qwen 3B responds in <5s for tool calls
- [ ] Qwen 7B responds in <10s for complex reasoning
- [ ] Browser automation cycle <15s
- [ ] Windows UIA extraction <1s
- [ ] Voice transcription latency <2s
- [ ] Face verification <1s

---

## BIGGEST LEVERAGE CHANGES

### #1: Better Tool Design > Better Models

**Insight:** A well-designed tool that outputs structured actions beats a smarter model with poor tools.

**Example:**
```python
# Bad: Model must figure out coordinates
"Screenshot shows button at (453, 821). Click there."

# Good: Model outputs structured action
{"tool": "click", "element": "submit-btn", "text": "Submit"}
```

**Why leverage:** Better tools give 10x improvement in reliability. Models give 2x.

### #2: Context Injection > Model Size

**Insight:** A 3B model with perfect context outperforms a 7B model with poor context.

**Example:**
```
# Poor context (generic model):
"I need to add the skills section."

# Perfect context (3B + active.md):
"Continue building the skills section of your resume-builder project. 
You decided to use React + TypeScript with bullet points.
Previous work: Header, About, Experience sections done.
Remaining: Skills section (in progress), Education, Projects."
```

**Why leverage:** Context is free (from your Obsidian vault). Model size costs VRAM.

### #3: Session Continuity > Feature Count

**Insight:** A simple system with perfect memory beats a feature-rich system with amnesia.

**Example:**
```
# Amnesia (every session):
User: "Work on resume"
Assistant: "What resume project?"

# Memory (perfect continuity):
User: "Work on resume"
Assistant: "Resuming the resume-builder project. You were working on
the skills section. Current status: 5 of 12 skills added. 
Remaining: CLI automation, React project, current work."
```

**Why leverage:** Continuity is the core promise. Features are nice-to-haves.

---

## WHAT TO IGNORE FOR NOW

### Ignore: Multi-Agent Orchestration
**Why:** Solo user = single agent is enough. Multi-agent adds complexity without benefit.

### Ignore: Enterprise Features
**Why:** RBAC, audit trails, team features = over-engineering for solo power user.

### Ignore: Advanced Vision Capabilities
**Why:** Your 4GB VRAM can't run vision models efficiently. DOM + UIA text-based approaches work better.

### Ignore: Cloud Integration
**Why:** You explicitly said NO CLOUD. Don't even build the option.

### Ignore: Cross-Platform
**Why:** Windows-only for now. Don't add Mac/Linux complexity.

### Ignore: Plugin Marketplace
**Why:** Core capabilities should be built-in. Plugin system adds maintenance burden.

---

## RAPID PROTOTYPING APPROACH

### Prototype 1: "Hello World" Operator (Day 1-2)
```python
# Minimal viable operator
class Operator:
    def __init__(self):
        self.memory = Memory()  # Simple dict for now
        self.llm = LLM("http://localhost:8080/v1/chat/completions")
        
    async def chat(self, message: str):
        context = self.memory.get_context()
        response = await self.llm.chat([
            {"role": "system", "content": f"You are BRAVO-1. Context: {context}"},
            {"role": "user", "content": message}
        ])
        self.memory.update(message, response)
        return response
```

**Test:** Can it remember things between messages?

### Prototype 2: "Shell Commander" (Day 3-4)
```python
# Add shell execution
class Operator:
    async def execute(self, command: str):
        result = subprocess.run(command, shell=True, capture_output=True)
        return result.stdout.decode()
```

**Test:** Can it run commands on your machine?

### Prototype 3: "Browser Buddy" (Day 5-6)
```python
# Add browser automation
class BrowserOperator(Operator):
    def __init__(self):
        super().__init__()
        self.browser = PlaywrightBrowser()
        
    async def browse(self, url: str):
        page = await self.browser.goto(url)
        dom = await page.get_dom()
        # Feed to LLM for reasoning
```

**Test:** Can it navigate websites and extract information?

### Prototype 4: "Memory Brain" (Day 7-8)
```python
# Add Obsidian integration
class ObsidianBrain:
    def __init__(self, vault_path: str):
        self.vault = vault_path
        
    async def get_active_context(self):
        # Read brain/active.md
        # Inject into LLM context
        
    async def update(self, session_data):
        # Write session summary
        # Update active.md with next steps
```

**Test:** Does it remember across restarts?

---

## FINAL SPEED RECOMMENDATION

| Phase | Duration | Focus | Validation |
|-------|----------|-------|------------|
| MVP | 2 weeks | Operator core + memory | Works on GTX 1050 Ti |
| Alpha | 2 weeks | Browser + Windows control | Real automation works |
| Beta | 2 weeks | Voice + security | Natural interaction |
| Polish | 2 weeks | WhatsApp + proactive | Always accessible |

**Total: 8 weeks to polished operator**

**Key insight:** Don't build voice, camera, WhatsApp until the core operator is solid. Channels are replaceable. The brain is core.