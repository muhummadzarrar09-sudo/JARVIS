# BRAVO-1 Dependency Onboarding v1

## Goal
Make it easy to bring optional capability lanes online without muddying the base rebuild.

## Base dev setup
- `scripts/bootstrap-dev.ps1`
- `scripts/bootstrap-dev.sh`

Installs:
- `requirements-dev.txt`

## Optional browser lane setup
- `scripts/install-playwright.ps1`
- `scripts/install-playwright.sh`

Installs:
- `playwright`
- Chromium browser for controlled mode

## Optional Windows control lane setup
- `scripts/install-windows-tools.ps1`
- `scripts/install-windows-tools.sh`

Installs:
- `pywinauto`
- `pyautogui`

## Why this matters
This keeps BRAVO-1:
- lightweight by default
- capability-upgradable on demand
- cleaner to package later
