# JARVIS Console UI Vision

This is the terminal-first interface direction inspired by the usability of Claude Code, but branded and shaped for JARVIS.

## Goal
Keep the speed and seriousness of a code-first terminal assistant while making it feel like a command center for:
- local AI
- tool execution
- browser control
- desktop control
- app wrappers
- long-running sessions

## Terminal design language

### Core vibe
- clean command prompt
- strong status panels
- action/timeline visibility
- low-friction slash commands
- minimal clutter, high signal

### JARVIS-specific twist
Instead of copying Claude Code exactly, the JARVIS console should add:
- wrapper/app awareness
- remembered wrapper targets/state
- session continuity state
- desktop/browser active status
- audit/action visibility
- later: orb/voice status in the desktop app shell

## Current console starter
Implemented now in the terminal:
- JARVIS console banner
- dashboard panels at startup
- wrapper status panel with remembered targets
- slash commands:
  - `/status`
  - `/wrappers`
  - `/recipes`
  - `/tools`
  - `/clear`
- `jarvis>` prompt

## Future console evolution
1. action timeline panel
2. live task panel
3. active browser/desktop state ribbon
4. approval prompts for risky actions
5. richer diff/view panels for file changes
6. command palette / fuzzy launcher

## Relationship to the desktop app
The terminal console is not throwaway.
It is the interaction model prototype for the packaged desktop app.

That means the future desktop app should preserve:
- command-center layout
- session/timeline visibility
- tool cards / wrapper cards
- audit visibility

So yes: terminal first, desktop app later — but the desktop app should feel like the visual evolution of this console.
