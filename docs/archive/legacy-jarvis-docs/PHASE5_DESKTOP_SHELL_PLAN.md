# Phase 5 Desktop Shell Plan

This document maps the next major layer after Phase 4 completion: the packaged desktop app shell.

## Goal
Turn the terminal-first JARVIS command center into a visual desktop application while preserving the same operating model.

## Core idea
The desktop shell should be the visual evolution of the current terminal console, not a separate product.

That means it should preserve:
- command center layout
- project context
- wrapper/browser status
- task/session visibility
- timeline/replay visibility
- approval prompts for risky actions

## Shell sections
### Left rail
- today
- progress
- browser
- tasks
- sessions
- phase status

### Center workspace
- conversation / command stream
- action results
- file/code/browser previews later

### Right rail
- current focus
- next actions
- wrapper doctor
- project context

## First shell milestones
1. packaged windowed app frame
2. panel layout matching current console concepts
3. call local FastAPI endpoints
4. render validation / progress / browser / tasks / sessions panels
5. render action timeline
6. add approval modal for high-risk actions

## Dependency on current work
Phase 5 depends on:
- Phase 4 command center being stable
- browser/desktop wrapper behavior being usable
- task/session/project summaries being reliable
- operator approval logic being present

## Recommended shell stack direction
- Python backend stays as core
- frontend can be local web UI first, then packaged desktop shell
- packaged shell should still work offline and talk to localhost APIs

## Immediate pre-shell priorities
1. validate browser launching on the real Windows machine
2. validate exact desktop focus behavior on the real Windows machine
3. keep improving fallback UX for missing local apps
4. stabilize operator summaries, validation reports, and project context outputs
