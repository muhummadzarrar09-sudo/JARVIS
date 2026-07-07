# BRAVO-1 — Commit History Intelligence

---

## REPOS THAT ARE TRULY ALIVE

### 1. Hermes Agent — EXPLOSIVE ACTIVITY
**Commits:** 14,751 | **Latest:** 4 minutes ago  
**Branches:** 1,283 | **Tags:** 25

**Verdict:** ALIVE and accelerating.

**Evidence:**
- Multiple commits per day (recent: 4 minutes ago)
- Active PR/issue engagement (#724: YOLO mode feature)
- CI infrastructure improvements (retry handling, flake prevention)
- TypeScript rewrite of plugins (architectural investment)
- Security hardening (event validation, identity blacklist)
- Versioned releases (v0.18.0 in July 2026)

**Signals this is production-grade:**
- CI timing report unflakeable fix (#59818) — obsession with reliability
- Ruff linting at scale (216 fixes) — code quality discipline
- Security review on event_log_append validation

**Concerns:** None identified. This is the real deal.

---

### 2. Browser Use — STRONG ACTIVITY
**Commits:** 9,800 | **Latest:** 7 hours ago  
**Branches:** 530 | **Tags:** 141

**Verdict:** ALIVE with focused development.

**Evidence:**
- Recent DOM visibility fixes (idempotency testing)
- Type checking strictness improvements
- Skill sync maintenance
- Benchmark tracking (BU-Ultra at 78%)
- Docker build improvements
- Python package structure well-maintained

**Signals this is production-grade:**
- Test coverage for edge cases (DOM visibility)
- Type checking in CI
- Lint script reliability improvements

**Concerns:** None identified. Active, well-engineered.

---

### 3. Open Interpreter — STRONG ACTIVITY
**Commits:** 8,064 | **Latest:** 9 hours ago  
**Architecture:** Rust rewrite in progress

**Verdict:** ALIVE with architectural evolution.

**Evidence:**
- Rust rewrite (codex-rs) in progress
- Bazel build system (enterprise-grade)
- Python version maintenance
- CI workflow updates
- Multiple harness implementations

**Signals this is production-grade:**
- Build system investment (Bazel)
- Cross-platform support (Windows, macOS, Linux)
- Multiple agent harnesses maintained

**Concerns:** Rust rewrite may complicate short-term integration.

---

### 4. llama.cpp — INDUSTRIAL STRENGTH
**Commits:** Massive | **Activity:** Continuous

**Verdict:** ALIVE and foundational.

**Evidence:**
- Core C/C++ implementation (battle-tested)
- Continuous GPU optimization
- GGUF format as industry standard
- Function calling support
- Multi-model serving

**Signals this is production-grade:**
- No concerning issues in years of operation
- Industry-standard model format
- Battle-tested inference engine

**Concerns:** None. This is infrastructure, not a product.

---

### 5. Open Second Brain — ACTIVE (NEWER PROJECT)
**Commits:** 146 | **Latest:** 12 hours ago  
**Recent:** v0.7.0 TypeScript rewrite (May 2026)

**Verdict:** ALIVE with recent architectural jump.

**Evidence:**
- TypeScript rewrite on Bun (modern stack)
- Security hardening (date validation, identity blacklist)
- Self-heal mechanisms for index corruption
- Integration tests (176 bun test cases)
- CI validation (OpenClaw bundle diff check)

**Signals this is production-grade:**
- Security-first development
- Test coverage for critical paths
- Active maintenance of critical fixes

**Concerns:** Small team (single maintainer pattern), but active community engagement.

---

## REPOS THAT ARE QUIETLY DEAD (OR DYING)

### 1. Work Buddy — UNCERTAIN
**Stars:** 3 | **Recent:** July 2026 release

**Verdict:** UNCERTAIN but not abandoned.

**Evidence:**
- Recent release (July 2026)
- But only 3 stars = tiny community
- Claude Code coupling limits audience
- Complex feature set for tiny user base

**Concerns:** May struggle to maintain momentum with limited community.

---

### 2. PyGPT — STALE
**Last meaningful update:** March 2025

**Verdict:** STALE, not actively developed.

**Evidence:**
- 11 modes of operation suggests feature sprawl
- No recent commits in search results
- Multiple cloud dependencies (Azure, ElevenLabs, OpenAI)

**Concerns:** Not local-first, cloud-dependent.

---

### 3. Windows-Use — SMALL BUT ACTIVE
**Stars:** 968 | **Activity:** Regular commits

**Verdict:** SMALL but ACTIVE.

**Evidence:**
- Recent README updates (March 2026)
- Documentation additions
- Active issue response

**Concerns:** Very small community. Risk of abandonment if maintainer loses interest.

---

## REPOS WITH SERIOUS ENGINEERING DISCIPLINE

### Hermes Agent
**What makes it disciplined:**
- CI retry handling (exponential backoff, rate limit awareness)
- Ruff linting at scale (216 fixes)
- Security review process (event validation, identity blacklist)
- Type checking in CI
- Versioned releases with changelogs

**Pattern:** Treats infrastructure as production-grade.

---

### Open Second Brain
**What makes it disciplined:**
- Security hardening (date traversal, identity blacklist)
- Self-heal mechanisms (index corruption recovery)
- Integration testing (176 test cases)
- CI validation (bundle diff check)
- Breaking change management (CHANGELOG)

**Pattern:** Treats data integrity as critical.

---

### Browser Use
**What makes it disciplined:**
- DOM visibility idempotency testing
- Type checking strictness
- Lint script reliability
- Benchmark tracking
- Docker build validation

**Pattern:** Treats correctness as critical.

---

## REPOS WITH VISION DRIFT

### None identified in top repos.

**Hermes Agent:** Vision is clear — operator agent with skills, memory, multi-channel.  
**Browser Use:** Vision is clear — browser automation for LLMs.  
**Open Interpreter:** Vision is clear — local code execution.

All top repos have consistent, focused vision.

---

## REPOS THAT FEEL LIKE FOUNDATIONS VS EXPERIMENTS

### FOUNDATIONS:
| Repo | Why Foundation | Evidence |
|------|----------------|----------|
| llama.cpp | Industry standard runtime | GGUF format adopted everywhere |
| Hermes Agent | Operator loop pattern | Multi-channel, memory, skills all proven |
| Browser Use | DOM automation pattern | 103k stars, benchmark proven |
| Open Interpreter | Code execution pattern | 64k stars, multiple harnesses |

### EXPERIMENTS:
| Repo | Why Experiment | Evidence |
|------|----------------|----------|
| Windows-Use | New, small community | 968 stars, limited adoption |
| Open Second Brain | New, TypeScript rewrite | 146 commits, recent architecture change |
| Work Buddy | Niche Claude Code integration | 3 stars, tight coupling |

---

## FINAL VERDICT: WHICH REPOS TO TRUST

### TRUST (Use as Foundation):
1. **Hermes Agent** — 14,751 commits, production-hardened, clear vision
2. **Browser Use** — 9,800 commits, benchmark-proven, active development
3. **llama.cpp** — Foundation infrastructure, industry standard
4. **Open Interpreter** — 8,064 commits, Rust rewrite shows investment

### TRUST WITH CAVEAT (Use as Reference):
5. **Windows-Use** — Good for patterns, small community risk
6. **Open Second Brain** — Good for memory patterns, recent rewrite
7. **Aider** — Good for git patterns, not primary operator
8. **FunASR** — Good for STT patterns, specialized use

### DON'T TRUST (Avoid):
9. **OpenHands** — Over-engineered for solo use case
10. **UI-TARS** — Requires 16GB+ VRAM, specialized model

---

## ARCHITECTURAL INSIGHTS FROM COMMITS

### Pattern 1: Event-Driven Evolution
**From:** Hermes Agent

**Evidence:** 14,751 commits show evolution from simple CLI to multi-channel operator. Each messaging platform added as isolated adapter, not core change.

**Lesson:** Build core that can absorb new capabilities without redesign.

---

### Pattern 2: Test-Driven Correctness
**From:** Browser Use, Open Second Brain

**Evidence:** DOM visibility tests, self-heal tests, integration tests — all committed alongside fixes.

**Lesson:** Write tests for edge cases, not just happy paths.

---

### Pattern 3: Security as Feature
**From:** Open Second Brain, Hermes Agent

**Evidence:** Security fixes (event validation, identity blacklist, date traversal) committed with same urgency as features.

**Lesson:** Don't defer security for features. Security IS a feature.

---

### Pattern 4: Architecture Investment
**From:** Open Interpreter (Rust rewrite), Open Second Brain (TypeScript rewrite)

**Evidence:** Rewrite investment signals long-term commitment and architectural evolution.

**Lesson:** Don't be afraid to rewrite for better foundations.

---

## SUMMARY TABLE

| Repo | Alive? | Discipline | Foundation? | Trust Level |
|------|--------|------------|-------------|-------------|
| Hermes Agent | YES (explosive) | HIGH | YES | TRUST |
| Browser Use | YES (strong) | HIGH | YES | TRUST |
| Open Interpreter | YES (strong) | HIGH | YES | TRUST |
| llama.cpp | YES (continuous) | HIGH | YES | TRUST |
| Open Second Brain | YES (active) | HIGH | EMERGING | TRUST (with caveat) |
| Windows-Use | YES (small) | MEDIUM | NO | REFERENCE |
| Aider | YES | HIGH | YES | REFERENCE |
| FunASR | YES | MEDIUM | YES | REFERENCE |
| Work Buddy | UNCERTAIN | LOW | NO | AVOID |
| OpenHands | YES | HIGH | YES | AVOID (scope) |