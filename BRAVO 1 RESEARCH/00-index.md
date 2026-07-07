# BRAVO-1 Research — Index

**Project:** Local-first autonomous executive operator shell  
**Hardware:** GTX 1050 Ti 4GB + 8GB DDR4 + i7 7700HQ  
**Platform:** Windows-only, Local-first (NO CLOUD)  
**Channels:** WhatsApp (primary), Voice, Camera

---

## RESEARCH FILES

| # | File | Content |
|---|------|---------|
| 00 | `00-index.md` | This file |
| 01 | `01-executive-summary.md` | Top 10 repos, scoring matrix, final verdict |
| 02 | `02-repos-deep-analysis.md` | Repo-by-repo deep analysis with commit history |
| 03 | `03-pattern-map.md` | UI, CLI, orchestration, browser, memory patterns |
| 04 | `04-synthesis-plan.md` | What to take, combine, reject, build ourselves |
| 05 | `05-recommended-stack.md` | Technology recommendations with code examples |
| 06 | `06-speed-strategy.md` | MVP first, validation, biggest leverage |
| 07 | `07-commit-history-intelligence.md` | Alive vs dead, engineering discipline analysis |
| 08 | `08-final-answer.md` | THE ANSWER: exact parts, from where, in what order |

---

## QUICK ANSWER

### Top Repos to Study:
1. Hermes Agent (211k stars) — operator brain, session management, multi-channel
2. Browser Use (103k stars) — DOM-based browser automation
3. Open Interpreter (64k stars) — code execution, OS control
4. Windows-Use — UIA-based Windows GUI control
5. llama.cpp (56k stars) — GGUF runtime for local models

### Steal Now (7 repos):
1. Hermes Agent — operator loop, session management, WhatsApp, voice, skills
2. Browser Use — DOM extraction, element references, session persistence
3. Open Interpreter — code execution harness, safety confirmations
4. Windows-Use — UIA tools, Windows control
5. Open Second Brain — Obsidian brain, session summaries, preferences
6. llama.cpp — GGUF runtime, OpenAI-compatible server
7. FunASR + DeepFace — speech recognition + face verification

### Implementation Order:
- **Weeks 1-2:** Operator brain (Hermes) + model runtime (llama.cpp)
- **Weeks 3-4:** Automation hands (Browser Use + Windows-Use)
- **Weeks 5-6:** Memory brain (Open Second Brain) + senses (FunASR + DeepFace)
- **Weeks 7-8:** Communication (WhatsApp) + polish (proactive loop)

---

## KEY INSIGHTS

### The Core Magic:
1. **Hermes Agent:** "Session-is-everything loop" — brain/active.md context injection
2. **Browser Use:** "DOM as language" — text-based browser control, no vision needed
3. **Windows-Use:** "UIA as universal interface" — direct Windows control without coordinates

### Anti-Patterns to Avoid:
- Dashboard overload (brains don't have dashboards)
- Fake autonomy (supervised > unreliable autonomous)
- Cloud lock-in (you're local-first)
- Vision model dependency (DOM + UIA = text-based = fast)

### Biggest Leverage Changes:
1. Better tool design > better models
2. Context injection > model size
3. Session continuity > feature count

---

## VALIDATION CHECKLIST

Before each phase, validate on GTX 1050 Ti:

- [ ] Qwen 3B responds in <5s for tool calls
- [ ] Qwen 7B responds in <10s for complex reasoning
- [ ] Browser automation cycle <15s
- [ ] Windows UIA extraction <1s
- [ ] Voice transcription latency <2s
- [ ] Face verification <1s

---

## THE VISION

**BRAVO-1 is not a chatbot. It's your autonomous chief-of-staff.**

When you open BRAVO-1:
- It knows what matters now
- It knows the current project/thread
- It reopens the right tools
- It reduces decision fatigue
- It helps you execute work quickly
- It evolves over time through preference learning
- It notifies you via WhatsApp when significant
- It shuts down gracefully when power is lost
- It resumes where it left off when you return

**8 weeks to production.**

---

*Research completed: 2026-07-07*  
*All files stored in `/home/user/bravo-1/`*