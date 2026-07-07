# BRAVO-1 — Pattern Map

---

## UI PATTERNS

### Pattern 1: Calm Operator UI (Hermes-style)
**Source:** Hermes Agent

**The Pattern:**
- Compact banner with tool summary
- Streaming token output (real-time)
- Tool progress indicators (can be quiet or verbose)
- Session ID displayed for reference
- Single-line mode for minimal intrusion

**Why it works:**
- Low noise — hides control surfaces until invoked
- Streaming makes it feel alive, not waiting
- Tool progress gives transparency without clutter

**BRAVO-1 Implementation:**
```
┌─────────────────────────────────────────────────────────────┐
│ BRAVO-1 │ Session: abc123 │ Project: resume-builder │ 14:32 │
├─────────────────────────────────────────────────────────────┤
│ > What should I work on next?                               │
│                                                           │
│ Based on your session yesterday, you're building the       │
│ skills section. The remaining tasks are:                   │
│   • Add React project                                       │
│   • Document CLI automation work                           │
│   • Update education timeline                              │
│                                                           │
│ [Running browser to check your live site...]               │
│                                                           │
│ Your site shows the portfolio correctly. Ready to proceed  │
│ with the skills section?                                   │
└─────────────────────────────────────────────────────────────┘
```

### Pattern 2: Minimal Confirmation UI
**Source:** Open Interpreter

**The Pattern:**
- Code shown in diff format before execution
- Confirmation required for dangerous operations
- `--auto-run` or `--yolo` mode to skip confirmations
- Clear indication of what will happen

**Why it works:**
- Power user can go fast with `--yolo`
- Security-conscious user gets confirmation
- Diff format is scannable, not overwhelming

**BRAVO-1 Implementation:**
```
⚠️ This will execute on your machine:

  git add -A && git commit -m "feat: Add skills section"
  
  Branch: main
  Files: 3 changed, 12 insertions
  
[Y] Execute  [N] Cancel  [A] Always for this session  [D] Details
```

### Pattern 3: Voice Mode Indicator
**Source:** Hermes Agent + Voice Chat AI

**The Pattern:**
- Visual indicator when recording
- Real-time transcription preview
- TTS response with personality hints
- Beep sounds for start/stop

**Why it works:**
- Clear feedback on voice state
- Transcription preview lets you correct before send
- Personality hints in TTS make it feel like a person

---

## CLI PATTERNS

### Pattern 1: Operator Loop (Hermes-style)
**Source:** Hermes Agent

**The Core Loop:**
```
Input (voice/text) → Session Context → Agent Reasoning → Tool Execution → Response → Memory Update
```

**Key characteristics:**
- Session context always injected
- Tools as first-class citizens
- Memory update at end of every turn
- Streaming output for responsiveness

### Pattern 2: Harness System (Open Interpreter)
**Source:** Open Interpreter

**The Pattern:**
- Swap agent behavior by changing harness
- Native harness: fast, simple, local-model optimized
- Claude Code harness: uses Claude's coding patterns
- Custom harnesses for specific workflows

**BRAVO-1 Implementation:**
```
bravo-1 --harness native      # Fast local model, simple execution
bravo-1 --harness coding      # Enhanced code understanding
bravo-1 --harness research    # Web search + browser heavy
```

### Pattern 3: Slash Commands
**Source:** Hermes Agent + Aider

**The Pattern:**
- `/brief` — Load project context
- `/capture` — Save decision in flow
- `/recall` — Look up information
- `/handoff` — Document session end
- `/undo` — Revert last change

**Why it works:**
- Zero-token execution (no LLM call)
- Fast access to common operations
- Composable with natural language

---

## ORCHESTRATION PATTERNS

### Pattern 1: Session Lifecycle (Hermes)
**Source:** Hermes Agent

**The Pattern:**
```
Session Start:
  → Load Brain/active.md
  → Inject context into system prompt
  → Orient agent to current work

Session Continue:
  → Process input
  → Execute with context
  → Update session state

Session Handoff:
  → Extract: request, decisions, learnings, next_steps
  → Write session summary to vault
  → Update Brain/active.md with next steps
```

### Pattern 2: Context Compression (Hermes)
**Source:** Hermes Agent

**The Pattern:**
- Track context usage per model family
- At 85% threshold, summarize middle turns
- Older messages compressed, recent kept verbatim
- Transparent notification when compaction occurs

**Why it matters:** Prevents context overflow while preserving recent work and final decisions.

### Pattern 3: Multi-Channel Routing (Hermes)
**Source:** Hermes Agent

**The Pattern:**
```
WhatsApp message → Session resolver → Per-contact session
Telegram message → Session resolver → Per-contact session
CLI input → Session resolver → Main session
```

**Key insight:** Each (channel, contact) pair = persistent session. Shared memory layer across channels.

---

## BROWSER PATTERNS

### Pattern 1: DOM-Based UI Reasoning (Browser Use)
**Source:** Browser Use

**The Pattern:**
```
Page load → DOM extraction → Element tree → LLM reasoning → Action → Verification
```

**Why better than screenshots:**
- Text-based = works with Qwen 3B
- Structured = reliable element targeting
- No vision model needed = fast, cheap

**Element schema:**
```json
{
  "type": "button",
  "id": "submit-btn",
  "text": "Submit",
  "visible": true,
  "parent": "form"
}
```

### Pattern 2: Persistent Browser Sessions
**Source:** Browser Use + Steel Browser

**The Pattern:**
- Launch browser with profile
- Cookies, local storage persist
- Logged-in state survives restarts
- Headful for auth, headless for automation

**Why it matters:** You log into a site once, agent uses it forever.

### Pattern 3: Headful/Headless Switching
**Source:** Browser Use

**The Pattern:**
```
Task requires interaction (login, CAPTCHA):
  → Headful mode (visible browser)
  → User or agent interacts
  → Auth state captured

Task is automation:
  → Headless mode (invisible)
  → Fast, no UI overhead
  → Resumes with auth state
```

---

## MEMORY / TASK PATTERNS

### Pattern 1: Vault-First Memory (Open Second Brain)
**Source:** Open Second Brain

**The Pattern:**
```
Brain/
  active.md          # Always-on context
  sessions/          # Session summaries
  decisions/         # Decision log
  preferences/       # Learned preferences with confidence
  projects/          # Project context
```

**Why Markdown:**
- Human-readable
- Git-tracked
- Obsidian-navigable
- LLM-parseable

### Pattern 2: Session Summary Format (Open Second Brain)
**Source:** Open Second Brain

**The Pattern:**
```markdown
---
title: Session 2026-07-07
date: 2026-07-07T14:32:00
type: session-summary
---

## Request
What the user asked for

## Decisions
- Decision 1
- Decision 2

## Learnings
- What the agent learned
- What patterns emerged

## Next Steps
- Immediate next action
- Long-term follow-up
```

### Pattern 3: Preference Confidence Scoring
**Source:** Open Second Brain

**The Pattern:**
```markdown
## preferences/

confidence_0.8/
  use-regex-而非split.txt     # Corrected 4 times, now confident
  project-structure.md        # Established pattern

confidence_0.3/
  naming-convention.txt       # Only corrected once, still learning
```

**Nightly dream pass:**
- Review corrections from past 24h
- If same correction 3+ times → elevate confidence
- If contradicted → reset confidence

### Pattern 4: Project Continuity Hook
**Source:** Work Buddy + Obsidian Mind

**The Pattern:**
```
SessionStart hook:
  → Read TODO.md
  → Read architecture/decisions.md  
  → Read recent session logs
  → Inject into context
  → Agent starts WITH work already understood
```

---

## PACKAGING PATTERNS

### Pattern 1: Tool Adapter Interface (Open Interpreter)
**Source:** Open Interpreter

**The Pattern:**
```python
class ToolAdapter:
    """Narrow interface contract"""
    
    def execute(self, tool: str, args: dict) -> ToolResult:
        """Execute tool, return result"""
        pass
    
    def validate(self, tool: str, args: dict) -> bool:
        """Validate tool call before execution"""
        pass
```

**Why narrow contracts matter:**
- Easy to add new tools
- Easy to swap implementations
- Easy to test in isolation

### Pattern 2: MCP Server Pattern (Hermes)
**Source:** Hermes Agent

**The Pattern:**
- MCP servers as tool providers
- StdIo (subprocess) or HTTP (remote) transport
- Per-server config (timeout, keepalive)
- Skills as MCP-compatible definitions

### Pattern 3: Safety Confirmation System
**Source:** Hermes Agent + Open Interpreter

**The Pattern:**
```python
class SafetyChecker:
    """Guardrail system"""
    
    def check(self, action: Action) -> SafetyResult:
        # Check against known dangerous patterns
        # Prompt user if uncertain
        # Allow or block
        
DANGEROUS_PATTERNS = [
    r"rm -rf /",
    r"format.*drive",
    r"del /f /s /q.*system",
]
```

---

## INTEGRATION PATTERNS

### Pattern 1: WhatsApp Integration (Hermes)
**Source:** Hermes Agent WhatsApp gateway

**The Pattern:**
```
WhatsApp Webhook → Flask/FastAPI → Session resolver → Agent → Response → WhatsApp API
```

**Key components:**
- Webhook verification (handshake)
- Message parsing (text, audio, image)
- Phone number as session key
- Template messages for responses

### Pattern 2: Camera Verification (DeepFace)
**Source:** DeepFace

**The Pattern:**
```python
# Enrollment (once)
camera.capture("reference.jpg")
embed_reference = DeepFace.represent("reference.jpg", model="ArcFace")
store(embed_reference)

# Verification (on activation)
frame = camera.capture()
embed_frame = DeepFace.represent(frame, model="ArcFace")
if cosine_distance(embed_frame, embed_reference) < threshold:
    # It's me
    activate_operator_mode()
else:
    # Unknown
    alert_and_lock()
```

### Pattern 3: Battery Monitor + Shutdown
**Source:** Custom (not from research)

**The Pattern:**
```
Power loss detected:
  → Save current state to vault
  → Document completed work
  → Document remaining work
  → Send WhatsApp: "Shutting down. Completed X, remaining Y"
  → Graceful shutdown

Power restored:
  → Load state from vault
  → Resume from checkpoint
```

---

## ANTI-PATTERNS TO AVOID

### Anti-Pattern 1: Dashboard Overload
**Why avoid:** Brains don't have dashboards. The operator shell should be a conversation, not a control center.

**What to do instead:**
- Minimal UI showing only current context
- Information density in text, not widgets
- Tools hidden until needed

### Anti-Pattern 2: Fake Autonomy
**Why avoid:** "Autonomous" agents that require constant supervision are worse than simple tools.

**What to do instead:**
- Clear distinction between autonomous and supervised tasks
- Human-in-the-loop for important decisions
- Proactive notifications for significant events

### Anti-Pattern 3: Cloud Lock-In
**Why avoid:** Cloud dependency breaks when offline, costs money, and sacrifices privacy.

**What to do instead:**
- All models run locally
- All data stays on machine
- Cloud only as explicit fallback

### Anti-Pattern 4: Vision Model Dependency
**Why avoid:** Vision models are slow, expensive, and require GPU horsepower you don't have.

**What to do instead:**
- DOM parsing for browser (text-based)
- UIA trees for Windows (text-based)
- Screenshot only as last-resort fallback

### Anti-Pattern 5: Plugin Sprawl
**Why avoid:** Every plugin is a maintenance burden and potential failure point.

**What to do instead:**
- Core capabilities built-in
- Plugin system only for truly optional features
- Stability over feature count