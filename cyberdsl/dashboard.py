"""
CyberDSL — HTML Dashboard Generator.

Generates a self-contained, single-file HTML report with interactive
Chart.js charts for simulation results and optional Monte Carlo bands.

Usage:
    from cyberdsl.dashboard import build_dashboard
    html = build_dashboard(result, mc_result=mc)
    open('report.html', 'w').write(html)
"""
from __future__ import annotations

import json
from typing import Any, Optional

from .models import SimulationResult, MonteCarloResult
from .graph import model_to_mermaid


# ─── Colour palette ───────────────────────────────────────────────────────────

_PALETTE = [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
    "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac",
]


def _hex_alpha(hex_color: str, alpha: float) -> str:
    """Convert '#rrggbb' + alpha to 'rgba(r,g,b,a)'."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ─── Data helpers ─────────────────────────────────────────────────────────────

def _steps_labels(result: SimulationResult) -> list[int]:
    return [snap['step'] for snap in result.timeline]


def _obs_datasets(
    result: SimulationResult,
    mc: Optional[MonteCarloResult] = None,
) -> list[dict[str, Any]]:
    """Build Chart.js datasets for all observables."""
    obs_keys = list(result.timeline[0].get('observables', {}).keys())
    datasets: list[dict[str, Any]] = []

    for i, key in enumerate(obs_keys):
        color = _PALETTE[i % len(_PALETTE)]
        vals = [snap['observables'].get(key) for snap in result.timeline]
        ds: dict[str, Any] = {
            "label": key,
            "data": vals,
            "borderColor": color,
            "backgroundColor": _hex_alpha(color, 0.08),
            "borderWidth": 2,
            "pointRadius": 2,
            "tension": 0.3,
            "fill": False,
        }
        datasets.append(ds)

        if mc is not None:
            mean = mc.mean_observable(key)
            p10 = mc.percentile_observable(key, 10)
            p90 = mc.percentile_observable(key, 90)
            datasets.append({
                "label": f"{key} p90",
                "data": p90,
                "borderColor": _hex_alpha(color, 0.0),
                "backgroundColor": _hex_alpha(color, 0.15),
                "borderWidth": 0,
                "pointRadius": 0,
                "fill": "+1",
                "tension": 0.3,
            })
            datasets.append({
                "label": f"{key} p10",
                "data": p10,
                "borderColor": _hex_alpha(color, 0.0),
                "backgroundColor": _hex_alpha(color, 0.15),
                "borderWidth": 0,
                "pointRadius": 0,
                "fill": False,
                "tension": 0.3,
            })
            datasets.append({
                "label": f"{key} mean (MC)",
                "data": mean,
                "borderColor": color,
                "backgroundColor": _hex_alpha(color, 0.0),
                "borderWidth": 1,
                "borderDash": [6, 3],
                "pointRadius": 0,
                "fill": False,
                "tension": 0.3,
            })

    return datasets


def _node_datasets(result: SimulationResult) -> dict[str, list[dict[str, Any]]]:
    """Return {node_id: [Chart.js dataset, ...]} for all node variables."""
    first = result.timeline[0]
    node_ids = list(first.get('nodes', {}).keys())
    out: dict[str, list[dict[str, Any]]] = {}
    for nid in node_ids:
        vars_ = list(first['nodes'].get(nid, {}).keys())
        datasets = []
        for i, var in enumerate(vars_):
            color = _PALETTE[i % len(_PALETTE)]
            vals = [snap['nodes'].get(nid, {}).get(var) for snap in result.timeline]
            datasets.append({
                "label": var,
                "data": vals,
                "borderColor": color,
                "backgroundColor": _hex_alpha(color, 0.08),
                "borderWidth": 2,
                "pointRadius": 2,
                "tension": 0.3,
                "fill": False,
            })
        out[nid] = datasets
    return out


# ─── HTML template ────────────────────────────────────────────────────────────

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>CyberDSL — {model_name}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, sans-serif; background: #0f1117; color: #e0e0e0; }}
  header {{ background: #1a1d27; padding: 1.2rem 2rem; border-bottom: 1px solid #2a2d3a; }}
  header h1 {{ font-size: 1.4rem; font-weight: 600; color: #a0c4ff; }}
  header p  {{ font-size: 0.85rem; color: #888; margin-top: 0.2rem; }}
  .tabs {{ display: flex; gap: 0.25rem; padding: 0.75rem 2rem 0; background: #1a1d27; border-bottom: 1px solid #2a2d3a; flex-wrap: wrap; }}
  .tab  {{ padding: 0.45rem 1.1rem; cursor: pointer; border-radius: 6px 6px 0 0; font-size: 0.82rem;
           background: #252836; color: #999; border: 1px solid #2a2d3a; border-bottom: none; transition: background 0.15s; }}
  .tab:hover {{ background: #2e3148; color: #ccc; }}
  .tab.active {{ background: #0f1117; color: #a0c4ff; border-color: #2a2d3a; }}
  .panel {{ display: none; padding: 1.5rem 2rem; }}
  .panel.active {{ display: block; }}
  .chart-wrap {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px;
                 padding: 1rem; margin-bottom: 1.5rem; }}
  .chart-wrap h2 {{ font-size: 1rem; margin-bottom: 0.75rem; color: #c0c8e0; font-weight: 500; }}
  canvas {{ max-height: 340px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 1rem; }}
  .summary-box {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px; padding: 1rem; }}
  .summary-box h2 {{ font-size: 1rem; color: #c0c8e0; margin-bottom: 0.6rem; }}
  .kv-table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
  .kv-table td {{ padding: 0.3rem 0.5rem; border-bottom: 1px solid #23263a; }}
  .kv-table td:first-child {{ color: #7aadff; width: 55%; }}
  .mc-badge {{ display: inline-block; background: #1e3a5f; color: #7aadff; border-radius: 4px;
               font-size: 0.72rem; padding: 0.1rem 0.45rem; margin-left: 0.4rem; vertical-align: middle; }}
  .dir-btn {{ padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid #2a2d3a; background: #252836;
              color: #aaa; cursor: pointer; font-size: 0.75rem; }}
  .dir-btn.active {{ background: #2e4a80; color: #a0c4ff; border-color: #3a5a9f; }}
  @media (max-width: 600px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<header>
  <h1>CyberDSL — {model_name}</h1>
  <p>Steps: {steps_run} &nbsp;·&nbsp; Nodes: {n_nodes} &nbsp;·&nbsp; Observables: {n_obs}{mc_badge}</p>
</header>

<div class="tabs" id="tabs">
  <div class="tab active" data-panel="panel-obs">Observables</div>
  <div class="tab" data-panel="panel-nodes">Nodes</div>
  <div class="tab" data-panel="panel-summary">Summary</div>
  <div class="tab" data-panel="panel-graph">Graph</div>
</div>

<div id="panel-obs" class="panel active">
  <div class="chart-wrap">
    <h2>Observables over time</h2>
    <canvas id="chart-obs"></canvas>
  </div>
</div>

<div id="panel-nodes" class="panel">
  <div class="grid" id="node-grid"></div>
</div>

<div id="panel-summary" class="panel">
  <div class="grid" id="summary-grid"></div>
</div>

<div id="panel-graph" class="panel">
  <div class="chart-wrap">
    <h2>Model structure — Mermaid graph
      <span style="float:right;font-size:0.78rem;color:#777">
        Direction:
        <span id="dir-btns" style="display:inline-flex;gap:0.3rem;margin-left:0.4rem">
          <button class="dir-btn active" onclick="setDir('TD')">TD</button>
          <button class="dir-btn" onclick="setDir('LR')">LR</button>
          <button class="dir-btn" onclick="setDir('BT')">BT</button>
          <button class="dir-btn" onclick="setDir('RL')">RL</button>
        </span>
      </span>
    </h2>
    <div id="mermaid-wrap" style="background:#131620;border-radius:8px;padding:1.5rem;overflow:auto;min-height:300px">
      <div class="mermaid" id="mermaid-diagram">{mermaid_td}</div>
    </div>
    <details style="margin-top:0.8rem">
      <summary style="cursor:pointer;font-size:0.78rem;color:#666">Mermaid source (.mmd)</summary>
      <pre id="mmd-src" style="font-size:0.7rem;color:#5a8aaa;margin-top:0.5rem;white-space:pre;overflow-x:auto">{mermaid_escaped}</pre>
    </details>
  </div>
</div>

<script>
const LABELS   = {labels_json};
const OBS_DS   = {obs_ds_json};
const NODE_DS  = {node_ds_json};
const LAST_OBS = {last_obs_json};
const LAST_NODES = {last_nodes_json};

const CHART_DEFAULTS = {{
  type: 'line',
  options: {{
    responsive: true,
    interaction: {{ mode: 'index', intersect: false }},
    plugins: {{ legend: {{ labels: {{ color: '#ccc', boxWidth: 12, font: {{ size: 11 }} }} }} }},
    scales: {{
      x: {{ ticks: {{ color: '#777', maxTicksLimit: 12 }}, grid: {{ color: '#2a2d3a' }} }},
      y: {{ min: 0, max: 1, ticks: {{ color: '#777' }}, grid: {{ color: '#2a2d3a' }} }},
    }},
  }},
}};

function makeChart(id, datasets) {{
  const ctx = document.getElementById(id).getContext('2d');
  return new Chart(ctx, {{ ...CHART_DEFAULTS, data: {{ labels: LABELS, datasets }} }});
}}

// Observables chart
makeChart('chart-obs', OBS_DS);

// Node charts
const grid = document.getElementById('node-grid');
Object.entries(NODE_DS).forEach(([nid, ds]) => {{
  const wrap = document.createElement('div');
  wrap.className = 'chart-wrap';
  wrap.innerHTML = `<h2>${{nid}}</h2><canvas id="nc-${{nid}}"></canvas>`;
  grid.appendChild(wrap);
  makeChart(`nc-${{nid}}`, ds);
}});

// Summary table — last step
const sg = document.getElementById('summary-grid');

const obsBox = document.createElement('div');
obsBox.className = 'summary-box';
obsBox.innerHTML = '<h2>Final observables</h2>' +
  '<table class="kv-table"><tbody>' +
  Object.entries(LAST_OBS).map(([k,v]) =>
    `<tr><td>${{k}}</td><td>${{typeof v === 'number' ? v.toFixed(4) : v}}</td></tr>`
  ).join('') + '</tbody></table>';
sg.appendChild(obsBox);

Object.entries(LAST_NODES).forEach(([nid, state]) => {{
  const box = document.createElement('div');
  box.className = 'summary-box';
  box.innerHTML = `<h2>${{nid}}</h2>` +
    '<table class="kv-table"><tbody>' +
    Object.entries(state).map(([k,v]) =>
      `<tr><td>${{k}}</td><td>${{typeof v === 'number' ? v.toFixed(4) : v}}</td></tr>`
    ).join('') + '</tbody></table>';
  sg.appendChild(box);
}});

// Tab switching
document.getElementById('tabs').addEventListener('click', e => {{
  const tab = e.target.closest('.tab');
  if (!tab) return;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  tab.classList.add('active');
  const panel = document.getElementById(tab.dataset.panel);
  panel.classList.add('active');
  if (tab.dataset.panel === 'panel-graph') initMermaid();
}});

// Mermaid
const DIAGRAMS = {diagrams_json};
let mermaidReady = false;
function initMermaid() {{
  if (mermaidReady) return;
  mermaidReady = true;
  mermaid.initialize({{ startOnLoad: false, theme: 'dark' }});
  mermaid.init(undefined, document.getElementById('mermaid-diagram'));
}}
function setDir(dir) {{
  document.querySelectorAll('.dir-btn').forEach(b => b.classList.toggle('active', b.textContent === dir));
  const src = DIAGRAMS[dir];
  document.getElementById('mmd-src').textContent = src;
  const el = document.getElementById('mermaid-diagram');
  el.removeAttribute('data-processed');
  el.innerHTML = src;
  mermaid.init(undefined, el);
}}
</script>
</body>
</html>
"""


def build_dashboard(
    result: SimulationResult,
    mc: Optional[MonteCarloResult] = None,
    model=None,
) -> str:
    """
    Build a self-contained HTML dashboard for a simulation result.

    Args:
        result: A SimulationResult from Simulation.run() or run_scenario().
        mc:     Optional MonteCarloResult for uncertainty bands.
        model:  Optional ModelDef for the Graph tab (Mermaid diagram).

    Returns:
        Complete HTML string, ready to write to a .html file.
    """
    labels = _steps_labels(result)
    obs_ds = _obs_datasets(result, mc)
    node_ds = _node_datasets(result)
    last = result.timeline[-1] if result.timeline else {}
    last_obs = last.get('observables', {})
    last_nodes = last.get('nodes', {})

    mc_badge = (
        f'&nbsp;·&nbsp; MC runs: {mc.n_runs} <span class="mc-badge">Monte Carlo</span>'
        if mc else ""
    )

    # Mermaid graph
    if model is not None:
        diagrams = {d: model_to_mermaid(model, direction=d) for d in ("TD", "LR", "BT", "RL")}
    else:
        diagrams = {d: "graph TD\n    no_model[Model not provided]" for d in ("TD", "LR", "BT", "RL")}
    mermaid_td = diagrams["TD"]
    mermaid_escaped = mermaid_td.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html = _HTML_TEMPLATE.format(
        model_name=result.model_name,
        steps_run=result.steps_run,
        n_nodes=len(last_nodes),
        n_obs=len(last_obs),
        mc_badge=mc_badge,
        labels_json=json.dumps(labels),
        obs_ds_json=json.dumps(obs_ds),
        node_ds_json=json.dumps(node_ds),
        last_obs_json=json.dumps(last_obs),
        last_nodes_json=json.dumps(last_nodes),
        mermaid_td=mermaid_td,
        mermaid_escaped=mermaid_escaped,
        diagrams_json=json.dumps(diagrams),
    )
    return html


def save_dashboard(
    result: SimulationResult,
    path: str,
    mc: Optional[MonteCarloResult] = None,
    model=None,
) -> None:
    """Write the HTML dashboard to `path`."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(build_dashboard(result, mc=mc, model=model))
