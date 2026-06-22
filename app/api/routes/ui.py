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
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='card'><div class='head'>JARVIS • Navigation</div><div class='body'><div class='pill'>Today</div><div class='pill'>Progress</div><div class='pill'>Browser</div><div class='pill'>Voice</div><div class='pill'>Tasks</div><div class='pill'>Sessions</div></div></div>
    <div class='card term'><div class='head'>JARVIS Console Shell</div><div class='output'>✅ Success — app_recipe on project.review\nJARVIS reviewed your project and opened the README preview.\nNext: start coding</div><div class='prompt'>jarvis&gt; show me today's focus</div></div>
    <div class='card'><div class='head'>Command Center</div><div class='body'><strong>Phase 5:</strong> 75% complete<br><br><strong>Voice/Orb:</strong><br>starter integrated<br><br><strong>Next actions:</strong><br>• validate browser launch<br>• start packaged shell</div></div>
  </div>
</body>
</html>
"""


@router.get("/app-shell", response_class=HTMLResponse)
def app_shell() -> str:
    return """
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>JARVIS App Shell</title>
  <style>
    :root {
      --bg: #08101f;
      --panel: #11192f;
      --panel-2: #0d1527;
      --border: #233459;
      --text: #e9f1ff;
      --muted: #9db1d8;
      --accent: #6ed1ff;
      --accent2: #9cf7c8;
      --danger: #ff8b8b;
      --warning: #ffd36e;
      --shadow: 0 10px 35px rgba(0,0,0,.28);
      --radius: 16px;
    }
    * { box-sizing: border-box; }
    body { margin:0; background: radial-gradient(circle at top, #0f1d39 0%, var(--bg) 42%); color: var(--text); font-family: Inter, Segoe UI, Arial, sans-serif; height:100vh; overflow:hidden; }
    .app { display:grid; grid-template-columns: 250px 1fr 340px; gap:14px; padding:14px; height:100vh; }
    .panel { background: linear-gradient(180deg, rgba(17,26,47,.96), rgba(12,19,35,.96)); border:1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); overflow:hidden; display:flex; flex-direction:column; min-height:0; }
    .head { padding:12px 14px; border-bottom:1px solid var(--border); font-size:13px; letter-spacing:.04em; color: var(--accent); font-weight:800; text-transform:uppercase; }
    .body { padding:14px; overflow:auto; min-height:0; }
    .nav-button, .chip, button { border:1px solid #28406b; background:#14203a; color:var(--text); border-radius:999px; padding:8px 11px; cursor:pointer; font-size:12px; }
    .nav-button { width:100%; text-align:left; margin:0 0 10px 0; }
    .nav-button:hover, .chip:hover, button:hover { background:#1b2b4d; }
    .term { display:flex; flex-direction:column; }
    .feed { flex:1; overflow:auto; padding:14px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; white-space:pre-wrap; line-height:1.45; }
    .entry { border:1px solid #233459; border-radius:14px; padding:12px; margin-bottom:12px; background:rgba(16,24,43,.8); }
    .entry .role { font-size:12px; color:var(--accent); margin-bottom:6px; }
    .entry .text { font-size:13px; color:var(--text); }
    .composer { border-top:1px solid var(--border); padding:12px; display:flex; gap:10px; align-items:center; }
    input[type=text] { flex:1; border-radius:12px; border:1px solid #2a406b; background:#0d1527; color:var(--text); padding:12px 14px; outline:none; }
    .grid-two { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    .metric, .item { border:1px solid #233459; background:var(--panel-2); border-radius:14px; padding:12px; }
    .small-title { font-size:12px; text-transform:uppercase; color:var(--muted); margin-bottom:10px; letter-spacing:.04em; }
    .big { font-size:28px; font-weight:800; color:var(--accent2); }
    .chips { display:flex; flex-wrap:wrap; gap:8px; }
    .list { display:flex; flex-direction:column; gap:10px; }
    .orb-wrap { display:flex; align-items:center; gap:14px; }
    .orb { width:58px; height:58px; border-radius:50%; background:radial-gradient(circle at 35% 35%, #a5ecff 0%, #63b9ff 40%, #2c4b9a 100%); box-shadow:0 0 24px rgba(110,209,255,.55); animation:pulse 2.6s infinite ease-in-out; }
    @keyframes pulse { 0%{transform:scale(1);opacity:.95} 50%{transform:scale(1.06);opacity:1} 100%{transform:scale(1);opacity:.95} }
    .modal-backdrop { position:fixed; inset:0; background:rgba(2,6,14,.72); display:none; align-items:center; justify-content:center; z-index:50; }
    .modal { width:min(560px, 92vw); background:#11192f; border:1px solid #28406b; border-radius:16px; box-shadow:var(--shadow); overflow:hidden; }
    .modal .head { color:#ffb0b0; }
    .modal .body { padding:16px; }
    .actions { display:flex; gap:10px; justify-content:flex-end; padding:12px 16px 16px; }
    .danger { border-color:#7d2f2f; background:#3a1515; }
    .hidden { display:none !important; }
    @media (max-width:1100px){ .app { grid-template-columns:220px 1fr; } .right { grid-column:1 / -1; height:340px; } }
  </style>
</head>
<body>
  <div class='app'>
    <aside class='panel'>
      <div class='head'>Navigation</div>
      <div class='body'>
        <button class='nav-button' onclick='loadAll()'>Refresh Dashboard</button>
        <button class='nav-button' onclick='loadToday()'>Today</button>
        <button class='nav-button' onclick='loadProgress()'>Progress</button>
        <button class='nav-button' onclick='loadPhase4()'>Phase 4</button>
        <button class='nav-button' onclick='loadPhase5()'>Phase 5</button>
        <button class='nav-button' onclick='loadBrowser()'>Browser</button>
        <button class='nav-button' onclick='loadValidation()'>Validation</button>
        <div class='small-title' style='margin-top:14px'>Quick Commands</div>
        <div class='chips'>
          <button class='chip' onclick="sendPreset('show me today')">today</button>
          <button class='chip' onclick="sendPreset('show my progress')">progress</button>
          <button class='chip' onclick="sendPreset('review this project')">review</button>
          <button class='chip' onclick="sendPreset('show browser options')">browser</button>
          <button class='chip' onclick="sendPreset('show my tasks')">tasks</button>
        </div>
      </div>
    </aside>

    <main class='panel'>
      <div class='head'>JARVIS Shell</div>
      <div class='feed' id='feed'></div>
      <div class='composer'>
        <input id='prompt' type='text' placeholder='Type a command or plain-English goal…' onkeydown='if(event.key==="Enter") sendPrompt()'>
        <button onclick='sendPrompt()'>Send</button>
      </div>
    </main>

    <section class='panel right'>
      <div class='head'>Command Center</div>
      <div class='body'>
        <div class='grid-two'>
          <div class='metric'>
            <div class='small-title'>Phase 4</div>
            <div class='big' id='phase4Pct'>--</div>
            <div class='tiny' id='phase4Meta'>loading…</div>
          </div>
          <div class='metric'>
            <div class='small-title'>Phase 5</div>
            <div class='big' id='phase5Pct'>--</div>
            <div class='tiny' id='phase5Meta'>loading…</div>
          </div>
        </div>
        <div style='height:12px'></div>
        <div class='metric'>
          <div class='small-title'>Voice / Orb</div>
          <div class='orb-wrap'>
            <div class='orb'></div>
            <div id='voiceBlock' class='tiny'>loading…</div>
          </div>
        </div>
        <div style='height:12px'></div>
        <div class='small-title'>Focus</div>
        <div id='focusBlock' class='tiny'>loading…</div>
        <div class='small-title' style='margin-top:12px'>Today</div>
        <div id='todayBlock' class='tiny'>loading…</div>
        <div class='small-title' style='margin-top:12px'>Browser</div>
        <div id='browserBlock' class='tiny'>loading…</div>
        <div class='small-title' style='margin-top:12px'>Tasks</div>
        <div id='tasksBlock' class='list'></div>
        <div class='small-title' style='margin-top:12px'>Recent Sessions</div>
        <div id='sessionsBlock' class='list'></div>
      </div>
    </section>
  </div>

  <div class='modal-backdrop' id='approvalModal'>
    <div class='modal'>
      <div class='head'>Approval Required</div>
      <div class='body'>
        <div id='approvalRisk'></div>
        <div style='height:8px'></div>
        <div id='approvalReason' class='tiny'></div>
        <div style='height:12px'></div>
        <div class='tiny'>Command:</div>
        <div id='approvalCommand' style='margin-top:6px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; white-space:pre-wrap;'></div>
      </div>
      <div class='actions'>
        <button onclick='closeApproval(false)'>Cancel</button>
        <button class='danger' onclick='closeApproval(true)'>Confirm</button>
      </div>
    </div>
  </div>

  <script>
    let sessionId = null;
    let pendingCommand = null;
    const feed = document.getElementById('feed');
    const promptInput = document.getElementById('prompt');
    const approvalModal = document.getElementById('approvalModal');

    function appendEntry(role, text) {
      const entry = document.createElement('div');
      entry.className = 'entry';
      entry.innerHTML = `<div class="role">${role}</div><div class="text"></div>`;
      entry.querySelector('.text').textContent = text;
      feed.appendChild(entry);
      feed.scrollTop = feed.scrollHeight;
    }

    async function api(path, options={}) {
      const res = await fetch(path, options);
      return await res.json();
    }

    async function classifyCommand(command) {
      const q = encodeURIComponent(command);
      return await api(`/operator/classify?command=${q}`);
    }

    function showApproval(command, info) {
      pendingCommand = command;
      document.getElementById('approvalRisk').textContent = `Risk: ${info.risk} (${info.label})`;
      document.getElementById('approvalReason').textContent = info.reason || '';
      document.getElementById('approvalCommand').textContent = command;
      approvalModal.style.display = 'flex';
    }

    function closeApproval(confirmed) {
      approvalModal.style.display = 'none';
      if (confirmed && pendingCommand) {
        const cmd = pendingCommand;
        pendingCommand = null;
        actuallySend(cmd);
      } else {
        pendingCommand = null;
      }
    }

    async function sendPrompt() {
      const message = promptInput.value.trim();
      if (!message) return;
      promptInput.value = '';
      const info = await classifyCommand(message);
      if (info.requires_confirmation) {
        showApproval(message, info);
        return;
      }
      await actuallySend(message);
    }

    async function actuallySend(message) {
      appendEntry('you', message);
      const payload = { message, session_id: sessionId, use_tools: true };
      const data = await api('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      sessionId = data.session_id || sessionId;
      appendEntry('jarvis', data.reply || 'No reply');
      loadAll();
    }

    function sendPreset(text) {
      promptInput.value = text;
      sendPrompt();
    }

    async function loadToday() {
      const today = await api('/quick-actions/today');
      document.getElementById('todayBlock').textContent = today.plain_english || 'No today brief.';
      const focus = today.focus || {};
      document.getElementById('focusBlock').textContent = focus.headline || 'No current focus.';
    }

    async function loadProgress() {
      const phase = await api('/progress/phase4');
      document.getElementById('phase4Pct').textContent = `${phase.percent ?? '--'}%`;
      document.getElementById('phase4Meta').textContent = `${phase.completed ?? 0}/${phase.total ?? 0} tasks complete`;
      const phase5 = await api('/progress/phase5');
      document.getElementById('phase5Pct').textContent = `${phase5.percent ?? '--'}%`;
      document.getElementById('phase5Meta').textContent = `${phase5.completed ?? 0}/${phase5.total ?? 0} tasks complete`;
    }

    async function loadPhase4() {
      const phase = await api('/progress/phase4');
      appendEntry('system', `Phase 4: ${phase.percent}% complete\nRemaining: ${(phase.remaining || []).join(', ') || 'none'}`);
    }

    async function loadPhase5() {
      const phase = await api('/progress/phase5');
      appendEntry('system', `Phase 5: ${phase.percent}% complete\nRemaining: ${(phase.remaining || []).join(', ') || 'none'}`);
    }

    async function loadBrowser() {
      const browser = await api('/quick-actions/progress');
      const ctx = browser.browser || {};
      let text = ctx.plain_english || 'No browser info.';
      if (ctx.url) text += `\nURL: ${ctx.url}`;
      if (ctx.preferred_browser) text += `\nPreferred: ${ctx.preferred_browser}`;
      if (ctx.available_browsers?.length) {
        text += `\nOptions: ${ctx.available_browsers.map(x => x.name).join(', ')}`;
      }
      document.getElementById('browserBlock').textContent = text;
    }

    async function loadVoice() {
      const voice = await api('/voice/status');
      let text = voice.plain_english || 'Voice status unavailable.';
      text += `\nSTT ready: ${voice.stt_ready ? 'yes' : 'no'}`;
      text += `\nTTS ready: ${voice.tts_ready ? 'yes' : 'no'}`;
      document.getElementById('voiceBlock').textContent = text;
    }

    async function loadTasks() {
      const tasks = await api('/tasks?status=open&limit=5');
      const root = document.getElementById('tasksBlock');
      root.innerHTML = '';
      const items = tasks.items || [];
      if (!items.length) {
        root.innerHTML = '<div class="tiny">No open tasks.</div>';
        return;
      }
      items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `<strong>#${item.id} ${item.title}</strong><span class='tiny'>${item.priority} • ${item.status}</span>`;
        root.appendChild(div);
      });
    }

    async function loadSessions() {
      const sessions = await api('/sessions/list?limit=5');
      const root = document.getElementById('sessionsBlock');
      root.innerHTML = '';
      const items = sessions.items || [];
      if (!items.length) {
        root.innerHTML = '<div class="tiny">No sessions yet.</div>';
        return;
      }
      items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `<strong>${item.title || item.session_id}</strong><span class='tiny'>${item.session_id.slice(0,8)} • ${item.message_count} msgs</span>`;
        div.onclick = () => { sessionId = item.session_id; appendEntry('system', `Switched session to ${item.session_id}`); };
        root.appendChild(div);
      });
    }

    async function loadTimeline() {
      if (!sessionId) return;
      const data = await api(`/audit/timeline?limit=6&session_id=${encodeURIComponent(sessionId)}`);
      const items = data.items || [];
      if (!items.length) return;
      appendEntry('timeline', items.map(x => `${x.event_type}: ${x.preview}`).join('\n'));
    }

    async function loadValidation() {
      const data = await api('/validation/report');
      appendEntry('validation', JSON.stringify({
        platform: data.platform,
        python: data.python_version,
        blockers: data.blockers,
        next_steps: data.next_steps
      }, null, 2));
    }

    async function loadAll() {
      await loadToday();
      await loadProgress();
      await loadBrowser();
      await loadVoice();
      await loadTasks();
      await loadSessions();
    }

    loadAll();
  </script>
</body>
</html>
"""
