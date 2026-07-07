# Build Audit — Phase 5 Hardening Pass 2

## Implemented

### Shell send-path hardening
- rebuilt the live shell composer around a real `<textarea>` flow
- Enter now sends reliably
- Shift+Enter keeps multiline entry
- added explicit submit/error handling in the shell UI
- added visible composer status messages
- added retry-last / clear controls
- added stronger `/chat` fetch error surfacing into the shell feed so failures are no longer silent

### Shell runtime visibility
- shell now loads `/health`, `/shell/state`, and `/voice/status` together during boot/refresh
- added status badges for:
  - API health
  - active model runtime mode
  - packaged-shell readiness
- added model runtime block in the right rail
- added snapshot actions for today/browser/models/validation/timeline

### Local GGUF model enablement
- added `app/services/model_service.py`
- added automatic GGUF discovery from `data/models`
- added configured-vs-effective provider logic
- added `auto` model provider mode
- added local model selection helpers for fast/main roles
- added local model status and provider switching API routes
- added beginner commands:
  - `show model status`
  - `use local models`
  - `use mock mode`
- added scripts:
  - `scripts/use-local-models.ps1`
  - `scripts/use-mock-models.ps1`

### Llama runtime improvements
- `llm_router` now uses discovered GGUF models when local mode is ready
- `llama_manager` now respects runtime tuning settings:
  - `LLAMA_N_CTX`
  - `LLAMA_N_THREADS`
  - `LLAMA_N_GPU_LAYERS`
  - `LLAMA_MAX_TOKENS`

### Validation/reporting upgrades
- validation report now includes model status
- shell state now includes model status
- runtime validation report now includes model status
- health route now reports configured/effective provider and selected model

## Why this matters
This pass directly targets the two pain points blocking real usability:
1. the shell now exposes errors instead of failing silently when sending a prompt
2. local GGUF usage is now a first-class runtime path instead of a manual `.env` guessing game

## Remaining real-machine checks
- confirm prompt send/receive behavior inside the packaged shell on the user’s Windows machine
- confirm `use local models` selects the intended GGUF files on the user’s actual model directory
- confirm local llama.cpp inference speed/stability on the user’s laptop hardware
- keep tightening shell UX from real Windows feedback
