# BRAVO-1 Runtime Profiles v1

## Why this exists
BRAVO-1 must survive current modest hardware **and** scale upward when stronger machines arrive.

So runtime profiles should be explicit, not improvised.

---

## Profile classes
### Low profile
Target:
- modest laptop
- light RAM budget
- smallest reliable GGUF lane

Use for:
- quick commands
- brief generation
- routing
- fallback operator turns

### Medium profile
Target:
- better laptop
- stronger CPU/GPU mix
- more comfortable 7B-class local reasoning

Use for:
- normal daily operator use
- better context windows
- stronger project continuity turns

### Heavy profile
Target:
- upgraded laptop or desktop
- larger context
- heavier models

Use for:
- deeper planning
- more capable local reasoning
- richer future browser/desktop tool loops

---

## Current lane mapping
### Fast lane
- default job: low-latency shell response
- expected model class: small instruct GGUF
- current script family: `llama-server-fast.*`

### Main lane
- default job: more capable local reasoning
- expected model class: 7B-ish instruct GGUF
- current script family: `llama-server-main.*`

---

## Next profile expansion
When the stronger laptop arrives, add:
- `llama-server-fast-medium.*`
- `llama-server-main-medium.*`
- `llama-server-main-heavy.*`

and let runtime status expose:
- current selected profile
- ctx size
- gpu layers
- thread count
- expected memory pressure

---

## Design rule
Do not hard-wire BRAVO-1 to one machine forever.
Keep runtime profiles machine-aware, lane-aware, and swappable.
