"""
CyberDSL — Graph visualisation helpers.

Converts a ModelDef into:
  * Mermaid diagram code  (model_to_mermaid)
  * Stand-alone HTML viewer with Mermaid + YAML source (build_graph_viewer)
  * .mmd file writer      (save_mermaid)
  * full-page HTML writer (save_graph_viewer)
"""
from __future__ import annotations

from typing import Optional

from .parser import ModelDef


# ─── Kind → style mapping ─────────────────────────────────────────────────────

_KIND_SHAPE = {
    "group":       ("([", "])"),   # subroutine / rounded
    "actor":       ("([", "])"),   # subroutine
    "institution": ("[", "]"),     # rectangle
    "subsystem":   ("{", "}"),     # rhombus
}
_KIND_SHAPE_DEFAULT = ("[", "]")


def _node_shape(kind: str, label: str) -> str:
    lo, hi = _KIND_SHAPE.get(kind, _KIND_SHAPE_DEFAULT)
    return f"{lo}{label}{hi}"


# ─── Mermaid generator ────────────────────────────────────────────────────────

def model_to_mermaid(model: ModelDef, direction: str = "TD") -> str:
    """
    Convert a ModelDef to a Mermaid graph diagram string.

    Args:
        model:     Parsed ModelDef.
        direction: Mermaid graph direction — TD, LR, BT, RL.

    Returns:
        Mermaid source string, ready to embed in a <pre class="mermaid"> block
        or save as a .mmd file.
    """
    lines: list[str] = [f"graph {direction}"]

    # ── Node declarations with kind and initial state ──────────────────────────
    for nid, node in model.nodes.items():
        state_str = ", ".join(f"{k}={v:.2f}" for k, v in node.state.items())
        # Use plain label without newlines to avoid Mermaid parse errors
        label = f"{nid} [{node.kind}]"
        if state_str:
            label = f"{nid} [{node.kind}] {state_str}"
        shape_lo, shape_hi = _KIND_SHAPE.get(node.kind, _KIND_SHAPE_DEFAULT)
        lines.append(f"    {nid}{shape_lo}\"{label}\"{shape_hi}")

    lines.append("")

    # ── Edges ─────────────────────────────────────────────────────────────────
    for edge in model.edges:
        delay_str = f"d={edge.delay}" if edge.delay > 0 else "d=0"
        label = f"{edge.relation}|w={edge.weight}|{delay_str}"
        lines.append(f"    {edge.src} -->|\"{label}\"| {edge.dst}")

    lines.append("")

    # ── Globals subgraph ───────────────────────────────────────────────────────
    if model.globals:
        lines.append("    subgraph globals")
        for k, v in model.globals.items():
            lines.append(f"        {k}[\"{k}: {v:.2f}\"]")
        lines.append("    end")

    return "\n".join(lines)


# ─── Stand-alone HTML graph viewer ────────────────────────────────────────────

_VIEWER_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>CyberDSL Graph — {model_name}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, sans-serif; background: #0f1117; color: #e0e0e0; display: flex; flex-direction: column; height: 100vh; }}
  header {{ background: #1a1d27; padding: 1rem 2rem; border-bottom: 1px solid #2a2d3a; flex-shrink: 0; }}
  header h1 {{ font-size: 1.3rem; color: #a0c4ff; }}
  header p  {{ font-size: 0.8rem; color: #888; margin-top: 0.2rem; }}
  .layout {{ display: flex; flex: 1; overflow: hidden; }}
  .sidebar {{ width: 340px; flex-shrink: 0; background: #131620; border-right: 1px solid #2a2d3a;
              overflow-y: auto; padding: 1rem; display: flex; flex-direction: column; gap: 0.8rem; }}
  .sidebar h2 {{ font-size: 0.85rem; color: #7aadff; text-transform: uppercase; letter-spacing: 0.05em; }}
  .kv-table {{ width: 100%; border-collapse: collapse; font-size: 0.78rem; }}
  .kv-table td {{ padding: 0.25rem 0.4rem; border-bottom: 1px solid #1e2130; }}
  .kv-table td:first-child {{ color: #7aadff; }}
  .node-card {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 6px; padding: 0.6rem 0.8rem; }}
  .node-card .kind {{ font-size: 0.7rem; color: #888; margin-bottom: 0.3rem; }}
  .main {{ flex: 1; overflow: auto; padding: 2rem; display: flex; align-items: flex-start; justify-content: center; }}
  .mermaid svg {{ max-width: 100%; height: auto; }}
  .dir-bar {{ display: flex; gap: 0.4rem; flex-wrap: wrap; }}
  .dir-btn {{ padding: 0.3rem 0.7rem; border-radius: 4px; border: 1px solid #2a2d3a; background: #252836;
              color: #aaa; cursor: pointer; font-size: 0.78rem; transition: background 0.15s; }}
  .dir-btn:hover, .dir-btn.active {{ background: #2e4a80; color: #a0c4ff; border-color: #3a5a9f; }}
  .mmd-src {{ background: #131620; border: 1px solid #2a2d3a; border-radius: 6px; padding: 0.6rem;
              font-size: 0.7rem; color: #5a8aaa; white-space: pre; overflow-x: auto; }}
</style>
</head>
<body>
<header>
  <h1>CyberDSL Graph — {model_name}</h1>
  <p>Steps: {steps} &nbsp;·&nbsp; Nodes: {n_nodes} &nbsp;·&nbsp; Edges: {n_edges} &nbsp;·&nbsp; Rules: {n_rules}</p>
</header>
<div class="layout">

  <aside class="sidebar">
    <div>
      <h2>Direction</h2>
      <div class="dir-bar">
        <button class="dir-btn active" onclick="setDir('TD')">Top→Down</button>
        <button class="dir-btn" onclick="setDir('LR')">Left→Right</button>
        <button class="dir-btn" onclick="setDir('BT')">Bottom→Top</button>
        <button class="dir-btn" onclick="setDir('RL')">Right→Left</button>
      </div>
    </div>

    <div>
      <h2>Globals</h2>
      <table class="kv-table"><tbody>
{globals_rows}
      </tbody></table>
    </div>

    <div>
      <h2>Nodes</h2>
{node_cards}
    </div>

    <div>
      <h2>Mermaid source</h2>
      <div class="mmd-src" id="mmd-src">{mermaid_escaped}</div>
    </div>
  </aside>

  <main class="main">
    <div class="mermaid" id="diagram">{mermaid_code}</div>
  </main>

</div>
<script>
mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});

const DIAGRAMS = {diagrams_json};
let currentDir = 'TD';

function setDir(dir) {{
  currentDir = dir;
  document.querySelectorAll('.dir-btn').forEach(b => b.classList.toggle('active', b.textContent.startsWith(dir.charAt(0)+'→')||b.textContent.startsWith(dir)));
  const src = DIAGRAMS[dir];
  document.getElementById('mmd-src').textContent = src;
  const el = document.getElementById('diagram');
  el.removeAttribute('data-processed');
  el.innerHTML = src;
  mermaid.init(undefined, el);
}}
</script>
</body>
</html>
"""


def build_graph_viewer(model: ModelDef, yaml_source: Optional[str] = None) -> str:
    """
    Build a self-contained HTML graph viewer for a ModelDef.

    Args:
        model:       Parsed ModelDef.
        yaml_source: Optional original YAML/DSL text to show in sidebar.

    Returns:
        Complete HTML string.
    """
    import json

    diagrams = {d: model_to_mermaid(model, direction=d) for d in ("TD", "LR", "BT", "RL")}
    mermaid_td = diagrams["TD"]

    # Globals rows
    globals_rows = "\n".join(
        f"        <tr><td>{k}</td><td>{v:.3f}</td></tr>"
        for k, v in model.globals.items()
    ) or "        <tr><td colspan='2' style='color:#555'>—</td></tr>"

    # Node cards
    node_cards_html = []
    for nid, node in model.nodes.items():
        state_rows = "".join(
            f"<tr><td>{k}</td><td>{v:.3f}</td></tr>"
            for k, v in node.state.items()
        )
        params_rows = "".join(
            f"<tr><td>{k}</td><td>{v}</td></tr>"
            for k, v in node.params.items()
        )
        node_cards_html.append(
            f'      <div class="node-card">'
            f'<div class="kind">{node.kind}</div>'
            f'<strong>{nid}</strong>'
            f'<table class="kv-table"><tbody>{state_rows}{params_rows}</tbody></table>'
            f'</div>'
        )

    # Escape mermaid for display
    mermaid_escaped = mermaid_td.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html = _VIEWER_TEMPLATE.format(
        model_name=model.name,
        steps=model.steps,
        n_nodes=len(model.nodes),
        n_edges=len(model.edges),
        n_rules=len(model.rules),
        globals_rows=globals_rows,
        node_cards="\n".join(node_cards_html),
        mermaid_escaped=mermaid_escaped,
        mermaid_code=mermaid_td,
        diagrams_json=json.dumps(diagrams),
    )
    return html


def save_mermaid(model: ModelDef, path: str, direction: str = "TD") -> None:
    """Write Mermaid source to a .mmd file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(model_to_mermaid(model, direction=direction))


def save_graph_viewer(model: ModelDef, path: str, yaml_source: Optional[str] = None) -> None:
    """Write the HTML graph viewer to `path`."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(build_graph_viewer(model, yaml_source=yaml_source))
