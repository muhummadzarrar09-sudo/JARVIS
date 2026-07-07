# Phase 5.12 — Daily-Driver Polish Plan

## Goal
Turn the stabilized JARVIS shell into a calmer daily-driver experience with a cleaner, more assistant-like interface.

## 5.12.1 — Shell UX cleanup
Status: **active**
Percent: **70.0%**

### Focus
- chat-first layout
- lower visual noise
- quieter assistant personality
- hide advanced controls behind drawers
- move toward a Claude-like chatting feel without cloning it literally

### Implemented so far
- default shell is now chat-first
- visible dashboard clutter was removed
- tasks, project, and next actions now live in a dedicated sidebar
- context/tools/ops/errors moved into hidden drawers
- small top status strip replaces the old heavy panel wall
- acceptance, maintenance, runtime, and model operations are no longer shoved in front of the operator by default
- composer and chat area are now the clear center of attention

### Exit criteria
- the shell feels calm instead of noisy
- chat is the obvious center of gravity
- useful context is available without cluttering the main surface
- advanced controls stay accessible without dominating the interface
