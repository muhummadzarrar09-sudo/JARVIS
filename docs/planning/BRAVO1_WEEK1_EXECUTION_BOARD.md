# BRAVO-1 Week 1 Execution Board

## Objective
Stand up the **new BRAVO-1 spine** fast.

## Week-1 outcome
By end of Week 1 we should have:
- importable Python package
- terminal shell loop
- session state working
- active brain file integration
- operator skeleton returning structured replies
- runtime profile docs/scripts ready for local GGUF serving

---

## Workstream A — Core package
### Must finish
- [ ] root `pyproject.toml`
- [ ] `app/bravo1/` package skeleton
- [ ] config loader
- [ ] operator core
- [ ] session store
- [ ] terminal channel

## Workstream B — Brain continuity
### Must finish
- [x] `data/brain/active.md` bootstrap
- [x] session summary path design
- [x] project continuity placeholder hooks
- [x] project capture path for notes / ideas / blockers

## Workstream C — Runtime
### Must finish
- [x] runtime README with model policy
- [x] PowerShell startup profile for llama-server
- [x] env example for local paths
- [x] first routing config notes
- [x] runtime reachability checks
- [x] runtime start/stop helper path

## Workstream D — Validation
### Must finish
- [x] package import test
- [x] CLI smoke test
- [x] syntax compile pass
- [x] operator command smoke test

---

## Cut list
If anything slows Week 1, cut it.

Cut for now:
- web UI
- browser automation
- Windows UIA
- voice
- WhatsApp
- installer
- fine-tuning
- camera/security

---

## Daily operating rule
Every change should improve one of these:
- speed of iteration
- clarity of architecture
- calmness of shell UX
- continuity of operator state

---

## Definition of success
At the end of Week 1, running the shell should feel like:
- BRAVO-1 starts
- BRAVO-1 knows its session
- BRAVO-1 can read active context
- BRAVO-1 can answer in a structured operator format
- BRAVO-1 is ready for browser + Windows layers next
