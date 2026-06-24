# JARVIS Hotfix Sync Bundle

This bundle contains the latest source-only project files from the Arena workspace.

## What to do on your Windows machine
1. Make a safety copy of your local project folder.
2. Extract `jarvis-pass10-hotfix-source.zip` into your local project root:
   - `D:\00000. Boss level JARVIS\`
3. Allow overwrite for source files.
4. Do **not** copy over your local `.venv`.
5. Do **not** delete your local `data/` unless you want a clean reset.
6. After extracting, run:
   ```powershell
   .\bootstrap.ps1
   .\scripts\start-api.ps1
   ```
7. Open:
   - `http://127.0.0.1:8000/ui/app-shell`

## Optional cleanup of old remembered wrapper state
If you still see old `/home/user/...` paths in the shell, remove:
```powershell
Remove-Item .\data\memory\app_wrapper_state.json -Force -ErrorAction SilentlyContinue
```
Then restart the API.
