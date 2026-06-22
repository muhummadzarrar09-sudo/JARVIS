from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/ui", tags=["ui"])


@router.get("/shell-preview", response_class=HTMLResponse)
def shell_preview() -> str:
    return """
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>JARVIS Shell Preview</title>
  <style>
    body { margin:0; background:#0b1020; color:#e8f0ff; font-family:Inter,Segoe UI,Arial,sans-serif; }
    .wrap { display:grid; grid-template-columns: 280px 1fr 320px; gap:14px; padding:14px; height:100vh; box-sizing:border-box; }
    .card { background:#11192f; border:1px solid #203153; border-radius:14px; box-shadow:0 10px 30px rgba(0,0,0,.3); overflow:hidden; }
    .head { padding:12px 14px; font-weight:700; font-size:14px; color:#8ec5ff; border-bottom:1px solid #203153; }
    .body { padding:14px; font-size:13px; line-height:1.45; }
    .pill { display:inline-block; padding:6px 10px; border-radius:999px; background:#172443; margin:4px 6px 0 0; color:#dbe9ff; }
    .term { display:flex; flex-direction:column; }
    .output { flex:1; padding:14px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; white-space:pre-wrap; color:#cfe1ff; }
    .prompt { border-top:1px solid #203153; padding:12px 14px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; color:#7ed7ff; }
    .accent { color:#9cf7c8; }
    ul { margin:8px 0 0 18px; padding:0; }
    li { margin:6px 0; }
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='card'>
      <div class='head'>JARVIS • Navigation</div>
      <div class='body'>
        <div class='pill'>Today</div>
        <div class='pill'>Progress</div>
        <div class='pill'>Browser</div>
        <div class='pill'>Tasks</div>
        <div class='pill'>Sessions</div>
        <div class='pill'>Phase 4</div>
        <ul>
          <li>Project context</li>
          <li>Wrapper status</li>
          <li>Replay / timeline</li>
          <li>Operator approvals</li>
        </ul>
      </div>
    </div>
    <div class='card term'>
      <div class='head'>JARVIS Console Shell</div>
      <div class='output'>
<span class='accent'>✅ Success</span> — app_recipe on project.review
JARVIS reviewed your project and opened the README preview.
Next: start coding

Suggested:
• show me today's focus
• show my tasks
• show browser options
• start my workday
      </div>
      <div class='prompt'>jarvis&gt; <span style='color:#dbe9ff'>show me today's focus</span></div>
    </div>
    <div class='card'>
      <div class='head'>Command Center</div>
      <div class='body'>
        <strong>Phase 4:</strong> 81.8% complete<br><br>
        <strong>Open tasks:</strong><br>
        • Review wrappers<br>
        • Validate browser launch<br><br>
        <strong>Browser:</strong><br>
        Preferred: chrome<br>
        Remembered page: https://example.com<br><br>
        <strong>Next actions:</strong><br>
        • start coding<br>
        • show my project files<br>
        • show me the current page
      </div>
    </div>
  </div>
</body>
</html>
"""
