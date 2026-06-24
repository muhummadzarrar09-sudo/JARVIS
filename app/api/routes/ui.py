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
    <div class='card'><div class='head'>JARVIS • Navigation</div><div class='body'><div class='pill'>Today</div><div class='pill'>Progress</div><div class='pill'>Browser</div><div class='pill'>Models</div><div class='pill'>Voice</div><div class='pill'>Tasks</div></div></div>
    <div class='card term'><div class='head'>JARVIS Console Shell</div><div class='output'>✅ Success — app_recipe on project.review\nJARVIS reviewed your project and opened the README preview.\nNext: start coding</div><div class='prompt'>jarvis&gt; show me today's focus</div></div>
    <div class='card'><div class='head'>Command Center</div><div class='body'><strong>Phase 4:</strong> 100.0% complete<br><br><strong>Phase 5:</strong> 100.0% complete<br><br><strong>Hardening target:</strong><br>real browser launch + real shell messaging + local GGUF readiness</div></div>
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
      --danger: #ff9b9b;
      --warning: #ffd36e;
      --good: #9cf7c8;
      --shadow: 0 10px 35px rgba(0,0,0,.28);
      --radius: 16px;
    }
    * { box-sizing: border-box; }
    body { margin:0; background: radial-gradient(circle at top, #0f1d39 0%, var(--bg) 42%); color: var(--text); font-family: Inter, Segoe UI, Arial, sans-serif; height:100vh; overflow:hidden; }
    .app { display:grid; grid-template-columns: 260px 1fr 360px; gap:14px; padding:14px; height:100vh; }
    .panel { background: linear-gradient(180deg, rgba(17,26,47,.96), rgba(12,19,35,.96)); border:1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); overflow:hidden; display:flex; flex-direction:column; min-height:0; }
    .head { padding:12px 14px; border-bottom:1px solid var(--border); font-size:13px; letter-spacing:.04em; color: var(--accent); font-weight:800; text-transform:uppercase; }
    .subhead { color:var(--muted); font-size:12px; }
    .body { padding:14px; overflow:auto; min-height:0; }
    .nav-button, .chip, button { border:1px solid #28406b; background:#14203a; color:var(--text); border-radius:999px; padding:8px 11px; cursor:pointer; font-size:12px; }
    .nav-button { width:100%; text-align:left; margin:0 0 10px 0; }
    .nav-button:hover, .chip:hover, button:hover { background:#1b2b4d; }
    .term { display:flex; flex-direction:column; }
    .feed { flex:1; overflow:auto; padding:14px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; white-space:pre-wrap; line-height:1.45; }
    .entry { border:1px solid #233459; border-radius:14px; padding:12px; margin-bottom:12px; background:rgba(16,24,43,.82); }
    .entry .role { font-size:12px; color:var(--accent); margin-bottom:6px; text-transform:uppercase; letter-spacing:.04em; }
    .entry.error { border-color:#6f2f3d; background:rgba(50,18,24,.82); }
    .entry.error .role { color:#ffafb9; }
    .entry .text { font-size:13px; color:var(--text); }
    .composer { border-top:1px solid var(--border); padding:12px; display:flex; flex-direction:column; gap:10px; }
    .composer-row { display:flex; gap:10px; align-items:flex-end; }
    textarea { flex:1; min-height:84px; resize:vertical; border-radius:14px; border:1px solid #2a406b; background:#0d1527; color:var(--text); padding:12px 14px; outline:none; font:inherit; }
    .grid-two { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    .metric, .item, .stack { border:1px solid #233459; background:var(--panel-2); border-radius:14px; padding:12px; }
    .small-title { font-size:12px; text-transform:uppercase; color:var(--muted); margin-bottom:10px; letter-spacing:.04em; }
    .big { font-size:28px; font-weight:800; color:var(--accent2); }
    .chips { display:flex; flex-wrap:wrap; gap:8px; }
    .list { display:flex; flex-direction:column; gap:10px; }
    .tiny { color:var(--muted); font-size:12px; line-height:1.45; }
    .orb-wrap { display:flex; align-items:center; gap:14px; }
    .orb { width:58px; height:58px; border-radius:50%; background:radial-gradient(circle at 35% 35%, #a5ecff 0%, #63b9ff 40%, #2c4b9a 100%); box-shadow:0 0 24px rgba(110,209,255,.55); animation:pulse 2.6s infinite ease-in-out; }
    @keyframes pulse { 0%{transform:scale(1);opacity:.95} 50%{transform:scale(1.06);opacity:1} 100%{transform:scale(1);opacity:.95} }
    .modal-backdrop { position:fixed; inset:0; background:rgba(2,6,14,.72); display:none; align-items:center; justify-content:center; z-index:50; }
    .modal { width:min(560px, 92vw); background:#11192f; border:1px solid #28406b; border-radius:16px; box-shadow:var(--shadow); overflow:hidden; }
    .modal .head { color:#ffb0b0; }
    .modal .body { padding:16px; }
    .actions { display:flex; gap:10px; justify-content:flex-end; padding:12px 16px 16px; }
    .danger { border-color:#7d2f2f; background:#3a1515; }
    .row { display:flex; gap:10px; align-items:center; justify-content:space-between; }
    .mono { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; }
    .session-button { width:100%; text-align:left; border-radius:14px; padding:10px 12px; background:#101a30; border:1px solid #233459; color:var(--text); cursor:pointer; }
    .session-button:hover { background:#172443; }
    .separator { height:12px; }
    .statusbar { display:flex; gap:8px; flex-wrap:wrap; }
    .badge { display:inline-block; padding:4px 10px; border-radius:999px; font-size:11px; border:1px solid #315287; color:#dce9ff; }
    .good { border-color:#2f7055; color:#b7f3d6; }
    .warn { border-color:#8a6c22; color:#ffe59c; }
    .bad { border-color:#823434; color:#ffc0c0; }
    select, input[type=number] { width:100%; border-radius:12px; border:1px solid #2a406b; background:#0d1527; color:var(--text); padding:10px 12px; outline:none; }
    .drawer { position:fixed; top:0; right:0; width:min(420px, 96vw); height:100vh; background:#0b1324; border-left:1px solid var(--border); box-shadow:var(--shadow); transform:translateX(100%); transition:transform .2s ease; z-index:60; display:flex; flex-direction:column; }
    .drawer.open { transform:translateX(0); }
    .drawer-head { padding:14px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; color:var(--accent); font-weight:800; text-transform:uppercase; }
    .drawer-body { padding:14px; overflow:auto; display:flex; flex-direction:column; gap:10px; }
    .toast-wrap { position:fixed; left:20px; bottom:20px; display:flex; flex-direction:column; gap:10px; z-index:70; }
    .toast { min-width:260px; max-width:420px; border:1px solid #28406b; background:#101a30; color:var(--text); border-radius:14px; padding:12px 14px; box-shadow:var(--shadow); }
    .toast.error { border-color:#823434; }
    .banner { margin:12px 14px 0 14px; border:1px solid #2b4572; background:#101b33; border-radius:14px; padding:12px 14px; font-size:12px; line-height:1.45; }
    .maintenance-status { margin-top:10px; }
    .overlay { position:fixed; inset:0; background:rgba(4,8,16,.72); display:flex; align-items:center; justify-content:center; z-index:80; }
    .overlay-card { width:min(520px, 92vw); background:#101a30; border:1px solid #28406b; border-radius:18px; padding:18px; box-shadow:var(--shadow); }
    .drawer.left { left:0; right:auto; transform:translateX(-100%); border-left:none; border-right:1px solid var(--border); }
    .drawer.left.open { transform:translateX(0); }
    .hidden { display:none !important; }
    @media (max-width:1180px){ .app { grid-template-columns:230px 1fr; } .right { grid-column:1 / -1; height:420px; } }
  </style>
</head>
<body>
  <div class='app'>
    <aside class='panel'>
      <div class='head'>Navigation</div>
      <div class='body'>
        <button class='nav-button' onclick='bootShell()'>Refresh Dashboard</button>
        <button class='nav-button' onclick='showSnapshot("today")'>Today Snapshot</button>
        <button class='nav-button' onclick='showSnapshot("browser")'>Browser Snapshot</button>
        <button class='nav-button' onclick='showSnapshot("models")'>Model Snapshot</button>
        <button class='nav-button' onclick='showSnapshot("validation")'>Validation Snapshot</button>
        <button class='nav-button' onclick='showSnapshot("database")'>Database Snapshot</button>
        <button class='nav-button' onclick='showSnapshot("maintenance")'>Maintenance Snapshot</button>
        <button class='nav-button' onclick='showSnapshot("timeline")'>Timeline Snapshot</button>
        <button class='nav-button' onclick='toggleMaintenanceDrawer(true)'>Open Maintenance Drawer</button>
        <button class='nav-button' onclick='toggleErrorDrawer(true)'>Open Error Drawer</button>

        <div class='small-title' style='margin-top:14px'>Quick Commands</div>
        <div class='chips' id='quickChips'></div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Status</div>
          <div class='statusbar' id='statusBar'></div>
          <div class='tiny' id='sessionBadge' style='margin-top:8px;'>loading…</div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Recommended</div>
          <div id='recommendedBlock' class='chips'></div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Maintenance</div>
          <div class='chips'>
            <button class='chip' onclick='backupDatabase()'>backup db</button>
            <button class='chip' onclick='vacuumDatabase()'>vacuum db</button>
            <button class='chip' onclick='rotateAudit()'>rotate audit</button>
            <button class='chip' onclick='pruneAudit()'>prune audit</button>
            <button class='chip' onclick='exportRecoveryPack()'>export pack</button>
            <button class='chip' onclick='cleanupSessions("light")'>cleanup light</button>
            <button class='chip' onclick='cleanupSessions("normal")'>cleanup normal</button>
            <button class='chip' onclick='cleanupSessions("aggressive")'>cleanup hard</button>
            <button class='chip' onclick='previewCleanup("light")'>preview light</button>
            <button class='chip' onclick='previewCleanup("normal")'>preview normal</button>
            <button class='chip' onclick='previewCleanup("aggressive")'>preview hard</button>
            <button class='chip' onclick='preloadModel("fast")'>preload fast</button>
            <button class='chip' onclick='preloadModel("main")'>preload main</button>
          </div>
          <div class='separator'></div>
          <div class='tiny'>Audit archive retention</div>
          <input id='auditKeepInput' type='number' min='0' max='200' value='10'>
          <div class='separator'></div>
          <div class='tiny'>Custom session cleanup</div>
          <input id='cleanupKeepRecentInput' type='number' min='0' max='1000' value='25'>
          <div class='separator'></div>
          <input id='cleanupEmptyDaysInput' type='number' min='0' max='3650' value='7'>
          <div class='separator'></div>
          <input id='cleanupInactiveDaysInput' type='number' min='0' max='3650' value='90'>
          <div class='separator'></div>
          <div class='chips'>
            <button class='chip' onclick='previewCustomCleanup()'>preview custom</button>
            <button class='chip' onclick='runCustomCleanup()'>run custom</button>
            <button class='chip' onclick='saveMaintenancePrefs()'>save prefs</button>
          </div>
          <div class='separator'></div>
          <div class='tiny'>Restore DB backup</div>
          <select id='dbBackupSelect'></select>
          <div class='separator'></div>
          <div class='chips'>
            <button class='chip' onclick='restoreDatabase()'>restore db</button>
            <button class='chip' onclick='downloadSelectedBackup()'>download backup</button>
            <button class='chip' onclick='deleteSelectedBackup()'>delete backup</button>
            <button class='chip' onclick='refreshMaintenance()'>refresh maintenance</button>
          </div>
          <div class='separator'></div>
          <div class='tiny'>Preview audit archive</div>
          <select id='auditArchiveSelect'></select>
          <div class='separator'></div>
          <div class='chips'>
            <button class='chip' onclick='previewAuditArchive()'>preview archive</button>
            <button class='chip' onclick='downloadAuditArchive()'>download archive</button>
            <button class='chip' onclick='deleteAuditArchive()'>delete archive</button>
          </div>
          <div class='separator'></div>
          <div class='tiny'>Recovery pack</div>
          <select id='recoveryPackSelect'></select>
          <div class='separator'></div>
          <div class='chips'>
            <button class='chip' onclick='previewRecoveryPack()'>preview pack</button>
            <button class='chip' onclick='importRecoveryPack()'>import pack</button>
            <button class='chip' onclick='downloadRecoveryPack()'>download pack</button>
            <button class='chip' onclick='deleteRecoveryPack()'>delete pack</button>
          </div>
          <div class='maintenance-status tiny' id='maintenanceStatus'>loading…</div>
        </div>
      </div>
    </aside>

    <main class='panel term'>
      <div class='head row'>
        <span>JARVIS Shell</span>
        <span class='subhead' id='shellMeta'>local command center</span>
      </div>
      <div class='banner' id='startupBanner'>Booting local startup diagnostics…</div>
      <div class='feed' id='feed'></div>
      <form class='composer' id='composerForm'>
        <div class='tiny'>Enter = send • Shift+Enter = newline • Ctrl/Cmd+Enter = send • / = focus composer</div>
        <div class='composer-row'>
          <textarea id='prompt' placeholder='Type a command or plain-English goal…'></textarea>
        </div>
        <div class='composer-row'>
          <button type='submit' id='sendButton'>Send</button>
          <button type='button' onclick='clearComposer()'>Clear</button>
          <button type='button' onclick='retryLastPrompt()'>Retry Last</button>
          <div class='tiny' id='composerStatus'>Ready.</div>
        </div>
      </form>
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

        <div class='separator'></div>
        <div class='metric'>
          <div class='small-title'>Voice / Orb</div>
          <div class='orb-wrap'>
            <div class='orb'></div>
            <div id='voiceBlock' class='tiny'>loading…</div>
          </div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Model Runtime</div>
          <div id='modelBlock' class='tiny'>loading…</div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Model Controls</div>
          <div class='tiny'>Fast model</div>
          <select id='fastModelSelect'></select>
          <div class='separator'></div>
          <div class='tiny'>Main model</div>
          <select id='mainModelSelect'></select>
          <div class='separator'></div>
          <div class='chips'>
            <button class='chip' onclick='applyModelSelection()'>apply models</button>
            <button class='chip' onclick='useLocalModels()'>use local</button>
            <button class='chip' onclick='useMockModels()'>use mock</button>
          </div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Focus</div>
          <div id='focusBlock' class='tiny'>loading…</div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Today</div>
          <div id='todayBlock' class='tiny'>loading…</div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Browser</div>
          <div id='browserBlock' class='tiny'>loading…</div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Validation</div>
          <div id='validationBlock' class='tiny'>loading…</div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Maintenance Doctor</div>
          <div id='maintenanceDoctorBlock' class='tiny'>loading…</div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Database</div>
          <div id='databaseBlock' class='tiny'>loading…</div>
        </div>

        <div class='separator'></div>
        <div class='stack'>
          <div class='small-title'>Operator</div>
          <div id='operatorBlock' class='tiny'>loading…</div>
        </div>

        <div class='separator'></div>
        <div class='small-title'>Tasks</div>
        <div id='tasksBlock' class='list'></div>

        <div class='separator'></div>
        <div class='small-title'>Recent Sessions</div>
        <div id='sessionsBlock' class='list'></div>

        <div class='separator'></div>
        <div class='small-title'>Recent Timeline</div>
        <div id='timelineBlock' class='list'></div>

        <div class='separator'></div>
        <div class='small-title'>Maintenance Events</div>
        <div id='maintenanceEventsBlock' class='list'></div>
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
        <div class='tiny'>Command</div>
        <div id='approvalCommand' style='margin-top:6px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; white-space:pre-wrap;'></div>
      </div>
      <div class='actions'>
        <button onclick='closeApproval(false)'>Cancel</button>
        <button class='danger' onclick='closeApproval(true)'>Confirm</button>
      </div>
    </div>
  </div>

  <div class='drawer left' id='maintenanceDrawer'>
    <div class='drawer-head'>
      <span>Maintenance Drawer</span>
      <button onclick='toggleMaintenanceDrawer(false)'>Close</button>
    </div>
    <div class='drawer-body' id='maintenanceDrawerBody'></div>
  </div>

  <div class='drawer' id='errorDrawer'>
    <div class='drawer-head'>
      <span>Error Drawer</span>
      <button onclick='toggleErrorDrawer(false)'>Close</button>
    </div>
    <div class='drawer-body' id='errorDrawerBody'></div>
  </div>

  <div class='overlay hidden' id='connectionOverlay'>
    <div class='overlay-card'>
      <div class='small-title'>Connection / Recovery</div>
      <div class='tiny' id='connectionOverlayText'>JARVIS is checking the local command center connection…</div>
      <div class='separator'></div>
      <div class='chips'>
        <button class='chip' onclick='manualReconnect()'>reconnect</button>
        <button class='chip' onclick='toggleMaintenanceDrawer(true)'>open maintenance drawer</button>
        <button class='chip' onclick='toggleErrorDrawer(true)'>open error drawer</button>
      </div>
    </div>
  </div>

  <div class='toast-wrap' id='toastWrap'></div>

  <script>
    let sessionId = null;
    let pendingCommand = null;
    let latestShellState = null;
    let lastPrompt = '';
    let sending = false;

    const feed = document.getElementById('feed');
    const promptInput = document.getElementById('prompt');
    const approvalModal = document.getElementById('approvalModal');
    const composerForm = document.getElementById('composerForm');
    const sendButton = document.getElementById('sendButton');
    const toastWrap = document.getElementById('toastWrap');
    const maintenanceDrawer = document.getElementById('maintenanceDrawer');
    const maintenanceDrawerBody = document.getElementById('maintenanceDrawerBody');
    const errorDrawer = document.getElementById('errorDrawer');
    const errorDrawerBody = document.getElementById('errorDrawerBody');
    const connectionOverlay = document.getElementById('connectionOverlay');
    const storageKeys = { draft: 'jarvis.shell.draft', session: 'jarvis.shell.session', cachedState: 'jarvis.shell.cachedState', errors: 'jarvis.shell.errors', warm: 'jarvis.shell.warm', maintenancePrefs: 'jarvis.shell.maintenancePrefs', reconnects: 'jarvis.shell.reconnects', maintenanceOps: 'jarvis.shell.maintenanceOps' };

    function appendEntry(role, text, isError=false) {
      const entry = document.createElement('div');
      entry.className = `entry${isError ? ' error' : ''}`;
      entry.innerHTML = `<div class="role"></div><div class="text"></div>`;
      entry.querySelector('.role').textContent = role;
      entry.querySelector('.text').textContent = text;
      feed.appendChild(entry);
      feed.scrollTop = feed.scrollHeight;
    }

    function setText(id, text) {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    }

    function setComposerStatus(text) {
      setText('composerStatus', text);
    }

    function showToast(message, kind='info') {
      const toast = document.createElement('div');
      toast.className = `toast${kind === 'error' ? ' error' : ''}`;
      toast.textContent = message;
      toastWrap.appendChild(toast);
      setTimeout(() => toast.remove(), 4200);
    }

    function readStorage(key, fallback=null) {
      try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
      } catch {
        return fallback;
      }
    }

    function writeStorage(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
      } catch {}
    }

    function pushReconnectEvent(status, detail) {
      const items = readStorage(storageKeys.reconnects, []);
      items.unshift({ ts: new Date().toISOString(), status, detail });
      writeStorage(storageKeys.reconnects, items.slice(0, 50));
      renderMaintenanceDrawer();
    }

    function pushMaintenanceOp(title, detail) {
      const items = readStorage(storageKeys.maintenanceOps, []);
      items.unshift({ ts: new Date().toISOString(), title, detail });
      writeStorage(storageKeys.maintenanceOps, items.slice(0, 60));
      renderMaintenanceDrawer();
    }

    function pushErrorRecord(title, detail) {
      const items = readStorage(storageKeys.errors, []);
      items.unshift({ ts: new Date().toISOString(), title, detail });
      writeStorage(storageKeys.errors, items.slice(0, 40));
      renderErrorDrawer();
    }

    function renderErrorDrawer() {
      const items = readStorage(storageKeys.errors, []);
      errorDrawerBody.innerHTML = '';
      if (!items.length) {
        errorDrawerBody.innerHTML = '<div class="tiny">No captured shell errors yet.</div>';
        return;
      }
      items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `<strong>${item.title}</strong><div class='tiny'>${item.ts}</div><div class='tiny'>${String(item.detail || '').slice(0, 1200)}</div>`;
        errorDrawerBody.appendChild(div);
      });
    }

    function toggleErrorDrawer(forceOpen=null) {
      const open = forceOpen === null ? !errorDrawer.classList.contains('open') : forceOpen;
      errorDrawer.classList.toggle('open', open);
      if (open) renderErrorDrawer();
    }

    function toggleMaintenanceDrawer(forceOpen=null) {
      const open = forceOpen === null ? !maintenanceDrawer.classList.contains('open') : forceOpen;
      maintenanceDrawer.classList.toggle('open', open);
      if (open) renderMaintenanceDrawer();
    }

    function showConnectionOverlay(message) {
      setText('connectionOverlayText', message);
      connectionOverlay.classList.remove('hidden');
    }

    function hideConnectionOverlay() {
      connectionOverlay.classList.add('hidden');
    }

    async function manualReconnect() {
      pushReconnectEvent('manual_reconnect', 'Manual reconnect requested from the shell overlay.');
      showConnectionOverlay('JARVIS is retrying the local shell connection…');
      await refreshState();
    }

    function cacheShellState(state) {
      writeStorage(storageKeys.cachedState, state);
      if (state?.session_id) writeStorage(storageKeys.session, state.session_id);
    }

    function restoreDraft() {
      const draft = readStorage(storageKeys.draft, '');
      if (draft && !promptInput.value) promptInput.value = draft;
      const savedSession = readStorage(storageKeys.session, null);
      if (savedSession && !sessionId) sessionId = savedSession;
    }

    function applyMaintenancePrefs() {
      const prefs = readStorage(storageKeys.maintenancePrefs, null) || {};
      const setIf = (id, value) => { const el = document.getElementById(id); if (el && value !== undefined && value !== null) el.value = String(value); };
      setIf('auditKeepInput', prefs.auditKeep);
      setIf('cleanupKeepRecentInput', prefs.cleanupKeepRecent);
      setIf('cleanupEmptyDaysInput', prefs.cleanupEmptyDays);
      setIf('cleanupInactiveDaysInput', prefs.cleanupInactiveDays);
    }

    async function saveMaintenancePrefs() {
      const prefs = {
        auditKeep: Number(document.getElementById('auditKeepInput')?.value || 10),
        cleanupKeepRecent: Number(document.getElementById('cleanupKeepRecentInput')?.value || 25),
        cleanupEmptyDays: Number(document.getElementById('cleanupEmptyDaysInput')?.value || 7),
        cleanupInactiveDays: Number(document.getElementById('cleanupInactiveDaysInput')?.value || 90),
      };
      writeStorage(storageKeys.maintenancePrefs, prefs);
      const result = await safeApi('/maintenance/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audit_keep: prefs.auditKeep,
          cleanup_keep_recent: prefs.cleanupKeepRecent,
          cleanup_empty_days: prefs.cleanupEmptyDays,
          cleanup_inactive_days: prefs.cleanupInactiveDays,
        })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Save maintenance preferences failed', result.error || 'unknown error');
        showToast('Saving backend maintenance preferences failed.', 'error');
        return;
      }
      pushMaintenanceOp('maintenance_prefs_save', JSON.stringify(prefs));
      showToast('Maintenance preferences saved.', 'info');
    }

    function customCleanupPayload(dryRun=false) {
      return {
        keep_recent: Number(document.getElementById('cleanupKeepRecentInput')?.value || 25),
        drop_empty_older_than_days: Number(document.getElementById('cleanupEmptyDaysInput')?.value || 7),
        drop_inactive_older_than_days: Number(document.getElementById('cleanupInactiveDaysInput')?.value || 90),
        dry_run: dryRun,
      };
    }

    function setSending(next) {
      sending = next;
      sendButton.disabled = next;
      promptInput.disabled = next;
      setComposerStatus(next ? 'Sending to JARVIS…' : 'Ready.');
    }

    async function api(path, options={}) {
      const url = new URL(path, window.location.origin).toString();
      const res = await fetch(url, options);
      const raw = await res.text();
      let data;
      try {
        data = raw ? JSON.parse(raw) : {};
      } catch {
        data = { raw };
      }
      if (!res.ok) {
        const detail = data?.detail ? JSON.stringify(data.detail) : (data?.raw || raw || `HTTP ${res.status}`);
        throw new Error(detail);
      }
      return data;
    }

    async function safeApi(path, options={}) {
      try {
        return await api(path, options);
      } catch (error) {
        return { ok: false, error: error.message || String(error) };
      }
    }

    async function classifyCommand(command) {
      const result = await safeApi(`/operator/classify?command=${encodeURIComponent(command)}`);
      if (result && result.ok === false && result.error) {
        return { risk: 'low', label: 'fallback', reason: 'Operator classifier was unavailable, so JARVIS will try the command directly.', requires_confirmation: false };
      }
      return result;
    }

    function showApproval(command, info) {
      pendingCommand = command;
      setText('approvalRisk', `Risk: ${info.risk} (${info.label})`);
      setText('approvalReason', info.reason || '');
      setText('approvalCommand', command);
      approvalModal.style.display = 'flex';
    }

    function closeApproval(confirmed) {
      approvalModal.style.display = 'none';
      if (confirmed && pendingCommand) {
        const cmd = pendingCommand;
        pendingCommand = null;
        actuallySend(cmd, true);
      } else {
        pendingCommand = null;
        setComposerStatus('Send cancelled.');
        showToast('Command cancelled.', 'info');
      }
    }

    function clearComposer() {
      promptInput.value = '';
      writeStorage(storageKeys.draft, '');
      promptInput.focus();
      setComposerStatus('Composer cleared.');
    }

    function retryLastPrompt() {
      if (!lastPrompt) {
        setComposerStatus('No previous prompt to retry yet.');
        return;
      }
      promptInput.value = lastPrompt;
      promptInput.focus();
      setComposerStatus('Restored previous prompt. Press Enter to resend.');
    }

    async function sendPrompt() {
      if (sending) return;
      const message = promptInput.value.trim();
      if (!message) {
        setComposerStatus('Type something first.');
        return;
      }
      lastPrompt = message;
      const info = await classifyCommand(message);
      if (info.requires_confirmation) {
        showApproval(message, info);
        return;
      }
      await actuallySend(message);
    }

    async function actuallySend(message, confirmed=false) {
      if (sending) return;
      setSending(true);
      promptInput.value = '';
      writeStorage(storageKeys.draft, '');
      appendEntry('you', message);
      try {
        const payload = { message, session_id: sessionId, use_tools: true, confirmed };
        const data = await api('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        sessionId = data.session_id || sessionId;
        if (data.requires_confirmation && data.confirmation) {
          appendEntry('system', data.reply || 'Approval required before execution.');
          showApproval(message, data.confirmation);
          setComposerStatus('Approval required.');
          showToast('Approval required before JARVIS can continue.', 'info');
          return;
        }
        appendEntry('jarvis', data.reply || 'No reply');
        if (data.steps?.length) {
          appendEntry('system', `Steps: ${data.steps.join(', ')}`);
        }
        await refreshState();
        setComposerStatus('Reply received.');
        showToast('Reply received.', 'info');
      } catch (error) {
        appendEntry('error', `Chat send failed: ${error.message || error}`, true);
        pushErrorRecord('Chat send failed', error.message || String(error));
        showToast('Chat send failed.', 'error');
        setComposerStatus('JARVIS send failed. See error in the feed.');
      } finally {
        setSending(false);
        promptInput.focus();
      }
    }

    function makeChip(label, onClick, rootId) {
      const btn = document.createElement('button');
      btn.className = 'chip';
      btn.textContent = label;
      btn.onclick = onClick;
      document.getElementById(rootId).appendChild(btn);
    }

    function renderQuickCommands(commands) {
      const quick = document.getElementById('quickChips');
      const recs = document.getElementById('recommendedBlock');
      quick.innerHTML = '';
      recs.innerHTML = '';
      const base = Array.from(new Set([...(commands || []), 'show model status', 'use local models']));
      const list = base.slice(0, 8);
      list.forEach(cmd => {
        makeChip(cmd, () => { promptInput.value = cmd; sendPrompt(); }, 'quickChips');
        makeChip(cmd, () => { promptInput.value = cmd; sendPrompt(); }, 'recommendedBlock');
      });
      if (!list.length) {
        quick.innerHTML = '<div class="tiny">No quick commands yet.</div>';
        recs.innerHTML = '<div class="tiny">No suggestions yet.</div>';
      }
    }

    function renderTasks(items) {
      const root = document.getElementById('tasksBlock');
      root.innerHTML = '';
      if (!items || !items.length) {
        root.innerHTML = '<div class="tiny">No open tasks.</div>';
        return;
      }
      items.slice(0, 5).forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `<strong>#${item.id} ${item.title}</strong><div class='tiny'>${item.priority} • ${item.status}</div>`;
        root.appendChild(div);
      });
    }

    function renderSessions(items) {
      const root = document.getElementById('sessionsBlock');
      root.innerHTML = '';
      if (!items || !items.length) {
        root.innerHTML = '<div class="tiny">No sessions yet.</div>';
        return;
      }
      items.slice(0, 5).forEach(item => {
        const btn = document.createElement('button');
        btn.className = 'session-button';
        btn.innerHTML = `<strong>${item.title || item.session_id}</strong><div class='tiny mono'>${item.session_id.slice(0, 8)} • ${item.message_count} msgs</div>`;
        btn.onclick = async () => {
          sessionId = item.session_id;
          appendEntry('system', `Switched session to ${item.session_id}`);
          await refreshState();
        };
        root.appendChild(btn);
      });
    }

    function renderTimeline(items) {
      const root = document.getElementById('timelineBlock');
      root.innerHTML = '';
      if (!items || !items.length) {
        root.innerHTML = '<div class="tiny">No recent timeline events.</div>';
        return;
      }
      items.slice(-5).forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `<strong>${item.event_type}</strong><div class='tiny'>${item.preview || '—'}</div>`;
        root.appendChild(div);
      });
    }

    function renderMaintenanceEvents(maintenance) {
      const root = document.getElementById('maintenanceEventsBlock');
      root.innerHTML = '';
      const combined = [
        ...(maintenance?.database_history || []),
        ...(maintenance?.audit_history || []),
        ...(maintenance?.session_history || []),
      ].sort((a, b) => String(b.ts || '').localeCompare(String(a.ts || '')));
      if (!combined.length) {
        root.innerHTML = '<div class="tiny">No maintenance events yet.</div>';
        return;
      }
      combined.slice(0, 6).forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `<strong>${item.event_type}</strong><div class='tiny'>${item.ts || ''}</div><div class='tiny'>${JSON.stringify(item.payload || {}).slice(0, 220)}</div>`;
        root.appendChild(div);
      });
    }

    function renderMaintenanceDrawer() {
      const root = maintenanceDrawerBody;
      root.innerHTML = '';
      const maintenance = latestShellState?.maintenance || {};
      const doctor = maintenance?.doctor || {};
      const reconnects = readStorage(storageKeys.reconnects, []);
      const ops = readStorage(storageKeys.maintenanceOps, []);

      const doctorCard = document.createElement('div');
      doctorCard.className = 'item';
      doctorCard.innerHTML = `<strong>Doctor</strong><div class='tiny'>overall=${doctor.overall || 'unknown'} • pass=${doctor.counts?.pass ?? 0} warn=${doctor.counts?.warn ?? 0} fail=${doctor.counts?.fail ?? 0}</div>`;
      root.appendChild(doctorCard);

      const sections = [
        { title: 'Recovery Packs', items: maintenance?.recovery_packs?.items || [], key: 'name' },
        { title: 'DB Backups', items: maintenance?.database_backups?.items || [], key: 'name' },
        { title: 'Audit Archives', items: maintenance?.audit_archives?.items || [], key: 'name' },
      ];
      sections.forEach(section => {
        const card = document.createElement('div');
        card.className = 'item';
        const lines = (section.items || []).slice(0, 6).map(item => `${item[section.key]} • ${((item.size_bytes || 0) / 1024).toFixed(1)} KB`);
        card.innerHTML = `<strong>${section.title}</strong><div class='tiny'>${lines.length ? lines.join('\n') : 'none'}</div>`;
        root.appendChild(card);
      });

      const reconnectCard = document.createElement('div');
      reconnectCard.className = 'item';
      reconnectCard.innerHTML = `<strong>Reconnect Timeline</strong><div class='tiny'>${reconnects.slice(0, 8).map(item => `${item.ts} • ${item.status} • ${item.detail}`).join('\n') || 'none'}</div>`;
      root.appendChild(reconnectCard);

      const opsCard = document.createElement('div');
      opsCard.className = 'item';
      opsCard.innerHTML = `<strong>Maintenance Results</strong><div class='tiny'>${ops.slice(0, 10).map(item => `${item.ts} • ${item.title} • ${String(item.detail).slice(0, 140)}`).join('\n') || 'none'}</div>`;
      root.appendChild(opsCard);
    }

    function renderRecoveryPackSelect(maintenance) {
      const select = document.getElementById('recoveryPackSelect');
      if (!select) return;
      select.innerHTML = '';
      const items = maintenance?.recovery_packs?.items || [];
      if (!items.length) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'No recovery packs found';
        select.appendChild(opt);
        return;
      }
      items.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item.relative_path || item.path;
        opt.textContent = `${item.name} • ${(item.size_bytes / 1024).toFixed(1)} KB`;
        select.appendChild(opt);
      });
    }

    function renderBackupSelect(maintenance) {
      const select = document.getElementById('dbBackupSelect');
      if (!select) return;
      select.innerHTML = '';
      const items = maintenance?.database_backups?.items || [];
      if (!items.length) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'No DB backups found';
        select.appendChild(opt);
        return;
      }
      items.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item.relative_path || item.path;
        opt.textContent = `${item.name} • ${(item.size_bytes / 1024).toFixed(1)} KB`;
        select.appendChild(opt);
      });
    }

    function renderArchiveSelect(maintenance) {
      const select = document.getElementById('auditArchiveSelect');
      if (!select) return;
      select.innerHTML = '';
      const items = maintenance?.audit_archives?.items || [];
      if (!items.length) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'No audit archives found';
        select.appendChild(opt);
        return;
      }
      items.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item.path;
        opt.textContent = `${item.name} • ${(item.size_bytes / 1024).toFixed(1)} KB`;
        select.appendChild(opt);
      });
    }

    function renderStartupBanner(health, state) {
      const banner = document.getElementById('startupBanner');
      const validation = state?.validation || {};
      const models = state?.models || {};
      const database = state?.database || {};
      const provider = models?.provider || {};
      const blockers = validation?.blockers || [];
      const bits = [
        `API: ${health?.status || 'unknown'}`,
        `Model mode: ${provider.effective_provider || 'unknown'}`,
        `DB integrity: ${database.integrity_check || (database.exists ? 'unknown' : 'not-created')}`,
        `Blockers: ${blockers.length}`
      ];
      if (state?.validation?.shell_launcher?.ready) bits.push('Packaged shell ready');
      banner.textContent = bits.join(' • ');
      banner.style.borderColor = blockers.length ? '#8a6c22' : '#2f7055';
    }

    function renderMaintenance(maintenance) {
      const status = maintenance?.audit_status || {};
      const backendSettings = maintenance?.settings || {};
      const localPrefs = readStorage(storageKeys.maintenancePrefs, null);
      if (!localPrefs && backendSettings.ok) {
        const setIf = (id, value) => { const el = document.getElementById(id); if (el && value !== undefined && value !== null) el.value = String(value); };
        setIf('auditKeepInput', backendSettings.audit_keep);
        setIf('cleanupKeepRecentInput', backendSettings.cleanup_keep_recent);
        setIf('cleanupEmptyDaysInput', backendSettings.cleanup_empty_days);
        setIf('cleanupInactiveDaysInput', backendSettings.cleanup_inactive_days);
      }
      const backups = maintenance?.database_backups?.count ?? 0;
      const archives = maintenance?.audit_archives?.count ?? 0;
      const lastDb = (maintenance?.database_history || []).slice(-1)[0];
      const lastAudit = (maintenance?.audit_history || []).slice(-1)[0];
      let text = `DB backups: ${backups}\nAudit archives: ${archives}\nActive audit lines: ${status.line_count ?? 0}`;
      const lastSession = (maintenance?.session_history || []).slice(-1)[0];
      if (lastDb) text += `\nLast DB op: ${lastDb.event_type} @ ${lastDb.ts}`;
      if (lastAudit) text += `\nLast audit op: ${lastAudit.event_type} @ ${lastAudit.ts}`;
      if (lastSession) text += `\nLast session op: ${lastSession.event_type} @ ${lastSession.ts}`;
      setText('maintenanceStatus', text);
      renderBackupSelect(maintenance);
      renderArchiveSelect(maintenance);
      renderRecoveryPackSelect(maintenance);
      renderMaintenanceEvents(maintenance);
      renderMaintenanceDrawer();
    }

    async function refreshMaintenance() {
      const maintenance = await safeApi('/shell/state');
      if (maintenance.error) {
        pushErrorRecord('Maintenance refresh failed', maintenance.error);
        showToast('Maintenance refresh failed.', 'error');
        return;
      }
      latestShellState = { ...(latestShellState || {}), maintenance: maintenance.maintenance, database: maintenance.database, validation: maintenance.validation, models: maintenance.models, audit: maintenance.audit };
      renderMaintenance(maintenance.maintenance || {});
      showToast('Maintenance state refreshed.', 'info');
      pushMaintenanceOp('maintenance_refresh', 'manual');
    }

    async function exportRecoveryPack() {
      const result = await safeApi('/maintenance/export-pack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label: 'shell', include_backups: true, include_archives: true })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Recovery pack export failed', result.error || 'unknown error');
        showToast('Recovery pack export failed.', 'error');
        return;
      }
      appendEntry('recovery-pack', JSON.stringify(result, null, 2));
      showToast('Recovery pack exported.', 'info');
      pushMaintenanceOp('recovery_pack_export', result.path || result.relative_path || 'ok');
      await refreshState();
    }

    function downloadRecoveryPack() {
      const select = document.getElementById('recoveryPackSelect');
      const packPath = select?.value || '';
      if (!packPath) {
        showToast('Pick a recovery pack first.', 'error');
        return;
      }
      window.open(`/maintenance/pack-file?path=${encodeURIComponent(packPath)}`, '_blank');
      showToast('Opening recovery pack download.', 'info');
    }

    async function importRecoveryPack() {
      const select = document.getElementById('recoveryPackSelect');
      const packPath = select?.value || '';
      if (!packPath) {
        showToast('Pick a recovery pack first.', 'error');
        return;
      }
      const ok = window.confirm(`Import recovery pack?\n${packPath}\n\nThis can restore database, audit log, and wrapper state.`);
      if (!ok) return;
      const result = await safeApi('/maintenance/import-pack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pack_path: packPath, restore_database: true, restore_audit: true, restore_wrapper_state: true, extract_only: false, create_safety_backup: true })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Recovery pack import failed', result.error || 'unknown error');
        showToast('Recovery pack import failed.', 'error');
        return;
      }
      appendEntry('recovery-pack', JSON.stringify(result, null, 2));
      showToast('Recovery pack imported.', 'info');
      pushMaintenanceOp('recovery_pack_import', result.pack_path || 'ok');
      await refreshState();
    }

    async function previewCleanup(mode) {
      const presets = {
        light: { keep_recent: 40, drop_empty_older_than_days: 14, drop_inactive_older_than_days: 180, dry_run: true },
        normal: { keep_recent: 25, drop_empty_older_than_days: 7, drop_inactive_older_than_days: 90, dry_run: true },
        aggressive: { keep_recent: 15, drop_empty_older_than_days: 3, drop_inactive_older_than_days: 30, dry_run: true },
      };
      const payload = presets[mode] || presets.normal;
      const result = await safeApi('/sessions/cleanup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Session cleanup preview failed', result.error || 'unknown error');
        showToast('Session cleanup preview failed.', 'error');
        return;
      }
      appendEntry('session-cleanup-preview', JSON.stringify(result, null, 2));
      showToast(`Cleanup preview (${mode}) ready.`, 'info');
      pushMaintenanceOp('session_cleanup_preview', mode);
    }

    async function previewCustomCleanup() {
      const result = await safeApi('/sessions/cleanup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customCleanupPayload(true))
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Custom cleanup preview failed', result.error || 'unknown error');
        showToast('Custom cleanup preview failed.', 'error');
        return;
      }
      appendEntry('session-cleanup-preview', JSON.stringify(result, null, 2));
      showToast('Custom cleanup preview ready.', 'info');
      pushMaintenanceOp('session_cleanup_preview_custom', JSON.stringify(customCleanupPayload(true)));
    }

    async function runCustomCleanup() {
      const payload = customCleanupPayload(false);
      const ok = window.confirm(`Run custom session cleanup?\nkeep_recent=${payload.keep_recent}\nempty_days=${payload.drop_empty_older_than_days}\ninactive_days=${payload.drop_inactive_older_than_days}`);
      if (!ok) return;
      const result = await safeApi('/sessions/cleanup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Custom cleanup failed', result.error || 'unknown error');
        showToast('Custom cleanup failed.', 'error');
        return;
      }
      appendEntry('session-cleanup', JSON.stringify(result, null, 2));
      showToast('Custom session cleanup complete.', 'info');
      pushMaintenanceOp('session_cleanup_custom', `${payload.keep_recent}/${payload.drop_empty_older_than_days}/${payload.drop_inactive_older_than_days}`);
      await refreshState();
    }

    async function deleteRecoveryPack() {
      const select = document.getElementById('recoveryPackSelect');
      const packPath = select?.value || '';
      if (!packPath) { showToast('Pick a recovery pack first.', 'error'); return; }
      if (!window.confirm(`Delete recovery pack?\n${packPath}`)) return;
      const result = await safeApi('/maintenance/pack-delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pack_path: packPath })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Delete recovery pack failed', result.error || 'unknown error');
        showToast('Delete recovery pack failed.', 'error');
        return;
      }
      pushMaintenanceOp('recovery_pack_delete', packPath);
      showToast('Recovery pack deleted.', 'info');
      await refreshState();
    }

    async function previewRecoveryPack() {
      const select = document.getElementById('recoveryPackSelect');
      const packPath = select?.value || '';
      if (!packPath) {
        showToast('Pick a recovery pack first.', 'error');
        return;
      }
      const result = await safeApi(`/maintenance/pack-preview?path=${encodeURIComponent(packPath)}`);
      if (result.error || result.ok === false) {
        pushErrorRecord('Recovery pack preview failed', result.error || 'unknown error');
        showToast('Recovery pack preview failed.', 'error');
        return;
      }
      appendEntry('recovery-pack-preview', JSON.stringify(result, null, 2));
      showToast('Recovery pack preview loaded.', 'info');
      pushMaintenanceOp('recovery_pack_preview', packPath);
    }

    async function deleteSelectedBackup() {
      const select = document.getElementById('dbBackupSelect');
      const backupPath = select?.value || '';
      if (!backupPath) { showToast('Pick a database backup first.', 'error'); return; }
      if (!window.confirm(`Delete database backup?\n${backupPath}`)) return;
      const result = await safeApi('/database/backup-delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ backup_path: backupPath })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Delete database backup failed', result.error || 'unknown error');
        showToast('Delete database backup failed.', 'error');
        return;
      }
      pushMaintenanceOp('database_backup_delete', backupPath);
      showToast('Database backup deleted.', 'info');
      await refreshState();
    }

    function downloadSelectedBackup() {
      const select = document.getElementById('dbBackupSelect');
      const backupPath = select?.value || '';
      if (!backupPath) {
        showToast('Pick a database backup first.', 'error');
        return;
      }
      window.open(`/database/backup-file?path=${encodeURIComponent(backupPath)}`, '_blank');
      showToast('Opening database backup download.', 'info');
    }

    async function cleanupSessions(mode) {
      const presets = {
        light: { keep_recent: 40, drop_empty_older_than_days: 14, drop_inactive_older_than_days: 180, dry_run: false },
        normal: { keep_recent: 25, drop_empty_older_than_days: 7, drop_inactive_older_than_days: 90, dry_run: false },
        aggressive: { keep_recent: 15, drop_empty_older_than_days: 3, drop_inactive_older_than_days: 30, dry_run: false },
      };
      const payload = presets[mode] || presets.normal;
      const ok = window.confirm(`Run session cleanup preset: ${mode}?`);
      if (!ok) return;
      const result = await safeApi('/sessions/cleanup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Session cleanup failed', result.error || result.plain_english || 'unknown error');
        showToast('Session cleanup failed.', 'error');
        return;
      }
      appendEntry('session-cleanup', JSON.stringify(result, null, 2));
      showToast(`Session cleanup (${mode}) complete.`, 'info');
      pushMaintenanceOp('session_cleanup', `${mode}:${result.deleted_count || 0}`);
      await refreshState();
    }

    async function restoreDatabase() {
      const select = document.getElementById('dbBackupSelect');
      const backup_path = select?.value || '';
      if (!backup_path) {
        showToast('Pick a database backup first.', 'error');
        return;
      }
      const ok = window.confirm(`Restore database from backup?\n${backup_path}\n\nJARVIS will create a safety backup first.`);
      if (!ok) return;
      const result = await safeApi('/database/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ backup_path, create_backup_first: true })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Database restore failed', result.error || result.plain_english || 'unknown error');
        showToast('Database restore failed.', 'error');
        return;
      }
      appendEntry('database', JSON.stringify(result, null, 2));
      showToast('Database restored from backup.', 'info');
      pushMaintenanceOp('database_restore', backup_path);
      await refreshState();
    }

    async function previewAuditArchive() {
      const select = document.getElementById('auditArchiveSelect');
      const archivePath = select?.value || '';
      if (!archivePath) {
        showToast('Pick an audit archive first.', 'error');
        return;
      }
      const result = await safeApi(`/audit/archive-preview?path=${encodeURIComponent(archivePath)}&limit=20`);
      if (result.error || result.ok === false) {
        pushErrorRecord('Audit archive preview failed', result.error || 'unknown error');
        showToast('Audit archive preview failed.', 'error');
        return;
      }
      appendEntry('audit-archive', JSON.stringify(result, null, 2));
      showToast('Audit archive preview loaded.', 'info');
      pushMaintenanceOp('audit_archive_preview', archivePath);
    }

    async function deleteAuditArchive() {
      const select = document.getElementById('auditArchiveSelect');
      const archivePath = select?.value || '';
      if (!archivePath) { showToast('Pick an audit archive first.', 'error'); return; }
      if (!window.confirm(`Delete audit archive?\n${archivePath}`)) return;
      const result = await safeApi('/audit/archive-delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ archive_path: archivePath })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Delete audit archive failed', result.error || 'unknown error');
        showToast('Delete audit archive failed.', 'error');
        return;
      }
      pushMaintenanceOp('audit_archive_delete', archivePath);
      showToast('Audit archive deleted.', 'info');
      await refreshState();
    }

    function downloadAuditArchive() {
      const select = document.getElementById('auditArchiveSelect');
      const archivePath = select?.value || '';
      if (!archivePath) {
        showToast('Pick an audit archive first.', 'error');
        return;
      }
      window.open(`/audit/archive-file?path=${encodeURIComponent(archivePath)}`, '_blank');
      showToast('Opening audit archive download.', 'info');
    }

    async function rotateAudit() {
      const result = await safeApi('/audit/rotate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label: 'shell', keep_archives: 10 })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Audit rotation failed', result.error || 'unknown error');
        showToast('Audit rotation failed.', 'error');
        return;
      }
      appendEntry('audit', JSON.stringify(result, null, 2));
      showToast('Audit log rotated.', 'info');
      pushMaintenanceOp('audit_rotate', result.archive_path || 'ok');
      await refreshState();
    }

    async function pruneAudit(keepArchives=null) {
      const effectiveKeep = keepArchives === null ? Number(document.getElementById('auditKeepInput')?.value || 10) : keepArchives;
      const result = await safeApi('/audit/prune', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keep_archives: effectiveKeep })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Audit prune failed', result.error || 'unknown error');
        showToast('Audit prune failed.', 'error');
        return;
      }
      appendEntry('audit', JSON.stringify(result, null, 2));
      showToast('Old audit archives pruned.', 'info');
      pushMaintenanceOp('audit_prune', `keep=${effectiveKeep} removed=${result.removed_count || 0}`);
      await refreshState();
    }

    async function autoWarmStartIfNeeded() {
      const models = latestShellState?.models || {};
      const provider = models?.provider || {};
      const selected = provider?.selected_model || {};
      const warmKey = `${selected.name || 'none'}::${provider.effective_provider || 'unknown'}`;
      const alreadyWarm = readStorage(storageKeys.warm, null);
      if (provider.effective_provider !== 'llama_cpp') return;
      if ((models.loaded_models?.count || 0) > 0) return;
      if (alreadyWarm === warmKey) return;
      const result = await safeApi('/models/preload?slot=fast', { method: 'POST' });
      if (result.error || result.ok === false) {
        pushErrorRecord('Auto warm-start failed', result.error || 'unknown error');
        return;
      }
      writeStorage(storageKeys.warm, warmKey);
      showToast(`Warm-started local model: ${result.model_name}`, 'info');
      await refreshState();
    }

    function renderStatusBar(health, models) {
      const root = document.getElementById('statusBar');
      root.innerHTML = '';
      const badges = [];
      badges.push({ label: `API ${health.status || 'unknown'}`, cls: health.status === 'ok' ? 'good' : 'bad' });
      const effective = models?.provider?.effective_provider || health.effective_provider || 'unknown';
      badges.push({ label: `model ${effective}`, cls: effective === 'llama_cpp' ? 'good' : 'warn' });
      const shellReady = latestShellState?.validation?.shell_launcher?.ready;
      badges.push({ label: shellReady ? 'shell ready' : 'shell browser-fallback', cls: shellReady ? 'good' : 'warn' });
      badges.forEach(item => {
        const span = document.createElement('span');
        span.className = `badge ${item.cls}`;
        span.textContent = item.label;
        root.appendChild(span);
      });
    }

    function renderState(state, health) {
      latestShellState = state;
      sessionId = state.session_id || sessionId;

      const session = state.sessions?.current || {};
      setText('shellMeta', session.title ? `${session.title} • ${session.message_count || 0} msgs` : 'local command center');
      setText('sessionBadge', session.session_id ? `${session.title || 'Session'}\n${session.session_id}` : 'No active session yet.');

      const phase4 = state.phase4 || {};
      const phase5 = state.phase5 || {};
      setText('phase4Pct', `${phase4.percent ?? '--'}%`);
      setText('phase4Meta', `${phase4.completed ?? 0}/${phase4.total ?? 0} tasks complete`);
      setText('phase5Pct', `${phase5.percent ?? '--'}%`);
      setText('phase5Meta', `${phase5.completed ?? 0}/${phase5.total ?? 0} tasks complete`);

      const focus = state.focus || {};
      const today = state.today || {};
      const browser = state.browser || {};
      const validation = state.validation || {};
      const database = state.database || {};
      const operator = state.audit?.operator_summary || {};
      const models = state.models || {};
      const provider = models.provider || {};
      const selectedModel = provider.selected_model || {};

      setText('focusBlock', `${focus.headline || 'No current focus.'}\n${focus.plain_english || ''}`.trim());
      setText('todayBlock', `${today.plain_english || 'No today brief.'}${today.next_action ? `\nNext: ${today.next_action}` : ''}`);

      let browserText = browser.plain_english || 'No browser info.';
      if (browser.selected_browser) browserText += `\nSelected: ${browser.selected_browser}`;
      else if (browser.preferred_browser) browserText += `\nPreferred: ${browser.preferred_browser}`;
      if (browser.url) browserText += `\nURL: ${browser.url}`;
      if (browser.running_browser_names?.length) browserText += `\nRunning windows: ${browser.running_browser_names.join(', ')}`;
      if (browser.available_browsers?.length) browserText += `\nOptions: ${browser.available_browsers.map(x => x.name).join(', ')}`;
      setText('browserBlock', browserText);

      let modelText = models.plain_english || 'Model status unavailable.';
      modelText += `\nConfigured: ${provider.configured_provider || 'unknown'}`;
      modelText += `\nEffective: ${provider.effective_provider || 'unknown'}`;
      if (selectedModel.name) modelText += `\nSelected model: ${selectedModel.name}`;
      const ggufCount = models.discovered?.count ?? 0;
      modelText += `\nLocal GGUFs found: ${ggufCount}`;
      if (models.next_action) modelText += `\nNext: ${models.next_action}`;
      setText('modelBlock', modelText);

      let validationText = validation.plain_english || 'Validation unavailable.';
      if (validation.blockers?.length) validationText += `\nBlockers: ${validation.blockers.join(' | ')}`;
      else validationText += '\nBlockers: none';
      if (validation.next_steps?.length) validationText += `\nNext: ${validation.next_steps[0]}`;
      setText('validationBlock', validationText);

      const maintenance = state.maintenance || {};
      const doctor = maintenance.doctor || {};
      let doctorText = `overall=${doctor.overall || 'unknown'} • pass=${doctor.counts?.pass ?? 0} warn=${doctor.counts?.warn ?? 0} fail=${doctor.counts?.fail ?? 0}`;
      if (doctor.next_action) doctorText += `\nNext: ${doctor.next_action}`;
      setText('maintenanceDoctorBlock', doctorText);

      let databaseText = database.plain_english || 'Database status unavailable.';
      if (database.exists) {
        databaseText += `\nIntegrity: ${database.integrity_check || 'unknown'}`;
        databaseText += `\nSessions: ${database.session_count ?? 0} • Messages: ${database.message_count ?? 0} • Tasks: ${database.task_count ?? 0}`;
      }
      setText('databaseBlock', databaseText);

      let operatorText = `Timeline events: ${operator.timeline_events ?? 0}`;
      const risk = operator.risk_counts || {};
      operatorText += `\nRisk mix — low:${risk.low ?? 0} medium:${risk.medium ?? 0} high:${risk.high ?? 0}`;
      setText('operatorBlock', operatorText);

      renderTasks(state.tasks?.items?.items || []);
      renderSessions(state.sessions?.items || []);
      renderTimeline(state.audit?.timeline || []);
      renderQuickCommands(today.next_steps || focus.recommended || []);
      renderModelSelectors(models);
      renderMaintenance(state.maintenance || {});
      renderStartupBanner(health || {}, state || {});
      renderStatusBar(health || {}, models || {});
    }

    function renderModelSelectors(models) {
      const fastSelect = document.getElementById('fastModelSelect');
      const mainSelect = document.getElementById('mainModelSelect');
      const items = models?.discovered?.items || [];
      const currentFast = models?.fast_selection?.selected?.name || models?.fast_selection?.configured_name || '';
      const currentMain = models?.main_selection?.selected?.name || models?.main_selection?.configured_name || '';
      [fastSelect, mainSelect].forEach(select => { select.innerHTML = ''; });
      if (!items.length) {
        const opt1 = document.createElement('option'); opt1.textContent = 'No GGUF models found'; opt1.value = '';
        const opt2 = opt1.cloneNode(true);
        fastSelect.appendChild(opt1);
        mainSelect.appendChild(opt2);
        return;
      }
      items.forEach(item => {
        const label = `${item.name} • ${item.size_gb} GB`;
        const optFast = document.createElement('option'); optFast.value = item.name; optFast.textContent = label;
        const optMain = document.createElement('option'); optMain.value = item.name; optMain.textContent = label;
        if (item.name === currentFast) optFast.selected = true;
        if (item.name === currentMain) optMain.selected = true;
        fastSelect.appendChild(optFast);
        mainSelect.appendChild(optMain);
      });
    }

    async function applyModelSelection() {
      const fast_model = document.getElementById('fastModelSelect').value;
      const main_model = document.getElementById('mainModelSelect').value;
      const result = await safeApi('/models/configure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: 'auto', fast_model, main_model })
      });
      if (result.error) {
        pushErrorRecord('Model configure failed', result.error);
        showToast('Model configure failed.', 'error');
        return;
      }
      showToast('Model selection applied. Restart recommended for the cleanest runtime refresh.', 'info');
      await refreshState();
    }

    async function useLocalModels() {
      const result = await safeApi('/models/use-local', { method: 'POST' });
      if (result.error || result.ok === false) {
        pushErrorRecord('Use local models failed', result.error || result.plain_english || 'unknown error');
        showToast('Use local models failed.', 'error');
        return;
      }
      showToast('Switched to local model preference.', 'info');
      await refreshState();
    }

    async function useMockModels() {
      const result = await safeApi('/models/use-mock', { method: 'POST' });
      if (result.error || result.ok === false) {
        pushErrorRecord('Use mock models failed', result.error || result.plain_english || 'unknown error');
        showToast('Use mock models failed.', 'error');
        return;
      }
      showToast('Switched to mock mode.', 'info');
      await refreshState();
    }

    async function preloadModel(slot) {
      const result = await safeApi(`/models/preload?slot=${encodeURIComponent(slot)}`, { method: 'POST' });
      if (result.error || result.ok === false) {
        pushErrorRecord('Model preload failed', result.error || result.plain_english || 'unknown error');
        showToast(`Preload ${slot} failed.`, 'error');
        return;
      }
      showToast(`Preloaded ${slot} model: ${result.model_name}`, 'info');
      pushMaintenanceOp('model_preload', `${slot}:${result.model_name}`);
      await refreshState();
    }

    async function backupDatabase() {
      const result = await safeApi('/database/backup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label: 'shell' })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Database backup failed', result.error || 'unknown error');
        showToast('Database backup failed.', 'error');
        return;
      }
      showToast('Database backup created.', 'info');
      pushMaintenanceOp('database_backup', result.path || 'ok');
      appendEntry('database', JSON.stringify(result, null, 2));
      await refreshState();
    }

    async function vacuumDatabase() {
      const result = await safeApi('/database/vacuum', { method: 'POST' });
      if (result.error || result.ok === false) {
        pushErrorRecord('Database vacuum failed', result.error || 'unknown error');
        showToast('Database vacuum failed.', 'error');
        return;
      }
      showToast('Database vacuum complete.', 'info');
      pushMaintenanceOp('database_vacuum', result.delta_bytes || 0);
      appendEntry('database', JSON.stringify(result, null, 2));
      await refreshState();
    }

    async function refreshState() {
      const qs = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : '';
      const [health, state, voice] = await Promise.all([
        safeApi('/health'),
        safeApi(`/shell/state${qs}`),
        safeApi('/voice/status'),
      ]);

      if (!voice.error) {
        let text = voice.plain_english || 'Voice status unavailable.';
        text += `\nSTT ready: ${voice.stt_ready ? 'yes' : 'no'}`;
        text += `\nTTS ready: ${voice.tts_ready ? 'yes' : 'no'}`;
        setText('voiceBlock', text);
      } else {
        setText('voiceBlock', `Voice status failed: ${voice.error}`);
      }

      if (state.error) {
        appendEntry('error', `Shell state load failed: ${state.error}`, true);
        pushErrorRecord('Shell state load failed', state.error);
        showConnectionOverlay(`JARVIS could not refresh the live local state. ${state.error}`);
        pushReconnectEvent('refresh_failed', state.error);
        const cached = readStorage(storageKeys.cachedState, null);
        if (cached) {
          renderState(cached, health);
          setText('startupBanner', `Recovery mode • last cached shell state loaded • live refresh error: ${state.error}`);
          showToast('Loaded cached shell state because live state refresh failed.', 'error');
          setComposerStatus('Recovery mode: using cached shell state.');
          return;
        }
        setComposerStatus('Shell state failed to load.');
        renderStatusBar(health || {}, latestShellState?.models || {});
        return;
      }

      hideConnectionOverlay();
      pushReconnectEvent('refresh_ok', 'Live shell state refreshed successfully.');
      cacheShellState(state);
      renderState(state, health);
    }

    async function bootShell() {
      restoreDraft();
      applyMaintenancePrefs();
      renderErrorDrawer();
      setComposerStatus('Booting shell…');
      await refreshState();
      await autoWarmStartIfNeeded();
      promptInput.focus();
      setComposerStatus('Ready.');
      showToast('JARVIS shell booted.', 'info');
    }

    function showSnapshot(kind) {
      if (!latestShellState) {
        appendEntry('system', 'No shell state loaded yet.');
        return;
      }
      const payloads = {
        today: latestShellState.today,
        browser: latestShellState.browser,
        models: latestShellState.models,
        validation: latestShellState.validation,
        database: latestShellState.database,
        maintenance: latestShellState.maintenance,
        timeline: latestShellState.audit?.timeline,
      };
      appendEntry(kind, JSON.stringify(payloads[kind], null, 2));
    }

    composerForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      await sendPrompt();
    });

    promptInput.addEventListener('input', () => {
      writeStorage(storageKeys.draft, promptInput.value);
    });

    promptInput.addEventListener('keydown', async (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        await sendPrompt();
      }
      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        await sendPrompt();
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === '/' && document.activeElement !== promptInput) {
        event.preventDefault();
        promptInput.focus();
      }
      if (event.key === 'Escape') {
        closeApproval(false);
      }
    });

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) refreshState();
    });
    setInterval(() => { refreshState(); }, 30000);

    appendEntry('system', 'JARVIS shell online. Type a natural-language goal, use Enter to send, or hit the quick actions on the left.');
    bootShell();
  </script>
</body>
</html>
"""
