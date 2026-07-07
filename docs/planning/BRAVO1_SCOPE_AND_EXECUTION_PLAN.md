# BRAVO-1 Scope + Execution Plan

## Why this exists
We need to stop building as a loose pile of features and start building toward a sharp release target.

**BRAVO-1** is the working release codename.
It is the thing that has to feel worthy of the hype.

This document defines:
- what the product actually is
- who it is for first
- what the UI/UX should feel like
- what architecture gets locked
- what model/training path is realistic
- how we move faster with bigger iteration value

---

## 1. Product thesis
BRAVO-1 is **a local-first executive operator for a solo power user / founder / builder**.

Not just a chatbot.
Not just automation.
Not just a dashboard.

It should feel like:
- a **Claude-like chat surface**
- backed by a **quiet chief-of-staff / operator brain**
- with real local context, project continuity, browser action, and task steering

### Core promise
When the user opens it, BRAVO-1 should:
1. know what matters now
2. know what project/thread is active
3. reopen the right tools quickly
4. keep the UI calm
5. help the user move without decision fatigue

---

## 2. Who BRAVO-1 is for first
### Primary user
- one heavy laptop user
- mixed personal + business life
- many projects
- task/context switching pain
- wants a smarter operator layer over local work

### First wedge
**Desktop executive operator for daily work**

That means first-release strength should be in:
- chat
- current project
- next actions
- browser
- code/files/terminal handoff
- continuity

Not in:
- enterprise multi-user features
- fancy avatars
- giant ecosystem/plugin sprawl
- training custom foundation models from scratch

---

## 3. Release definition for BRAVO-1
A BRAVO-1-worthy release is one where the user can say:
- what should i do now
- resume work
- open browser
- search for X
- review this project
- open code here
- open terminal here

And the system feels:
- fast enough
- calm enough
- correct often enough
- proactive enough
- structured enough
that it becomes a real daily habit.

### BRAVO-1 must win on
- **continuity**
- **clarity**
- **speed of resuming work**
- **low-noise UI**
- **external browser behavior**

### BRAVO-1 does not need to win on
- voice/orb polish yet
- mobile handoff yet
- giant autonomous multi-agent workflows yet
- custom-trained deep specialist models yet

---

## 4. UX/UI scope freeze
## 4.1 Shell principle
The UI is **not** a dashboard product.
The UI is a **calm operating shell**.

### Always visible
- chat
- tiny status strip
- compact left sidebar with:
  - do this now
  - current project
  - tasks
  - next actions

### Hidden by default
- ops
- maintenance
- validation
- low-level tools
- debug detail
- raw diagnostics

### Shell feeling
- minimal
- premium
- low-noise
- confident
- direct
- not “AI toy”

## 4.2 UI behaviors to lock
- entering the app should immediately answer: **what matters now?**
- one primary action only
- no panel explosion
- no dashboard wall
- browser opening should work from UI directly
- context drawers should be secondary, not the main event

## 4.3 UX anti-goals
- cluttered control center
- too many visible buttons
- loud metrics everywhere
- giant exposed technical surfaces
- generic motivational filler

---

## 5. Product architecture freeze
We need a stable architecture for speed.

## 5.1 Stack posture
- **Python-first** core runtime
- FastAPI backend
- local web shell / packaged shell later
- SQLite + local state + audit
- llama.cpp-compatible local inference path
- tool wrappers over shell/browser/desktop/files/processes

## 5.2 Core modules
### Locked core
- orchestrator
- shell state service
- executive brief service
- project intelligence service
- browser tool / desktop tool / file tool / process tool
- audit / acceptance / maintenance services
- wrapper state / trusted roots

### Keep modular
- UI rendering
- tool adapters
- model router
- future voice
- future mobile handoff

## 5.3 Architecture rule
No major stack churn unless it clearly multiplies speed.

That means for now:
- no Laravel/PHP in core runtime
- no giant rewrite for novelty
- no exotic infra before product fit

---

## 6. Model strategy
## 6.1 Truth: GGUF is deployment, not training
We should be precise here:
- **GGUF is a model packaging / inference format**
- you do **not** “train a GGUF” directly
- you typically:
  1. fine-tune or adapt a source model
  2. export / convert
  3. quantize to GGUF for local use

## 6.2 BRAVO-1 model policy
For BRAVO-1, the product should rely on:
- strong prompting
- routing
- memory
- state
- tool correctness
- continuity

More than on custom model training.

### Why
On current hardware:
- 16 GB RAM
- GTX 1050 Ti 4 GB
- i7 7th gen

Training from scratch is a bad use of time.
Local LoRA fine-tuning is still limited and slow.

## 6.3 Recommended practical model path
### Local runtime
- fast/router: **Qwen 2.5 3B Instruct Q4_K_M GGUF**
- main: **Qwen 2.5 7B Instruct Q4_K_M GGUF**

### Adaptation path later
If we need specialization:
1. collect real transcripts / task patterns / tool traces
2. create instruction + preference datasets
3. do small fine-tunes or LoRA on rented/cloud GPU
4. quantize resulting checkpoint to GGUF
5. test against local daily workflows

## 6.4 Training priorities in order
1. prompt quality
2. routing quality
3. memory formatting
4. tool-call shaping
5. evaluation sets from real use
6. only then fine-tuning / LoRA

## 6.5 Non-goal right now
Do **not** spend cycles on from-scratch model training.
It will slow the product massively.

---

## 7. Speed doctrine
The current complaint is valid: things feel too slow.

We need **quick iterations** and **massive ones**.
That means each iteration must change product feel, not just add backend trivia.

## 7.1 New iteration rule
Every cycle must ship one of these:
- a big UX simplification
- a big latency cut
- a big continuity improvement
- a big execution capability jump

Not 15 scattered micro-features.

## 7.2 Cadence
### Macro loop
- plan
- build
- run on real machine
- bug-kill
- lock gains

### Suggested rhythm
- **2–3 day vertical loops**
- every loop ends with one real user validation round
- every loop must update one visible user-facing behavior

## 7.3 Performance budgets
These are targets, not guarantees yet:
- shell state refresh: **sub-700 ms target**
- obvious UI action to response: **sub-300 ms shell feedback target**
- local simple reply/tool route start: **sub-2.5 s target**
- browser open feedback: **instant shell confirmation** even if external app takes longer

---

## 8. What we are actually building next
## Track A — Product shell
Goal:
make BRAVO-1 feel like a real operator shell.

Includes:
- shell calmness
- better command UX
- cleaner resume behavior
- tighter state summaries
- better latency visibility

## Track B — Execution layer
Goal:
make BRAVO-1 actually do useful work reliably.

Includes:
- browser
- code/files/terminal flows
- trusted global roots
- safer write policies
- stronger wrappers/recipes

## Track C — Intelligence layer
Goal:
make BRAVO-1 feel context-aware, not generic.

Includes:
- executive briefing
- project continuity
- action ranking
- session resume quality
- later evaluation dataset building

## Track D — Model layer
Goal:
improve answer quality without derailing product speed.

Includes:
- prompt packs
- context shaping
- route selection
- evaluation harness
- later fine-tune plan

---

## 9. BRAVO-1 release slice
This is the lean, high-value release scope.

## Must-have
- calm chat shell
- real external browser open/search from UI + chat
- current-project intelligence
- resume-work packet
- next-action / brief engine
- trusted-root global reach with guardrails
- reliable code/files/terminal reopen flows
- local GGUF runtime that works on real machine
- acceptance / recovery / audit baseline

## Should-have
- stronger task/project linking
- better multi-project switching
- faster shell refresh
- cleaner browser context resume

## Nice-to-have later
- voice
- orb
- Android handoff
- advanced multi-agent delegation
- polished packaging/updater stack

---

## 10. Immediate architecture decisions to keep
- keep Python core
- keep FastAPI
- keep SQLite for now
- keep GGUF local runtime path
- keep browser external-first
- keep shell chat-first
- keep advanced power hidden by default
- keep trusted roots for safe global reach

---

## 11. Decision on naming for now
Because naming is still in motion:
- use **BRAVO-1** as the current release codename
- keep existing internal implementation names until later refactor/rename pass
- do **not** let naming churn slow product progress

---

## 12. Real bottleneck diagnosis
Right now the biggest risk is **not lack of features**.
It is this mix:
- unclear release target
- too many directions at once
- not enough real-machine validation loops
- too much polish before enough daily-driver proof

So from now on:
### Rule
If a feature does not clearly make BRAVO-1:
- faster
- calmer
- more correct
- more resumable
- more useful daily

then it is secondary.

---

## 13. Execution plan from here
## Step 1 — lock product scope
Done by this doc.

## Step 2 — run real-machine validation against BRAVO-1 scope
Validate only the critical daily loop:
- shell load
- browser button
- what should i do now
- current project
- resume work
- external search
- controlled browser difference

## Step 3 — bug-kill only what breaks BRAVO-1
No random expansion during bug-kill.

## Step 4 — start Phase 7 around product hardening
Only after BRAVO-1 daily-driver loop is real.

---

## 14. Bottom line
BRAVO-1 is **not** “a local AI project with many features.”
It is:

> a local-first executive operator shell that helps one power user resume, decide, and execute work with low noise.

That is the thing worth the hype.
