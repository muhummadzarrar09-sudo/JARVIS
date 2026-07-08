# BRAVO-1 Installer Build Manifest v1

## Purpose
This document defines what a future installer build must gather before we can generate `BRAVO-1-Setup.exe`.

## Build inputs
### App entrypoints
- CLI entrypoint
- web shell entrypoint
- API entrypoint
- runtime validation entrypoint

### Config assets
- env example
- runtime profile scripts
- prompt pack files
- shell web assets

### Data directories to create
- `data/brain/`
- `data/sessions/`
- `data/summaries/`
- `data/runtime/`
- `data/browser/`

### Shortcut targets
- BRAVO-1 CLI
- BRAVO-1 Web Shell
- BRAVO-1 API (optional developer shortcut)

## Runtime prerequisites to evaluate later
- Python presence / embedded runtime strategy
- browser automation prerequisites
- Windows automation prerequisites
- model path selection / model download strategy

## First installer dry-run target
Before a real `.exe` build, we should be able to produce:
1. a clean file inventory
2. a pinned dependency inventory
3. a reproducible local bootstrap script
4. a runtime validation report proving the install works
