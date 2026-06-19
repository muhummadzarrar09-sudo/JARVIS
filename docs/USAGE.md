# Terminal MVP Usage

## Start the API
```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Start terminal JARVIS
```powershell
.\.venv\Scripts\Activate.ps1
python -m app.cli repl
```

## CLI examples

### Normal chat
```text
Design me a roadmap for my Python project
```

### Shell command
```text
shell: dir
```

### List files
```text
fs list: .
```

### Read a file
```text
fs read: README.md
```

### Write a file
```text
fs write: notes/todo.txt ::: Build JARVIS phase 1 today
```

### Append to a file
```text
fs append: notes/todo.txt ::: Add browser automation later
```

### Make a directory
```text
fs mkdir: notes/archive
```

## Browser mode examples

### Install browser support
```powershell
.\scripts\install-browser.ps1
```

### Start browser
```text
browser start
```

### Open a page
```text
browser open: https://example.com
```

### Get title
```text
browser title
```

### Read page text
```text
browser text
```

### Fill and submit a search field
```text
browser fill: input[name='q'] ::: jarvis local agent
browser press: input[name='q'] ::: Enter
```

### Screenshot
```text
browser screenshot: data/browser/example.png
```

### Close browser
```text
browser close
```

## Switching from mock mode to real GGUF inference

Open `.env` and set:
```env
DEFAULT_MODEL_PROVIDER=llama_cpp
```

Make sure your GGUF file names match:
```env
DEFAULT_FAST_MODEL=Qwen2.5-3B-Instruct-Q4_K_M.gguf
DEFAULT_MAIN_MODEL=Qwen2.5-7B-Instruct-Q4_K_M.gguf
```

## Notes
- current tool use is explicit/prefix-based for reliability
- later phases can let the planner decide tools automatically
- workspace_root is restricted so file operations stay inside the project scope
- browser mode is currently single-session and Chromium-based
- if browser start fails, run `python -m playwright install chromium` inside the venv
