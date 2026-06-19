# Phase Plan

## Phase 0 — Foundation
**Outcome:** local app boots reliably.
- bootstrap script works
- `.env` exists
- folders created
- at least one GGUF model downloaded
- `/health` and `/chat` respond

## Phase 1 — Terminal MVP
**Outcome:** JARVIS can reason + act in terminal workflows.
- llama.cpp wired in for real inference
- shell execution endpoint works
- file tool layer added
- session memory persists
- audit logs visible

## Phase 2 — Structured Tool Use
**Outcome:** less raw shell, more reliable tool contracts.
- filesystem tool adapter
- process manager tool
- Git tool adapter
- policy labels for risky tools
- command replay and undo metadata

## Phase 3 — Browser Automation
**Outcome:** JARVIS can operate web tasks.
- Playwright integration
- browser sessions
- screenshot capture
- form-fill / extraction flows

## Phase 4 — Windows Desktop Control
**Outcome:** JARVIS operates normal desktop apps.
- window enumeration
- focus management
- click/type automation
- screenshot perception loop

## Phase 5 — Voice + Orb UI
**Outcome:** feels like JARVIS.
- local STT
- local TTS
- subtitle layer
- orb UI
- wake-word / always-listening pipeline

## Phase 6 — Android Companion + Handoff
**Outcome:** session follows you.
- mobile-responsive UI first
- LAN websocket sync
- session checkpoint handoff
- room-exit logic later

## Phase 7 — Product Hardening
**Outcome:** personal tool becomes product-grade.
- auth hardening
- permission policies
- packaging
- updater
- installer
- telemetry (local-first)
