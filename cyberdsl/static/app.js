/* CyberDSL Studio — frontend SPA */
'use strict';

// ─── Palette ──────────────────────────────────────────────────────────────────
const PAL = ["#58a6ff","#3fb950","#d29922","#f85149","#bc8cff",
             "#79c0ff","#56d364","#e3b341","#ff7b72","#d2a8ff"];
function pal(i) { return PAL[i % PAL.length]; }
function palA(i, a) {
  const c = PAL[i % PAL.length].replace('#','');
  const r=parseInt(c.slice(0,2),16), g=parseInt(c.slice(2,4),16), b=parseInt(c.slice(4,6),16);
  return `rgba(${r},${g},${b},${a})`;
}

// ─── State ───────────────────────────────────────────────────────────────────
const state = {
  fmt: 'dsl',
  model: null,
  timeline: [],
  totalSteps: 0,
  mermaid: '',
  charts: {},
  direction: 'TD',
  streaming: false,
};

// ─── DOM refs ────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const editor      = $('editor');
const fmtSelect   = $('fmt-select');
const exampleSel  = $('example-select');
const btnParse    = $('btn-parse');
const btnRun      = $('btn-run');
const btnStream   = $('btn-stream');
const statusBadge = $('status-badge');
const parseError  = $('parse-error');
const mermaidEl   = $('mermaid-render');
const graphSteps  = $('graph-steps-label');
const streamProg  = $('stream-progress');
const streamBar   = $('stream-bar');
const streamLabel = $('stream-label');
const infoContent = $('model-info-content');

// ─── Tab switching ────────────────────────────────────────────────────────────
document.getElementById('tabs').addEventListener('click', e => {
  const btn = e.target.closest('.tab');
  if (!btn) return;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
  btn.classList.add('active');
  $(btn.dataset.panel).classList.remove('hidden');
});

// ─── Format selector ─────────────────────────────────────────────────────────
fmtSelect.addEventListener('change', () => { state.fmt = fmtSelect.value; });

// ─── Direction buttons ────────────────────────────────────────────────────────
document.querySelectorAll('.dir-btn').forEach(b => {
  b.addEventListener('click', async () => {
    document.querySelectorAll('.dir-btn').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    state.direction = b.dataset.dir;
    if (state.mermaid) await renderMermaid(state.mermaid, state.direction);
  });
});

// ─── Copy Mermaid ─────────────────────────────────────────────────────────────
$('btn-copy-mmd').addEventListener('click', async () => {
  if (!state.mermaid) return;
  await navigator.clipboard.writeText(state.mermaid).catch(() => {});
  $('btn-copy-mmd').textContent = '✓ Copied';
  setTimeout(() => { $('btn-copy-mmd').textContent = '⎘ .mmd'; }, 1500);
});

// ─── Keyboard shortcuts ───────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.ctrlKey && e.shiftKey && e.key === 'Enter') { e.preventDefault(); runSimulation(); }
  else if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); parseModel(); }
});

// ─── Examples loader ──────────────────────────────────────────────────────────
async function loadExampleList() {
  try {
    const r = await fetch('/api/examples');
    const data = await r.json();
    if (!data.ok) return;
    console.log('[CyberDSL] Loaded', data.examples.length, 'examples');
    const groups = {};
    data.examples.forEach(ex => {
      if (!groups[ex.category]) groups[ex.category] = [];
      groups[ex.category].push(ex);
    });
    Object.entries(groups).forEach(([cat, exs]) => {
      const grp = document.createElement('optgroup');
      grp.label = cat;
      exs.forEach(ex => {
        const opt = document.createElement('option');
        opt.value = ex.name;
        opt.dataset.fmt = ex.fmt;
        opt.textContent = ex.name;
        grp.appendChild(opt);
      });
      exampleSel.appendChild(grp);
    });
  } catch(e) { console.warn('[CyberDSL] Could not load examples', e); }
}

exampleSel.addEventListener('change', async () => {
  const name = exampleSel.value;
  if (!name) return;
  console.log('[CyberDSL] Loading example:', name);
  try {
    const r = await fetch(`/api/examples/${encodeURIComponent(name)}`);
    const data = await r.json();
    if (!data.ok) { showError(data.error); return; }
    editor.value = data.text;
    fmtSelect.value = data.fmt;
    state.fmt = data.fmt;
    clearResults();
    await parseModel();
  } catch(e) { showError(String(e)); }
  exampleSel.value = '';
});

// ─── Parse ────────────────────────────────────────────────────────────────────
btnParse.addEventListener('click', parseModel);

async function parseModel() {
  clearError();
  const text = editor.value.trim();
  if (!text) { setBadge('err', 'empty'); return; }
  setBadge('run', 'parsing…');
  console.log('[CyberDSL] parseModel fmt=%s len=%d', state.fmt, text.length);
  try {
    const r = await fetch('/api/parse', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ text, fmt: state.fmt }),
    });
    const data = await r.json();
    console.log('[CyberDSL] parse response ok=%s', data.ok, data.error || '');
    if (!data.ok) { showError(data.error); setBadge('err', 'parse error'); return; }
    state.model = data.model;
    setBadge('ok', `parsed — ${data.model.name}`);
    renderModelInfo(data.model);
    // get mermaid
    const mr = await fetch('/api/mermaid', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ text, fmt: state.fmt, direction: state.direction }),
    });
    const md = await mr.json();
    console.log('[CyberDSL] mermaid response ok=%s', md.ok);
    if (md.ok) {
      state.mermaid = md.mermaid;
      await renderMermaid(md.mermaid, state.direction);
    } else {
      showError('Mermaid: ' + md.error);
    }
  } catch(e) { console.error('[CyberDSL] parseModel error:', e); showError(String(e)); setBadge('err', 'error'); }
}

// ─── Run simulation (full) ────────────────────────────────────────────────────
btnRun.addEventListener('click', runSimulation);

async function runSimulation() {
  const text = editor.value.trim();
  if (!text) { setBadge('err', 'empty'); return; }
  clearError(); clearResults();
  setBadge('run', 'running…');
  setButtons(false);
  console.log('[CyberDSL] runSimulation fmt=%s', state.fmt);
  try {
    const r = await fetch('/api/simulate', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ text, fmt: state.fmt }),
    });
    const data = await r.json();
    console.log('[CyberDSL] simulate ok=%s steps=%d', data.ok, data.steps_run);
    if (!data.ok) { showError(data.error + (data.trace ? '\n'+data.trace : '')); setBadge('err', 'error'); return; }
    state.timeline = data.timeline;
    state.totalSteps = data.steps_run;
    state.mermaid = data.mermaid;
    if (data.model) { state.model = data.model; renderModelInfo(data.model); }
    await renderMermaid(data.mermaid, state.direction);
    renderAllCharts(data.timeline);
    graphSteps.textContent = `${data.steps_run} steps`;
    setBadge('ok', `done — ${data.steps_run} steps`);
  } catch(e) { console.error('[CyberDSL] runSimulation error:', e); showError(String(e)); setBadge('err', 'error'); }
  finally { setButtons(true); }
}

// ─── Stream simulation (SSE, step-by-step) ───────────────────────────────────
btnStream.addEventListener('click', streamSimulation);

async function streamSimulation() {
  if (state.streaming) return;
  const text = editor.value.trim();
  if (!text) { setBadge('err', 'empty'); return; }
  clearError(); clearResults();
  setBadge('run', 'streaming…');
  setButtons(false);
  state.streaming = true;
  state.timeline = [];

  streamProg.classList.remove('hidden');
  streamBar.style.width = '0%';
  streamLabel.textContent = 'Step 0';

  console.log('[CyberDSL] streamSimulation fmt=%s', state.fmt);
  try {
    const r = await fetch('/api/simulate/stream', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ text, fmt: state.fmt }),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({error: r.statusText}));
      showError(err.error || r.statusText); setBadge('err','error'); return;
    }

    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let totalSteps = 0;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop();
      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith('data:')) continue;
        const json_str = line.slice(5).trim();
        let msg;
        try { msg = JSON.parse(json_str); } catch { continue; }

        if (msg.type === 'meta') {
          state.model = msg.model;
          state.mermaid = msg.mermaid;
          totalSteps = msg.model.steps;
          state.totalSteps = totalSteps;
          console.log('[CyberDSL] stream meta model=%s steps=%d', msg.model.name, totalSteps);
          await renderMermaid(msg.mermaid, state.direction);
          renderModelInfo(msg.model);
          initStreamCharts(msg.model);
        } else if (msg.type === 'step') {
          state.timeline.push(msg.data);
          const pct = totalSteps > 0 ? Math.round(msg.data.step / totalSteps * 100) : 0;
          streamBar.style.width = pct + '%';
          streamLabel.textContent = `Step ${msg.data.step} / ${totalSteps}`;
          appendStreamPoint(msg.data);
        } else if (msg.type === 'done') {
          graphSteps.textContent = `${msg.steps_run} steps`;
          setBadge('ok', `done — ${msg.steps_run} steps`);
          streamBar.style.width = '100%';
          console.log('[CyberDSL] stream done steps=%d', msg.steps_run);
        }
      }
    }
  } catch(e) { console.error('[CyberDSL] stream error:', e); showError(String(e)); setBadge('err','error'); }
  finally { state.streaming = false; setButtons(true); streamProg.classList.add('hidden'); }
}

// ─── Mermaid rendering ────────────────────────────────────────────────────────
mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose',
  flowchart: { htmlLabels: false, curve: 'basis' } });

let _mmdCounter = 0;

async function renderMermaid(src, direction) {
  if (!src) return;
  const diagramSrc = src.replace(/^graph \S+/m, `graph ${direction}`);
  console.log('[CyberDSL] renderMermaid dir=%s len=%d', direction, diagramSrc.length);
  mermaidEl.classList.remove('mermaid-placeholder');
  try {
    _mmdCounter++;
    const id = 'mmd' + _mmdCounter;
    // remove any stale element mermaid might have left in <body>
    const stale = document.getElementById(id);
    if (stale) stale.remove();
    const { svg } = await mermaid.render(id, diagramSrc);
    mermaidEl.innerHTML = svg;
    console.log('[CyberDSL] Mermaid rendered OK id=%s', id);
  } catch(e) {
    console.error('[CyberDSL] Mermaid render error:', e);
    mermaidEl.innerHTML =
      `<pre style="color:#f85149;font-size:0.75rem;white-space:pre-wrap">Mermaid error:\n${e.message || String(e)}\n\nSource:\n${diagramSrc.slice(0,400)}</pre>`;
  }
}

// ─── Chart helpers ────────────────────────────────────────────────────────────
const CHART_OPTS = {
  type: 'line',
  options: {
    responsive: true,
    animation: false,
    interaction: { mode: 'index', intersect: false },
    plugins: { legend: { labels: { color: '#8b949e', boxWidth: 12, font: { size: 11 } } } },
    scales: {
      x: { ticks: { color: '#555', maxTicksLimit: 16 }, grid: { color: '#21262d' } },
      y: { min: 0, max: 1, ticks: { color: '#555' }, grid: { color: '#21262d' } },
    },
  },
};

function makeChart(canvasId, datasets, labels) {
  if (state.charts[canvasId]) { state.charts[canvasId].destroy(); }
  const ctx = document.getElementById(canvasId).getContext('2d');
  state.charts[canvasId] = new Chart(ctx, {
    ...CHART_OPTS,
    data: { labels: labels || [], datasets },
  });
  return state.charts[canvasId];
}

function destroyAllCharts() {
  Object.values(state.charts).forEach(c => c.destroy());
  state.charts = {};
}

// ─── Full-run chart rendering ─────────────────────────────────────────────────
function renderAllCharts(timeline) {
  destroyAllCharts();
  if (!timeline.length) return;

  const labels = timeline.map(s => s.step);
  const obsKeys = Object.keys(timeline[0].observables);
  const nodeIds = Object.keys(timeline[0].nodes);

  // Observables chart
  const obsDatasets = obsKeys.map((k, i) => ({
    label: k,
    data: timeline.map(s => s.observables[k]),
    borderColor: pal(i), backgroundColor: palA(i, 0.06),
    borderWidth: 2, pointRadius: 2, tension: 0.3, fill: false,
  }));
  const existingArea = $('panel-obs').querySelector('.chart-area');
  if (existingArea) existingArea.remove();
  const obsArea = document.createElement('div');
  obsArea.className = 'chart-area';
  obsArea.innerHTML = '<canvas id="chart-obs"></canvas>';
  $('panel-obs').prepend(obsArea);
  makeChart('chart-obs', obsDatasets, labels);

  // Node charts
  const grid = $('node-charts-grid');
  grid.innerHTML = '';
  nodeIds.forEach((nid) => {
    const vars = Object.keys(timeline[0].nodes[nid]);
    const card = document.createElement('div');
    card.className = 'node-chart-card';
    card.innerHTML = `<h3>${nid}</h3><canvas id="nc-${nid}"></canvas>`;
    grid.appendChild(card);
    const ds = vars.map((v, vi) => ({
      label: v,
      data: timeline.map(s => s.nodes[nid][v]),
      borderColor: pal(vi), backgroundColor: palA(vi, 0.06),
      borderWidth: 2, pointRadius: 2, tension: 0.3, fill: false,
    }));
    makeChart(`nc-${nid}`, ds, labels);
  });
  console.log('[CyberDSL] renderAllCharts obs=%d nodes=%d', obsKeys.length, nodeIds.length);
}

// ─── Stream chart init + update ───────────────────────────────────────────────
function initStreamCharts(modelMeta) {
  destroyAllCharts();
  const obsKeys = modelMeta.observables;
  const nodeIds = Object.keys(modelMeta.nodes);

  const existingArea = $('panel-obs').querySelector('.chart-area');
  if (existingArea) existingArea.remove();
  const obsArea = document.createElement('div');
  obsArea.className = 'chart-area';
  obsArea.innerHTML = '<canvas id="chart-obs"></canvas>';
  $('panel-obs').prepend(obsArea);
  const obsDatasets = obsKeys.map((k, i) => ({
    label: k, data: [],
    borderColor: pal(i), backgroundColor: palA(i, 0.06),
    borderWidth: 2, pointRadius: 2, tension: 0.3, fill: false,
  }));
  makeChart('chart-obs', obsDatasets, []);

  const grid = $('node-charts-grid');
  grid.innerHTML = '';
  nodeIds.forEach((nid) => {
    const vars = Object.keys(modelMeta.nodes[nid].state);
    const card = document.createElement('div');
    card.className = 'node-chart-card';
    card.innerHTML = `<h3>${nid}</h3><canvas id="nc-${nid}"></canvas>`;
    grid.appendChild(card);
    const ds = vars.map((v, vi) => ({
      label: v, data: [],
      borderColor: pal(vi), backgroundColor: palA(vi, 0.06),
      borderWidth: 2, pointRadius: 2, tension: 0.3, fill: false,
    }));
    makeChart(`nc-${nid}`, ds, []);
  });
  console.log('[CyberDSL] initStreamCharts obs=%d nodes=%d', obsKeys.length, nodeIds.length);
}

function appendStreamPoint(snap) {
  const obsChart = state.charts['chart-obs'];
  if (obsChart) {
    obsChart.data.labels.push(snap.step);
    const obsKeys = obsChart.data.datasets.map(d => d.label);
    obsKeys.forEach((k, i) => {
      obsChart.data.datasets[i].data.push(snap.observables[k] ?? null);
    });
    obsChart.update('none');
  }
  Object.keys(snap.nodes).forEach(nid => {
    const nc = state.charts[`nc-${nid}`];
    if (!nc) return;
    nc.data.labels.push(snap.step);
    const vars = nc.data.datasets.map(d => d.label);
    vars.forEach((v, i) => {
      nc.data.datasets[i].data.push(snap.nodes[nid][v] ?? null);
    });
    nc.update('none');
  });
}

// ─── Model info panel ─────────────────────────────────────────────────────────
function renderModelInfo(model) {
  infoContent.innerHTML = '';

  const meta = document.createElement('div');
  meta.className = 'info-card';
  meta.innerHTML = `<h3>Model</h3>
    <table class="kv-table">
      <tr><td>Name</td><td>${model.name}</td></tr>
      <tr><td>Steps</td><td>${model.steps}</td></tr>
      <tr><td>Nodes</td><td>${Object.keys(model.nodes).length}</td></tr>
      <tr><td>Edges</td><td>${model.edges.length}</td></tr>
      <tr><td>Rules</td><td>${model.rules_count}</td></tr>
      <tr><td>Observables</td><td>${model.observables.join(', ')}</td></tr>
    </table>`;
  infoContent.appendChild(meta);

  if (Object.keys(model.globals).length) {
    const gc = document.createElement('div');
    gc.className = 'info-card';
    gc.innerHTML = '<h3>Globals</h3><table class="kv-table"><tbody>' +
      Object.entries(model.globals).map(([k,v]) =>
        `<tr><td>${k}</td><td>${v.toFixed(3)}</td></tr>`).join('') +
      '</tbody></table>';
    infoContent.appendChild(gc);
  }

  const nc = document.createElement('div');
  nc.className = 'info-card';
  nc.innerHTML = '<h3>Nodes</h3>';
  const tbl = document.createElement('table');
  tbl.className = 'kv-table';
  Object.entries(model.nodes).forEach(([nid, n]) => {
    const stateStr = Object.entries(n.state).map(([k,v]) => `${k}=${v.toFixed(2)}`).join(' · ');
    const tr = document.createElement('tr');
    tr.innerHTML = `<td><strong>${nid}</strong> <span style="color:#8b949e">${n.kind}</span></td><td>${stateStr}</td>`;
    tbl.appendChild(tr);
  });
  nc.appendChild(tbl);
  infoContent.appendChild(nc);

  const ec = document.createElement('div');
  ec.className = 'info-card';
  ec.innerHTML = '<h3>Edges</h3>';
  const etbl = document.createElement('table');
  etbl.className = 'kv-table';
  model.edges.forEach(e => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${e.src} → ${e.dst}</td><td>${e.relation} w=${e.weight} d=${e.delay}</td>`;
    etbl.appendChild(tr);
  });
  ec.appendChild(etbl);
  infoContent.appendChild(ec);
}

// ─── UI helpers ───────────────────────────────────────────────────────────────
function setBadge(type, text) {
  statusBadge.className = 'badge ' + type;
  statusBadge.textContent = text;
}
function showError(msg) {
  parseError.textContent = msg;
  parseError.classList.remove('hidden');
}
function clearError() {
  parseError.textContent = '';
  parseError.classList.add('hidden');
}
function clearResults() {
  destroyAllCharts();
  $('node-charts-grid').innerHTML = '';
  const a = $('panel-obs').querySelector('.chart-area');
  if (a) a.remove();
}
function setButtons(enabled) {
  btnRun.disabled    = !enabled;
  btnStream.disabled = !enabled;
  btnParse.disabled  = !enabled;
}

// ─── Init ─────────────────────────────────────────────────────────────────────
console.log('[CyberDSL] Studio loaded. API at /api/  Ctrl+Enter=Parse  Ctrl+Shift+Enter=Run');
loadExampleList();
