# BRAVO-1 Dependency Strategy v1

## Goal
Keep BRAVO-1 fast to iterate on now, but predictable to package later.

## Phase-based dependency policy
### Phase 0 / current rebuild
- prefer stdlib where possible
- add external dependencies only when they unlock real product value
- do not import heavy stacks before the architecture lane is proven

### Phase 1 / operator core
Expected first real dependencies later:
- `pywinauto` for Windows UIA
- `pyautogui` as fallback desktop action layer
- `playwright` for controlled browser mode
- optionally `pydantic` or `pydantic-settings` if config complexity rises enough to justify it

### Phase 2 / runtime + packaging
- pin production dependencies exactly
- split dev/test dependencies from runtime dependencies
- produce exportable install manifests for the future installer

## Practical rules
1. every new dependency must justify itself against:
   - Windows fit
   - local-first fit
   - packaging burden
   - speed of iteration
2. every dependency should have:
   - purpose
   - owner module
   - fallback if absent
3. avoid framework sprawl until the operator loop is solid

## Packaging implication
The installer path gets much easier if BRAVO-1 keeps:
- light Python core
- explicit optional dependency groups
- clear runtime prerequisites

## Current onboarding assets
- `requirements-runtime.txt`
- `requirements-dev.txt`
- `docs/planning/BRAVO1_DEPENDENCY_ONBOARDING_V1.md`
- `scripts/bootstrap-dev.*`
- `scripts/install-playwright.*`
- `scripts/install-windows-tools.*`

## Next dependency milestone
When we begin the full controlled browser + Windows UIA integration pass, pin real runtime versions instead of placeholders and verify packaging implications.
