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
    body { margin:0; background:#0d1014; color:#eef3f8; font-family:Inter,Segoe UI,Arial,sans-serif; }
    .app { display:grid; grid-template-columns:280px 1fr; gap:14px; padding:14px; height:100vh; box-sizing:border-box; }
    .card { background:#151a21; border:1px solid #262e39; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,.28); }
    .sidebar { padding:14px; }
    .main { display:flex; flex-direction:column; overflow:hidden; }
    .head { padding:14px 16px; border-bottom:1px solid #262e39; color:#dfe7f0; font-weight:700; }
    .body { padding:14px 16px; color:#9caab8; font-size:13px; }
    .feed { flex:1; padding:16px; font-size:14px; }
    .composer { border-top:1px solid #262e39; padding:14px 16px; color:#7f93a8; }
  </style>
</head>
<body>
  <div class='app'>
    <div class='card sidebar'>
      <div class='head'>JARVIS</div>
      <div class='body'>Quiet executive assistant<br><br>Tasks, project, and next actions live in the sidebar. Chat stays central.</div>
    </div>
    <div class='card main'>
      <div class='head'>Chat-first shell</div>
      <div class='feed'>Minimal, Claude-like chat surface with low noise.</div>
      <div class='composer'>Type a goal. JARVIS handles the rest.</div>
    </div>
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
  <title>JARVIS Shell</title>
  <style>
    :root {
      --bg: #0c1014;
      --bg2: #11161d;
      --panel: #171c23;
      --panel2: #1c232d;
      --border: #2a313c;
      --text: #eef2f7;
      --muted: #94a1b2;
      --soft: #cbd5e1;
      --accent: #c7d2fe;
      --good: #a7f3d0;
      --warn: #fde68a;
      --bad: #fda4af;
      --shadow: 0 12px 40px rgba(0,0,0,.28);
      --radius: 20px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: radial-gradient(circle at top, #121821 0%, var(--bg) 48%);
      color: var(--text);
      font-family: Inter, Segoe UI, Arial, sans-serif;
      height: 100vh;
      overflow: hidden;
    }
    .app {
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 14px;
      height: 100vh;
      padding: 14px;
    }
    .sidebar, .main, .drawer, .modal, .overlay-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    .sidebar {
      display: flex;
      flex-direction: column;
      min-height: 0;
      overflow: hidden;
    }
    .main {
      display: flex;
      flex-direction: column;
      min-height: 0;
      overflow: hidden;
    }
    .sidebar-head, .topbar, .drawer-head, .modal-head {
      padding: 14px 16px;
      border-bottom: 1px solid var(--border);
    }
    .sidebar-head .title, .topbar .title {
      font-size: 13px;
      font-weight: 800;
      letter-spacing: .08em;
      text-transform: uppercase;
      color: var(--text);
    }
    .sidebar-head .subtitle, .topbar .subtitle {
      margin-top: 4px;
      font-size: 12px;
      color: var(--muted);
    }
    .sidebar-body, .drawer-body {
      flex: 1;
      min-height: 0;
      overflow: auto;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      min-height: 66px;
    }
    .status-strip {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
      justify-content: flex-end;
    }
    .pill {
      border: 1px solid #364152;
      background: #1a212b;
      color: var(--soft);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 11px;
      white-space: nowrap;
    }
    .pill.good { border-color: #315d4f; color: var(--good); }
    .pill.warn { border-color: #7a6838; color: var(--warn); }
    .pill.bad { border-color: #6d3b45; color: var(--bad); }
    .section {
      border: 1px solid #27303a;
      background: var(--panel2);
      border-radius: 16px;
      padding: 12px;
    }
    .section-title {
      font-size: 11px;
      letter-spacing: .06em;
      text-transform: uppercase;
      color: var(--muted);
      font-weight: 800;
      margin-bottom: 10px;
    }
    .section-body {
      font-size: 13px;
      color: var(--soft);
      line-height: 1.55;
      white-space: pre-wrap;
    }
    .list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .item {
      border: 1px solid #2b3440;
      background: #161d26;
      border-radius: 14px;
      padding: 10px 11px;
      font-size: 12px;
      color: var(--soft);
      line-height: 1.45;
    }
    .item strong { color: var(--text); }
    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    button, .chip {
      appearance: none;
      border: 1px solid #334050;
      background: #202833;
      color: var(--text);
      border-radius: 12px;
      padding: 9px 11px;
      cursor: pointer;
      font-size: 12px;
    }
    button:hover, .chip:hover { background: #253040; }
    .shell-banner {
      margin: 12px 12px 0 12px;
      border: 1px solid #313d4b;
      background: #151d27;
      border-radius: 16px;
      padding: 12px 14px;
      color: var(--soft);
      font-size: 12px;
      white-space: pre-wrap;
    }
    .feed {
      flex: 1;
      min-height: 0;
      overflow: auto;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .entry {
      border: 1px solid #2d3641;
      background: #181f28;
      border-radius: 18px;
      padding: 14px;
    }
    .entry .role {
      font-size: 11px;
      letter-spacing: .06em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
      font-weight: 700;
    }
    .entry .text {
      font-size: 15px;
      color: var(--text);
      line-height: 1.62;
      white-space: pre-wrap;
    }
    .entry.user { background: #1b2330; }
    .entry.assistant { background: #151b22; }
    .entry.system { background: #141920; }
    .entry.error {
      border-color: #6a3d47;
      background: #201419;
    }
    .composer {
      border-top: 1px solid var(--border);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      background: rgba(17, 22, 29, .92);
    }
    .composer-help {
      font-size: 12px;
      color: var(--muted);
    }
    .composer-row {
      display: flex;
      gap: 10px;
      align-items: flex-end;
    }
    textarea {
      width: 100%;
      min-height: 96px;
      resize: vertical;
      border-radius: 16px;
      border: 1px solid #334152;
      background: #10161d;
      color: var(--text);
      padding: 12px 14px;
      outline: none;
      font: inherit;
      line-height: 1.5;
    }
    .toolbar {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .toolbar .status {
      font-size: 12px;
      color: var(--muted);
    }
    .drawer {
      position: fixed;
      top: 14px;
      left: 14px;
      width: min(420px, 94vw);
      height: calc(100vh - 28px);
      transform: translateX(-110%);
      transition: transform .18s ease;
      z-index: 50;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .drawer.right {
      left: auto;
      right: 14px;
      transform: translateX(110%);
    }
    .drawer.open { transform: translateX(0); }
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(5, 8, 14, .74);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 70;
    }
    .modal {
      width: min(560px, 94vw);
      overflow: hidden;
    }
    .modal-head {
      color: var(--bad);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .06em;
    }
    .modal-body {
      padding: 16px;
      color: var(--soft);
      line-height: 1.55;
      white-space: pre-wrap;
    }
    .modal-actions {
      padding: 14px 16px 16px;
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }
    .overlay {
      position: fixed;
      inset: 0;
      background: rgba(5, 8, 14, .72);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 60;
    }
    .overlay.hidden { display: none; }
    .overlay-card {
      width: min(560px, 94vw);
      padding: 18px;
    }
    .toast-wrap {
      position: fixed;
      left: 18px;
      bottom: 18px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      z-index: 80;
    }
    .toast {
      min-width: 240px;
      max-width: 420px;
      border: 1px solid #334152;
      background: #161d26;
      color: var(--text);
      border-radius: 14px;
      padding: 12px 13px;
      box-shadow: var(--shadow);
      font-size: 12px;
    }
    .toast.error { border-color: #6a3d47; }
    .hidden { display: none !important; }
    @media (max-width: 980px) {
      .app { grid-template-columns: 1fr; }
      .sidebar { display: none; }
    }
  </style>
</head>
<body>
  <div class='app'>
    <aside class='sidebar'>
      <div class='sidebar-head'>
        <div class='title'>JARVIS</div>
        <div class='subtitle'>Quiet executive assistant</div>
      </div>
      <div class='sidebar-body'>
        <div class='section'>
          <div class='section-title'>Do this now</div>
          <div class='section-body' id='sidebarBrief'>Loading…</div>
          <div class='chips' style='margin-top:10px;'>
            <button class='chip' id='sidebarPrimaryAction'>Run</button>
          </div>
        </div>
        <div class='section'>
          <div class='section-title'>Current project</div>
          <div class='section-body' id='sidebarProject'>Loading…</div>
        </div>
        <div class='section'>
          <div class='section-title'>Tasks</div>
          <div class='section-body' id='sidebarTasks'>Loading…</div>
        </div>
        <div class='section'>
          <div class='section-title'>Next actions</div>
          <div class='chips' id='sidebarNextActions'></div>
        </div>
      </div>
    </aside>

    <main class='main'>
      <div class='topbar'>
        <div>
          <div class='title'>JARVIS Shell</div>
          <div class='subtitle' id='topSubtitle'>Chat first. Low noise. Context when needed.</div>
        </div>
        <div class='status-strip' id='statusStrip'></div>
      </div>

      <div class='shell-banner' id='startupBanner'>Booting local startup diagnostics…</div>
      <div class='feed' id='feed'></div>

      <form class='composer' id='composerForm'>
        <div class='composer-help'>Enter sends • Shift+Enter adds a new line • Most tools stay hidden until needed.</div>
        <div class='composer-row'>
          <textarea id='prompt' placeholder='What do you need, boss?'></textarea>
        </div>
        <div class='toolbar'>
          <button type='submit' id='sendButton'>Send</button>
          <button type='button' onclick='clearComposer()'>Clear</button>
          <button type='button' onclick='retryLastPrompt()'>Retry Last</button>
          <button type='button' onclick='openBrowserFromShell()'>Browser</button>
          <button type='button' onclick='sendPreset("show me the current page")'>Current page</button>
          <button type='button' onclick='toggleDrawer("context", true)'>Context</button>
          <button type='button' onclick='toggleDrawer("tools", true)'>Tools</button>
          <button type='button' onclick='toggleDrawer("ops", true)'>Ops</button>
          <button type='button' onclick='toggleDrawer("errors", true)'>Errors</button>
          <span class='status' id='composerStatus'>Ready.</span>
        </div>
      </form>
    </main>
  </div>

  <div class='drawer' id='contextDrawer'>
    <div class='drawer-head'>Context <button onclick='toggleDrawer("context", false)'>Close</button></div>
    <div class='drawer-body' id='contextDrawerBody'></div>
  </div>

  <div class='drawer' id='toolsDrawer'>
    <div class='drawer-head'>Tools <button onclick='toggleDrawer("tools", false)'>Close</button></div>
    <div class='drawer-body' id='toolsDrawerBody'></div>
  </div>

  <div class='drawer right' id='opsDrawer'>
    <div class='drawer-head'>Operations <button onclick='toggleDrawer("ops", false)'>Close</button></div>
    <div class='drawer-body' id='opsDrawerBody'></div>
  </div>

  <div class='drawer right' id='errorDrawer'>
    <div class='drawer-head'>Errors <button onclick='toggleDrawer("errors", false)'>Close</button></div>
    <div class='drawer-body' id='errorDrawerBody'></div>
  </div>

  <div class='modal-backdrop' id='approvalModal'>
    <div class='modal'>
      <div class='modal-head'>Approval Required</div>
      <div class='modal-body'>
        <div id='approvalRisk'></div>
        <div style='margin-top:8px;' id='approvalReason'></div>
        <div style='margin-top:12px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace;' id='approvalCommand'></div>
      </div>
      <div class='modal-actions'>
        <button onclick='closeApproval(false)'>Cancel</button>
        <button onclick='closeApproval(true)'>Confirm</button>
      </div>
    </div>
  </div>

  <div class='overlay hidden' id='connectionOverlay'>
    <div class='overlay-card'>
      <div class='section-title'>Connection / Recovery</div>
      <div class='section-body' id='connectionOverlayText'>JARVIS is checking the local shell connection…</div>
      <div class='chips' style='margin-top:12px;'>
        <button onclick='manualReconnect()'>Reconnect</button>
        <button onclick='toggleDrawer("ops", true)'>Open Ops</button>
        <button onclick='toggleDrawer("errors", true)'>Open Errors</button>
      </div>
    </div>
  </div>

  <div class='toast-wrap' id='toastWrap'></div>

  <script>
    let sessionId = null;
    let latestShellState = null;
    let lastAcceptance = null;
    let lastPrompt = '';
    let sending = false;
    let chatReady = false;

    const feed = document.getElementById('feed');
    const promptInput = document.getElementById('prompt');
    const sendButton = document.getElementById('sendButton');
    const toastWrap = document.getElementById('toastWrap');
    const approvalModal = document.getElementById('approvalModal');
    const connectionOverlay = document.getElementById('connectionOverlay');

    const storageKeys = {
      draft: 'jarvis.shell.draft',
      session: 'jarvis.shell.session',
      cachedState: 'jarvis.shell.cachedState',
      errors: 'jarvis.shell.errors'
    };

    function $(id) { return document.getElementById(id); }

    function setText(id, text) {
      const el = $(id);
      if (el) el.textContent = text;
    }

    function appendEntry(role, text, isError=false) {
      const entry = document.createElement('div');
      entry.className = `entry ${role}${isError ? ' error' : ''}`;
      entry.innerHTML = `<div class='role'></div><div class='text'></div>`;
      entry.querySelector('.role').textContent = role;
      entry.querySelector('.text').textContent = text;
      feed.appendChild(entry);
      feed.scrollTop = feed.scrollHeight;
    }

    function showToast(message, kind='info') {
      const toast = document.createElement('div');
      toast.className = `toast${kind === 'error' ? ' error' : ''}`;
      toast.textContent = message;
      toastWrap.appendChild(toast);
      setTimeout(() => toast.remove(), 3800);
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
      try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
    }

    function setComposerStatus(text) {
      setText('composerStatus', text);
    }

    function setShellReady(ready, reason='') {
      chatReady = !!ready;
      promptInput.disabled = !ready && !sending;
      sendButton.disabled = !ready && !sending;
      setComposerStatus(ready ? 'Ready.' : (reason || 'Shell send path not ready yet.'));
    }

    function toggleDrawer(name, open) {
      const map = {
        context: 'contextDrawer',
        tools: 'toolsDrawer',
        ops: 'opsDrawer',
        errors: 'errorDrawer'
      };
      const el = $(map[name]);
      if (!el) return;
      el.classList.toggle('open', open);
      if (open) {
        if (name === 'context') renderContextDrawer();
        if (name === 'tools') renderToolsDrawer();
        if (name === 'ops') {
          renderOpsDrawer();
          refreshAcceptanceStatus().then(() => renderOpsDrawer());
        }
        if (name === 'errors') renderErrorsDrawer();
      }
    }

    function showConnectionOverlay(message) {
      setText('connectionOverlayText', message);
      connectionOverlay.classList.remove('hidden');
    }

    function hideConnectionOverlay() {
      connectionOverlay.classList.add('hidden');
    }

    function renderErrorsDrawer() {
      const items = readStorage(storageKeys.errors, []);
      const root = $('errorDrawerBody');
      if (!items.length) {
        root.innerHTML = `<div class='section'><div class='section-title'>Errors</div><div class='section-body'>No captured errors.</div></div>`;
        return;
      }
      root.innerHTML = items.slice(0, 20).map(item => `
        <div class='section'>
          <div class='section-title'>${item.title}</div>
          <div class='section-body'>${item.ts}\n${String(item.detail || '').slice(0, 1200)}</div>
        </div>
      `).join('');
    }

    function pushErrorRecord(title, detail) {
      const items = readStorage(storageKeys.errors, []);
      items.unshift({ ts: new Date().toISOString(), title, detail });
      writeStorage(storageKeys.errors, items.slice(0, 50));
      renderErrorsDrawer();
    }

    function restoreDraft() {
      const draft = readStorage(storageKeys.draft, '');
      if (draft && !promptInput.value) promptInput.value = draft;
      const savedSession = readStorage(storageKeys.session, null);
      if (savedSession && !sessionId) sessionId = savedSession;
    }

    function cacheShellState(state) {
      writeStorage(storageKeys.cachedState, state);
      if (state?.session_id) writeStorage(storageKeys.session, state.session_id);
    }

    function clearComposer() {
      promptInput.value = '';
      writeStorage(storageKeys.draft, '');
      setComposerStatus('Composer cleared.');
      promptInput.focus();
    }

    function retryLastPrompt() {
      if (!lastPrompt) {
        setComposerStatus('No previous prompt to retry yet.');
        return;
      }
      promptInput.value = lastPrompt;
      promptInput.focus();
      setComposerStatus('Restored previous prompt.');
    }

    async function api(path, options={}) {
      const url = new URL(path, window.location.origin).toString();
      const res = await fetch(url, options);
      const raw = await res.text();
      let data;
      try { data = raw ? JSON.parse(raw) : {}; } catch { data = { raw }; }
      if (!res.ok) {
        const detail = data?.detail ? JSON.stringify(data.detail) : (data?.raw || raw || `HTTP ${res.status}`);
        throw new Error(detail);
      }
      return data;
    }

    async function safeApi(path, options={}) {
      try { return await api(path, options); }
      catch (error) { return { ok: false, error: error.message || String(error) }; }
    }

    async function classifyCommand(command) {
      const result = await safeApi(`/operator/classify?command=${encodeURIComponent(command)}`);
      if (result && result.ok === false && result.error) {
        return { risk: 'low', label: 'fallback', reason: 'Operator classifier unavailable.', requires_confirmation: false };
      }
      return result;
    }

    function showApproval(command, info) {
      setText('approvalRisk', `Risk: ${info.risk} (${info.label})`);
      setText('approvalReason', info.reason || '');
      setText('approvalCommand', command || '');
      approvalModal.dataset.pending = command || '';
      approvalModal.style.display = 'flex';
    }

    function closeApproval(confirmed) {
      approvalModal.style.display = 'none';
      const cmd = approvalModal.dataset.pending || '';
      approvalModal.dataset.pending = '';
      if (confirmed && cmd) actuallySend(cmd, true);
      else showToast('Command cancelled.', 'info');
    }

    async function sendPrompt() {
      if (sending) return;
      if (!chatReady) {
        setComposerStatus('Shell send path not ready yet.');
        showToast('Shell send path not ready yet.', 'error');
        return;
      }
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
      sending = true;
      setShellReady(chatReady);
      promptInput.value = '';
      writeStorage(storageKeys.draft, '');
      appendEntry('you', message);
      try {
        const data = await api('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, session_id: sessionId, use_tools: true, confirmed })
        });
        sessionId = data.session_id || sessionId;
        if (data.requires_confirmation && data.confirmation) {
          appendEntry('system', data.reply || 'Approval required before execution.');
          showApproval(message, data.confirmation);
          setComposerStatus('Approval required.');
          return;
        }
        appendEntry('assistant', data.reply || 'No reply');
        await refreshState();
        setComposerStatus('Reply received.');
      } catch (error) {
        promptInput.value = message;
        writeStorage(storageKeys.draft, message);
        appendEntry('error', `Chat send failed: ${error.message || error}`, true);
        pushErrorRecord('Chat send failed', error.message || String(error));
        setComposerStatus('JARVIS send failed.');
      } finally {
        sending = false;
        setShellReady(chatReady);
        promptInput.focus();
      }
    }

    function sendPreset(text) {
      promptInput.value = text;
      sendPrompt();
    }

    async function openBrowserFromShell(url=null, controlled=false) {
      const target = (url || latestShellState?.browser?.remembered_url || 'https://example.com').trim();
      const result = await safeApi('/tools/apps/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'browse',
          target,
          launch_mode: controlled ? 'playwright_managed' : 'external'
        })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Browser launch from shell failed', result.error || 'unknown error');
        showToast('Browser launch from shell failed.', 'error');
        return;
      }
      const summary = result.plain_english || result.result?.plain_english || (controlled ? 'Controlled browser launched.' : 'External browser launched.');
      const next = result.next_action || result.result?.next_action;
      const manualSteps = Array.isArray(result.manual_steps) ? result.manual_steps : (Array.isArray(result.result?.manual_steps) ? result.result.manual_steps : []);
      const detail = [summary, next ? `Next: ${next}` : '', manualSteps.length ? `Manual: ${manualSteps.slice(0, 2).join(' • ')}` : ''].filter(Boolean).join('
');
      appendEntry('system', detail);
      showToast(controlled ? 'Controlled browser launched.' : 'External browser launched.', 'info');
      await refreshState();
    }

    function renderStatusStrip(state, chatPing) {
      const brief = state?.brief || {};
      const models = state?.models || {};
      const provider = models.provider || {};
      const browser = state?.browser || {};
      const shellMs = state?.duration_ms;
      const pills = [
        { label: `API ${state?.ok ? 'ok' : 'warn'}`, cls: state?.ok ? 'good' : 'bad' },
        { label: `Model ${provider.effective_provider || chatPing?.effective_provider || 'unknown'}`, cls: (provider.effective_provider || chatPing?.effective_provider) === 'llama_cpp' ? 'good' : 'warn' },
        { label: `Mode ${browser.last_launch_mode || browser.default_mode || 'external'}`, cls: (browser.last_launch_mode || browser.default_mode) === 'playwright_managed' ? 'warn' : 'good' },
        { label: `Shell ${shellMs ?? '--'}ms`, cls: typeof shellMs === 'number' && shellMs < 700 ? 'good' : 'warn' },
        { label: `Next ${brief.primary_action || 'review'}`, cls: brief.primary_action ? 'good' : 'warn' }
      ];
      $('statusStrip').innerHTML = pills.map(item => `<span class='pill ${item.cls}'>${item.label}</span>`).join('');
    }

    function renderSidebar(state) {
      const brief = state?.brief || {};
      const project = state?.project || {};
      const projectIntel = state?.project_intelligence || {};
      const tasks = state?.tasks?.summary || {};
      const briefLines = [
        brief.headline || 'Do this now',
        brief.why || 'No executive brief yet.',
        brief.reentry_hint || '',
        brief.startup_subtitle ? `Signals: ${brief.startup_subtitle}` : ''
      ].filter(Boolean);
      setText('sidebarBrief', briefLines.join('\n'));
      const primaryBtn = $('sidebarPrimaryAction');
      primaryBtn.textContent = brief.primary_action || 'No action';
      primaryBtn.onclick = () => { if (brief.primary_action) sendPreset(brief.primary_action); };
      const projectType = Array.isArray((projectIntel.summary || project.summary || {}).project_type) ? ((projectIntel.summary || project.summary || {}).project_type).slice(0, 2).join(', ') : '';
      const confidence = projectIntel.confidence_label ? `\n${projectIntel.source || 'source'} • ${projectIntel.confidence_label}` : '';
      const projectLine = (projectIntel.path || project.path)
        ? `${projectIntel.path || project.path}${projectType ? `\n${projectType}` : ''}${confidence}`
        : 'No active project context.';
      setText('sidebarProject', projectLine);
      const currentTask = brief.current_task?.title;
      const nextTask = brief.next_task?.title;
      const taskLine = currentTask
        ? `In progress: ${currentTask}\n${tasks.open ?? 0} open • ${(tasks.done ?? 0)} done`
        : nextTask
          ? `Next: ${nextTask}\n${tasks.open ?? 0} open • ${(tasks.done ?? 0)} done`
          : (tasks.open ?? 0) > 0
            ? `${tasks.open ?? 0} open • ${(tasks.in_progress ?? 0)} in progress`
            : `clear board • ${(tasks.done ?? 0)} done`;
      setText('sidebarTasks', taskLine);
      const nextRoot = $('sidebarNextActions');
      nextRoot.innerHTML = '';
      (brief.secondary_actions || []).filter(Boolean).slice(0, 3).forEach(step => {
        const btn = document.createElement('button');
        btn.className = 'chip';
        btn.textContent = step;
        btn.onclick = () => sendPreset(step);
        nextRoot.appendChild(btn);
      });
    }

    function renderContextDrawer() {
      const state = latestShellState || {};
      const browser = state.browser || {};
      const models = state.models || {};
      const runtime = state.runtime || {};
      const validation = state.validation || {};
      const brief = state.brief || {};
      const projectIntel = state.project_intelligence || {};
      const trustedRoots = state.trusted_roots || {};
      const trustedRootLines = Array.isArray(trustedRoots.items)
        ? trustedRoots.items.slice(0, 5).map(item => `${item.name}: ${item.path}`).join('\n')
        : 'No trusted roots loaded.';
      $('contextDrawerBody').innerHTML = `
        <div class='section'><div class='section-title'>Executive brief</div><div class='section-body'>${brief.headline || 'No brief'}\n${brief.why || ''}\n${brief.reentry_hint || ''}</div></div>
        <div class='section'><div class='section-title'>Project</div><div class='section-body'>${projectIntel.path || state.project?.path || 'No active project.'}\n${projectIntel.source || ''} ${projectIntel.confidence_label ? `• ${projectIntel.confidence_label}` : ''}\n${projectIntel.reentry_hint || ''}</div></div>
        <div class='section'><div class='section-title'>Trusted roots</div><div class='section-body'>${trustedRootLines}</div></div>
        <div class='section'><div class='section-title'>Browser</div><div class='section-body'>${browser.plain_english || 'No browser summary.'}</div></div>
        <div class='section'><div class='section-title'>Model</div><div class='section-body'>${models.plain_english || 'No model summary.'}</div></div>
        <div class='section'><div class='section-title'>Runtime</div><div class='section-body'>${runtime.plain_english || 'No runtime summary.'}</div></div>
        <div class='section'><div class='section-title'>Validation</div><div class='section-body'>${validation.plain_english || 'No validation summary.'}</div></div>
      `;
    }

    function renderToolsDrawer() {
      const brief = latestShellState?.brief || {};
      const suggested = [brief.primary_action, ...(brief.secondary_actions || [])].filter(Boolean).slice(0, 3);
      const watchouts = Array.isArray(brief.watchouts) ? brief.watchouts.slice(0, 2) : [];
      $('toolsDrawerBody').innerHTML = `
        <div class='section'>
          <div class='section-title'>Best next move</div>
          <div class='section-body'>${brief.why || 'Use JARVIS to keep momentum without overthinking the next move.'}${brief.reentry_hint ? `\n${brief.reentry_hint}` : ''}</div>
          <div class='chips' style='margin-top:10px;'>
            ${suggested.map(step => `<button class="chip" onclick='sendPreset(${JSON.stringify(step)})'>${step}</button>`).join('')}
          </div>
        </div>
        ${watchouts.length ? `<div class='section'><div class='section-title'>Watchouts</div><div class='section-body'>${watchouts.join('\n')}</div></div>` : ''}
        <div class='section'>
          <div class='section-title'>Quick access</div>
          <div class='chips'>
            <button class='chip' onclick='openBrowserFromShell()'>Open browser</button>
            <button class='chip' onclick='sendPreset("show me the current page")'>Current page</button>
            <button class='chip' onclick='openBrowserFromShell(null, true)'>Controlled browser</button>
            <button class='chip' onclick='sendPreset("open code here")'>Code</button>
            <button class='chip' onclick='sendPreset("open terminal here")'>Terminal</button>
          </div>
        </div>
      `;
    }

    async function refreshAcceptanceStatus() {
      const result = await safeApi('/acceptance/status');
      if (!result.error) lastAcceptance = result;
      return result;
    }

    function renderOpsDrawer() {
      const maintenance = latestShellState?.maintenance || {};
      const acceptance = lastAcceptance || {};
      const doctor = maintenance.doctor || {};
      const verification = maintenance.verification || {};
      $('opsDrawerBody').innerHTML = `
        <div class='section'>
          <div class='section-title'>Acceptance</div>
          <div class='section-body'>overall=${acceptance?.latest?.overall || 'n/a'} • score=${acceptance?.latest?.score ?? '--'} • blockers=${acceptance?.latest?.blocker_count ?? 0}</div>
          <div class='chips' style='margin-top:10px;'>
            <button class='chip' onclick='runAcceptance(false)'>Run safe</button>
            <button class='chip' onclick='runAcceptance(true)'>Run deep</button>
            <button class='chip' onclick='showAcceptanceHistory()'>History</button>
            <button class='chip' onclick='showFinalBlockers()'>Blockers</button>
          </div>
        </div>
        <div class='section'>
          <div class='section-title'>Protect & Recover</div>
          <div class='section-body'>doctor=${doctor.overall || 'unknown'} • verify=${verification.overall || 'unknown'}</div>
          <div class='chips' style='margin-top:10px;'>
            <button class='chip' onclick='verifyMaintenance()'>Verify</button>
            <button class='chip' onclick='backupDatabase()'>Backup DB</button>
            <button class='chip' onclick='exportRecoveryPack()'>Export pack</button>
          </div>
        </div>
        <div class='section'>
          <div class='section-title'>Runtime checks</div>
          <div class='section-body'>Use these only when validating the live machine behavior.</div>
          <div class='chips' style='margin-top:10px;'>
            <button class='chip' onclick='validateBrowserRuntime()'>Browser</button>
            <button class='chip' onclick='validateDesktopRuntime()'>Desktop</button>
            <button class='chip' onclick='verifyModelRuntime("fast")'>Model</button>
          </div>
        </div>
        <div class='section'>
          <div class='section-title'>Advanced</div>
          <div class='chips'>
            <button class='chip' onclick='vacuumDatabase()'>Vacuum</button>
            <button class='chip' onclick='verifyModelRuntime("main")'>Verify main</button>
            <button class='chip' onclick='unloadModelRuntime()'>Unload models</button>
            <button class='chip' onclick='exportAcceptance()'>Export report</button>
            <button class='chip' onclick='resetAcceptance()'>Reset acceptance</button>
          </div>
        </div>
      `;
    }

    function renderBootstrap(bootstrap) {
      if (!bootstrap || bootstrap.error) return;
      const hygiene = bootstrap.state_hygiene || {};
      const model = bootstrap.models || {};
      const pieces = [
        `model=${model.provider || 'unknown'}`,
        `selected=${model.selected_model || 'none'}`
      ];
      if ((hygiene.count || 0) > 0) pieces.push(`normalized=${hygiene.count}`);
      if (bootstrap.next_action) pieces.push(`next=${bootstrap.next_action}`);
      setText('startupBanner', pieces.join(' • '));
    }

    function renderShellPath(health, chatPing, shellBootstrap, shellDoctor) {
      const pieces = [
        `api=${health?.status || 'unknown'}`,
        `chat=${chatPing?.chat_ready ? 'ready' : 'not-ready'}`,
        `model=${chatPing?.selected_model || 'none'}`,
        `loaded=${chatPing?.loaded_model_count ?? 0}`,
        `hygiene=${shellBootstrap?.state_hygiene?.count ?? 0}`
      ];
      if (chatPing?.consistency?.overall) pieces.push(`consistency=${chatPing.consistency.overall}`);
      if (shellDoctor?.next_action) pieces.push(`next=${shellDoctor.next_action}`);
      setText('shellPathBlock', pieces.join(' • '));
    }

    function renderRuntimeStability(runtime) {
      const warnings = runtime?.warnings || [];
      const pieces = [
        `overall=${runtime?.overall || 'unknown'}`,
        `warnings=${warnings.length}`,
        `browser=${runtime?.browser?.context?.preferred_browser || 'none'}`,
        `desktop=${runtime?.desktop?.active?.window?.title || 'unknown'}`
      ];
      if (warnings.length) pieces.push(`top=${warnings[0]}`);
      setText('runtimeBlock', pieces.join(' • '));
    }

    function renderAcceptanceStatus(acceptance) {
      let text = `history=${acceptance?.history_count ?? 0}`;
      if (acceptance?.latest?.overall) {
        text = `overall=${acceptance.latest.overall} • score=${acceptance.latest.score ?? '--'} • blockers=${acceptance.latest.blocker_count ?? 0}`;
        if (acceptance.latest.comparison?.blocker_delta !== undefined) text += ` • delta=${acceptance.latest.comparison.blocker_delta}`;
      }
      if (acceptance?.ready_for_phase_5_12 !== undefined) text += ` • ready=${acceptance.ready_for_phase_5_12 ? 'yes' : 'no'}`;
      if (acceptance?.blockers?.length) text += ` • top=${acceptance.blockers[0]}`;
      setText('acceptanceBlock', text);
    }

    function applyMaintenancePrefs() {
      // 5.12 minimal shell keeps advanced maintenance settings off the default surface.
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
    }

    function renderState(state, chatPing) {
      latestShellState = state;
      const shellBootstrap = state?.shell?.bootstrap || {};
      const shellDoctor = state?.shell?.doctor || {};
      renderStatusStrip(state, chatPing || {});
      renderSidebar(state);
      renderBootstrap(shellBootstrap || {});
      renderShellPath({ status: state?.ok ? 'ok' : 'warn' }, chatPing || {}, shellBootstrap || {}, shellDoctor || {});
      renderRuntimeStability(state.runtime || {});
      const brief = state?.brief || {};
      if (brief.primary_action) {
        const banner = [brief.headline || 'Do this now', brief.primary_action, brief.startup_subtitle || brief.why || '', brief.reentry_hint || '', typeof state?.duration_ms === 'number' ? `${state.duration_ms}ms` : ''].filter(Boolean).join(' • ');
        setText('startupBanner', banner);
      }
      setText('topSubtitle', brief.startup_subtitle || brief.why || 'Chat first. Low noise. Context when needed.');
    }

    async function verifyMaintenance() {
      const result = await safeApi('/maintenance/verify?limit=5');
      if (result.error || result.ok === false) {
        pushErrorRecord('Maintenance verification failed', result.error || 'unknown error');
        showToast('Maintenance verification failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast('Maintenance verification complete.', 'info');
    }

    async function backupDatabase() {
      const result = await safeApi('/database/backup', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ label: 'shell' })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Database backup failed', result.error || 'unknown error');
        showToast('Database backup failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast('Database backup created.', 'info');
      await refreshState();
    }

    async function vacuumDatabase() {
      const result = await safeApi('/database/vacuum', { method: 'POST' });
      if (result.error || result.ok === false) {
        pushErrorRecord('Database vacuum failed', result.error || 'unknown error');
        showToast('Database vacuum failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast('Database vacuum complete.', 'info');
      await refreshState();
    }

    async function exportRecoveryPack() {
      const result = await safeApi('/maintenance/export-pack', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ label: 'shell', include_backups: true, include_archives: true })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Recovery pack export failed', result.error || 'unknown error');
        showToast('Recovery pack export failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast('Recovery pack exported.', 'info');
      await refreshState();
    }

    async function validateBrowserRuntime() {
      const preferred = latestShellState?.browser?.preferred_browser;
      const browsers = preferred ? [preferred] : null;
      const result = await safeApi('/runtime/browser/validate', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ browsers, url: 'https://example.com', headless: false, mode: 'external' })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Browser runtime validation failed', result.error || 'unknown error');
        showToast('Browser runtime validation failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast('Browser runtime validation complete.', 'info');
      await refreshState();
    }

    async function validateDesktopRuntime() {
      const activeTitle = latestShellState?.runtime?.desktop?.active?.window?.title || latestShellState?.validation?.desktop_active?.window?.title;
      if (!activeTitle) {
        showToast('No active desktop window is available for validation.', 'error');
        return;
      }
      const result = await safeApi('/runtime/desktop/validate', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title: activeTitle, exact: false, match_index: 0, undo: true })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Desktop runtime validation failed', result.error || 'unknown error');
        showToast('Desktop runtime validation failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast('Desktop runtime validation complete.', 'info');
      await refreshState();
    }

    async function verifyModelRuntime(slot) {
      const payload = { slot, prompt: `Reply with exactly: SHELL ${slot.toUpperCase()} MODEL TEST`, expected: `SHELL ${slot.toUpperCase()} MODEL TEST` };
      const result = await safeApi('/models/verify', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Model runtime verification failed', result.error || result.reply || 'unknown error');
        appendEntry('error', JSON.stringify(result, null, 2), true);
        showToast(`Model verify ${slot} failed.`, 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast(`Model verify ${slot} passed.`, 'info');
      await refreshState();
    }

    async function unloadModelRuntime() {
      const result = await safeApi('/models/unload', { method: 'POST' });
      if (result.error || result.ok === false) {
        pushErrorRecord('Unload model runtime failed', result.error || 'unknown error');
        showToast('Unload model runtime failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast(`Unloaded ${result.unloaded_count || 0} in-process models.`, 'info');
      await refreshState();
    }

    async function runAcceptance(deep=false) {
      const result = await safeApi('/acceptance/run', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ deep })
      });
      if (result.error || result.ok === false) {
        pushErrorRecord('Acceptance sweep failed', result.error || 'unknown error');
        showToast('Acceptance sweep failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast(`Acceptance sweep (${deep ? 'deep' : 'safe'}) complete.`, 'info');
      await refreshState();
    }

    async function showAcceptanceHistory() {
      const result = await safeApi('/acceptance/history?limit=10');
      if (result.error || result.ok === false) {
        pushErrorRecord('Acceptance history failed', result.error || 'unknown error');
        showToast('Acceptance history failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast('Acceptance history loaded.', 'info');
    }

    async function showFinalBlockers() {
      const result = await safeApi('/acceptance/final-blockers');
      if (result.error || result.ok === false) {
        pushErrorRecord('Acceptance blocker summary failed', result.error || 'unknown error');
        showToast('Acceptance blocker summary failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast('Acceptance blocker summary loaded.', 'info');
    }

    async function exportAcceptance() {
      const result = await safeApi('/acceptance/export', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
      if (result.error || result.ok === false) {
        pushErrorRecord('Acceptance export failed', result.error || 'unknown error');
        showToast('Acceptance export failed.', 'error');
        return;
      }
      appendEntry('ops', JSON.stringify(result, null, 2));
      showToast('Acceptance report exported.', 'info');
    }

    async function resetAcceptance() {
      const ok = window.confirm('Reset acceptance history?');
      if (!ok) return;
      const result = await safeApi('/acceptance/reset', { method: 'POST' });
      if (result.error || result.ok === false) {
        pushErrorRecord('Acceptance reset failed', result.error || 'unknown error');
        showToast('Acceptance reset failed.', 'error');
        return;
      }
      showToast('Acceptance history reset.', 'info');
      await refreshState();
    }

    async function refreshState() {
      const qs = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : '';
      const [state, chatPing] = await Promise.all([
        safeApi(`/shell/state${qs}`),
        safeApi('/chat/ping')
      ]);

      setText('topSubtitle', 'Chat first. Low noise. Context when needed.');

      if (state.error) {
        appendEntry('error', `Shell state load failed: ${state.error}`, true);
        pushErrorRecord('Shell state load failed', state.error);
        showConnectionOverlay(`JARVIS could not refresh the live local state. ${state.error}`);
        const cached = readStorage(storageKeys.cachedState, null);
        if (cached) {
          renderState(cached, chatPing || {});
          setText('startupBanner', `Recovery mode • cached shell state loaded • error=${state.error}`);
          setShellReady(false, 'Recovery mode: using cached shell state.');
          return;
        }
        setShellReady(false, 'Shell state failed to load.');
        return;
      }

      hideConnectionOverlay();
      cacheShellState(state);
      renderState(state, chatPing || {});
      const ready = !chatPing?.error && !!chatPing?.chat_ready;
      setShellReady(ready, ready ? '' : 'Chat path is not ready yet.');
      renderContextDrawer();
      renderToolsDrawer();
      if ($('opsDrawer')?.classList.contains('open')) renderOpsDrawer();
    }

    async function manualReconnect() {
      showConnectionOverlay('JARVIS is retrying the local shell connection…');
      await refreshState();
    }

    async function bootShell() {
      restoreDraft();
      setComposerStatus('Booting shell…');
      appendEntry('system', 'What matters today?');
      await refreshState();
      refreshAcceptanceStatus();
      await autoWarmStartIfNeeded();
      promptInput.focus();
      setComposerStatus(chatReady ? 'Ready.' : 'Shell send path not ready yet.');
    }

    document.getElementById('composerForm').addEventListener('submit', async (event) => {
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
      if (event.key === 'Escape' && approvalModal.style.display === 'flex') {
        closeApproval(false);
      }
    });

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) refreshState();
    });

    setInterval(() => { refreshState(); }, 30000);
    bootShell();
  </script>
</body>
</html>
"""
