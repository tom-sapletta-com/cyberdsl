"""Tests for CyberDSL parser and simulation runtime."""
from __future__ import annotations

import pytest
from cyberdsl.parser import parse_dsl, parse_yaml, dsl_to_yaml
from cyberdsl.models import ModelCompiler, Simulation

SIMPLE_DSL = """
model:
  name = "TestModel"
  steps = 5

globals:
  stress = 0.30
  support = 0.60

nodes:
  a:group | state={x:0.50, y:0.40} | alpha=0.8
  b:institution | state={x:0.70, trust:0.60} | authority=0.9

edges:
  a->b:influence | weight=0.40 | delay=0
  b->a:feedback  | weight=0.30 | delay=1

rules:
  a.x => clip(self['x'] + 0.10*sum_influence - 0.05*globals['stress'])
  b.x => clip(self['x'] + 0.08*signals.get('w_a',0)*signals.get('sig_a',{}).get('x',0))

observables:
  avg_x = (nodes['a']['x'] + nodes['b']['x']) / 2
  gap   = abs(nodes['a']['x'] - nodes['b']['x'])
"""


def test_parse_model_meta():
    m = parse_dsl(SIMPLE_DSL)
    assert m.name == "TestModel"
    assert m.steps == 5


def test_parse_globals():
    m = parse_dsl(SIMPLE_DSL)
    assert abs(m.globals['stress'] - 0.30) < 1e-9
    assert abs(m.globals['support'] - 0.60) < 1e-9


def test_parse_nodes():
    m = parse_dsl(SIMPLE_DSL)
    assert 'a' in m.nodes
    assert 'b' in m.nodes
    assert m.nodes['a'].kind == 'group'
    assert abs(m.nodes['a'].state['x'] - 0.50) < 1e-9
    assert abs(m.nodes['b'].state['trust'] - 0.60) < 1e-9


def test_parse_edges():
    m = parse_dsl(SIMPLE_DSL)
    assert len(m.edges) == 2
    edge = m.edges[0]
    assert edge.src == 'a'
    assert edge.dst == 'b'
    assert abs(edge.weight - 0.40) < 1e-9
    assert edge.delay == 0


def test_parse_rules():
    m = parse_dsl(SIMPLE_DSL)
    assert len(m.rules) == 2
    assert m.rules[0].node == 'a'
    assert m.rules[0].var == 'x'


def test_parse_observables():
    m = parse_dsl(SIMPLE_DSL)
    assert 'avg_x' in m.observables
    assert 'gap' in m.observables


def test_simulation_runs():
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run(steps=5)
    assert result.steps_run == 5
    assert len(result.timeline) == 5


def test_simulation_observables():
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run(steps=5)
    last = result.timeline[-1]
    assert 'avg_x' in last['observables']
    assert 0.0 <= last['observables']['avg_x'] <= 1.0


def test_simulation_clip_bounds():
    """State variables after rules should stay in [0,1]."""
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run(steps=10)
    for snap in result.timeline:
        for nid, state in snap['nodes'].items():
            for var, val in state.items():
                assert 0.0 <= val <= 1.0, f"{nid}.{var}={val} out of bounds"


def test_shock_api():
    model = ModelCompiler().parse(SIMPLE_DSL)
    sim = Simulation(model)
    sim.run(steps=2)
    sim.apply_shock('a', 'x', -0.5)
    assert 0.0 <= sim._states['a']['x'] <= 1.0


def test_observables_over_time():
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run()
    ot = result.observables_over_time()
    assert 'avg_x' in ot
    assert len(ot['avg_x']) == model.steps


def test_example_file():
    """Run the bundled example.cyberdsl."""
    import pathlib
    p = pathlib.Path(__file__).parent.parent / "example.cyberdsl"
    if not p.exists():
        pytest.skip("example.cyberdsl not found")
    model = ModelCompiler().parse(p.read_text(encoding='utf-8'))
    result = Simulation(model).run()
    assert len(result.timeline) == model.steps
    print(result.summary())


# ─── YAML tests ───────────────────────────────────────────────────────────────

SIMPLE_YAML = """
model:
  name: TestModelYAML
  steps: 5

globals:
  stress: 0.30
  support: 0.60

nodes:
  a:
    kind: group
    state: {x: 0.50, y: 0.40}
    params: {alpha: 0.8}
  b:
    kind: institution
    state: {x: 0.70, trust: 0.60}
    params: {authority: 0.9}

edges:
  - src: a
    dst: b
    relation: influence
    weight: 0.40
    delay: 0
  - src: b
    dst: a
    relation: feedback
    weight: 0.30
    delay: 1

rules:
  - node: a
    var: x
    expr: "clip(self['x'] + 0.10*sum_influence - 0.05*globals['stress'])"
  - node: b
    var: x
    expr: "clip(self['x'] + 0.08*signals.get('w_a',0)*signals.get('sig_a',{}).get('x',0))"

observables:
  avg_x: "(nodes['a']['x'] + nodes['b']['x']) / 2"
  gap: "abs(nodes['a']['x'] - nodes['b']['x'])"
"""


def test_parse_yaml_meta():
    m = parse_yaml(SIMPLE_YAML)
    assert m.name == "TestModelYAML"
    assert m.steps == 5


def test_parse_yaml_globals():
    m = parse_yaml(SIMPLE_YAML)
    assert abs(m.globals['stress'] - 0.30) < 1e-9
    assert abs(m.globals['support'] - 0.60) < 1e-9


def test_parse_yaml_nodes():
    m = parse_yaml(SIMPLE_YAML)
    assert 'a' in m.nodes and 'b' in m.nodes
    assert m.nodes['a'].kind == 'group'
    assert abs(m.nodes['a'].state['x'] - 0.50) < 1e-9
    assert abs(m.nodes['b'].state['trust'] - 0.60) < 1e-9


def test_parse_yaml_edges():
    m = parse_yaml(SIMPLE_YAML)
    assert len(m.edges) == 2
    assert m.edges[0].src == 'a' and m.edges[0].dst == 'b'
    assert abs(m.edges[0].weight - 0.40) < 1e-9


def test_parse_yaml_rules():
    m = parse_yaml(SIMPLE_YAML)
    assert len(m.rules) == 2
    assert m.rules[0].node == 'a' and m.rules[0].var == 'x'


def test_parse_yaml_observables():
    m = parse_yaml(SIMPLE_YAML)
    assert 'avg_x' in m.observables and 'gap' in m.observables


def test_yaml_simulation_runs():
    m = parse_yaml(SIMPLE_YAML)
    result = Simulation(m).run(steps=5)
    assert result.steps_run == 5
    assert len(result.timeline) == 5


def test_dsl_to_yaml_roundtrip():
    """DSL → YAML → parse_yaml should produce equivalent ModelDef."""
    yaml_text = dsl_to_yaml(SIMPLE_DSL)
    m_yaml = parse_yaml(yaml_text)
    m_dsl = parse_dsl(SIMPLE_DSL)
    assert m_yaml.name == m_dsl.name
    assert m_yaml.steps == m_dsl.steps
    assert set(m_yaml.nodes) == set(m_dsl.nodes)
    assert len(m_yaml.edges) == len(m_dsl.edges)
    assert len(m_yaml.rules) == len(m_dsl.rules)
    assert set(m_yaml.observables) == set(m_dsl.observables)


def test_dsl_to_yaml_is_valid_yaml():
    import yaml
    yaml_text = dsl_to_yaml(SIMPLE_DSL)
    data = yaml.safe_load(yaml_text)
    assert 'model' in data and 'nodes' in data


# ─── CSV export ───────────────────────────────────────────────────────────────

def test_csv_export_columns():
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run(steps=5)
    csv_text = result.to_csv()
    lines = csv_text.strip().splitlines()
    assert len(lines) == 6  # header + 5 data rows
    header = lines[0]
    assert 'step' in header
    assert 'obs_avg_x' in header
    assert 'a_x' in header


def test_csv_export_step_values():
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run(steps=3)
    csv_text = result.to_csv()
    rows = csv_text.strip().splitlines()
    assert rows[1].startswith('1,')
    assert rows[3].startswith('3,')


def test_save_csv(tmp_path):
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run(steps=3)
    out = tmp_path / "test.csv"
    result.save_csv(str(out))
    assert out.exists()
    content = out.read_text()
    assert 'step' in content


# ─── HTML dashboard ───────────────────────────────────────────────────────────

def test_build_dashboard_returns_html():
    from cyberdsl.dashboard import build_dashboard
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run(steps=5)
    html = build_dashboard(result)
    assert html.startswith('<!DOCTYPE html>')
    assert 'chart.js' in html.lower()
    assert 'avg_x' in html


def test_save_dashboard(tmp_path):
    from cyberdsl.dashboard import save_dashboard
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run(steps=5)
    out = tmp_path / "report.html"
    save_dashboard(result, str(out))
    assert out.exists()
    assert out.stat().st_size > 2000


def test_dashboard_with_mc(tmp_path):
    from cyberdsl.dashboard import save_dashboard
    from cyberdsl.models import run_monte_carlo
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run(steps=5)
    mc = run_monte_carlo(model, n_runs=10, steps=5, seed=42)
    out = tmp_path / "mc_report.html"
    save_dashboard(result, str(out), mc=mc)
    content = out.read_text()
    assert 'Monte Carlo' in content


# ─── Monte Carlo ──────────────────────────────────────────────────────────────

def test_monte_carlo_run_count():
    from cyberdsl.models import run_monte_carlo
    model = ModelCompiler().parse(SIMPLE_DSL)
    mc = run_monte_carlo(model, n_runs=20, steps=5, seed=0)
    assert mc.n_runs == 20
    assert len(mc.runs) == 20


def test_monte_carlo_mean_length():
    from cyberdsl.models import run_monte_carlo
    model = ModelCompiler().parse(SIMPLE_DSL)
    mc = run_monte_carlo(model, n_runs=10, steps=5, seed=1)
    mean = mc.mean_observable('avg_x')
    assert len(mean) == 5


def test_monte_carlo_bounds():
    from cyberdsl.models import run_monte_carlo
    model = ModelCompiler().parse(SIMPLE_DSL)
    mc = run_monte_carlo(model, n_runs=30, steps=5, seed=2)
    for step_mean in mc.mean_observable('avg_x'):
        assert 0.0 <= step_mean <= 1.0
    for step_std in mc.std_observable('avg_x'):
        assert step_std >= 0.0


def test_monte_carlo_percentiles():
    from cyberdsl.models import run_monte_carlo
    model = ModelCompiler().parse(SIMPLE_DSL)
    mc = run_monte_carlo(model, n_runs=50, steps=5, seed=3)
    p10 = mc.percentile_observable('avg_x', 10)
    p90 = mc.percentile_observable('avg_x', 90)
    for lo, hi in zip(p10, p90):
        assert lo <= hi


def test_monte_carlo_reproducible():
    from cyberdsl.models import run_monte_carlo
    model = ModelCompiler().parse(SIMPLE_DSL)
    mc1 = run_monte_carlo(model, n_runs=10, steps=5, seed=99)
    mc2 = run_monte_carlo(model, n_runs=10, steps=5, seed=99)
    assert mc1.mean_observable('avg_x') == mc2.mean_observable('avg_x')


# ─── run_scenario ─────────────────────────────────────────────────────────────

def test_run_scenario_shock():
    model = ModelCompiler().parse(SIMPLE_DSL)
    sim = Simulation(model)
    result = sim.run_scenario(
        shock_at={3: [('a', 'x', -0.3)]},
        steps=5,
    )
    assert result.steps_run == 5
    assert len(result.timeline) == 5


def test_run_scenario_global_change():
    model = ModelCompiler().parse(SIMPLE_DSL)
    sim = Simulation(model)
    result = sim.run_scenario(
        global_at={2: {'stress': 0.9}},
        steps=5,
    )
    assert len(result.timeline) == 5


# ─── Harbor community example ─────────────────────────────────────────────────

def test_harbor_community_example():
    import pathlib
    p = pathlib.Path(__file__).parent.parent / "examples" / "harbor_community.cyberdsl"
    if not p.exists():
        pytest.skip("harbor_community.cyberdsl not found")
    model = ModelCompiler().parse(p.read_text(encoding='utf-8'))
    result = Simulation(model).run()
    assert len(result.timeline) == model.steps
    last = result.timeline[-1]
    assert 'instability_risk' in last['observables']
    assert 'community_health' in last['observables']


def test_harbor_community_clip_bounds():
    import pathlib
    p = pathlib.Path(__file__).parent.parent / "examples" / "harbor_community.cyberdsl"
    if not p.exists():
        pytest.skip("harbor_community.cyberdsl not found")
    model = ModelCompiler().parse(p.read_text(encoding='utf-8'))
    result = Simulation(model).run()
    for snap in result.timeline:
        for nid, state in snap['nodes'].items():
            for var, val in state.items():
                assert 0.0 <= val <= 1.0, f"{nid}.{var}={val} out of bounds"


# ─── Graph / Mermaid ──────────────────────────────────────────────────────────

def test_model_to_mermaid_contains_nodes():
    from cyberdsl.graph import model_to_mermaid
    model = ModelCompiler().parse(SIMPLE_DSL)
    mmd = model_to_mermaid(model)
    assert 'graph TD' in mmd
    assert 'a' in mmd
    assert 'b' in mmd


def test_model_to_mermaid_contains_edges():
    from cyberdsl.graph import model_to_mermaid
    model = ModelCompiler().parse(SIMPLE_DSL)
    mmd = model_to_mermaid(model)
    assert '-->' in mmd
    assert 'influence' in mmd


def test_model_to_mermaid_contains_globals():
    from cyberdsl.graph import model_to_mermaid
    model = ModelCompiler().parse(SIMPLE_DSL)
    mmd = model_to_mermaid(model)
    assert 'subgraph globals' in mmd
    assert 'stress' in mmd


def test_model_to_mermaid_directions():
    from cyberdsl.graph import model_to_mermaid
    model = ModelCompiler().parse(SIMPLE_DSL)
    for d in ('TD', 'LR', 'BT', 'RL'):
        mmd = model_to_mermaid(model, direction=d)
        assert f'graph {d}' in mmd


def test_build_graph_viewer_returns_html():
    from cyberdsl.graph import build_graph_viewer
    model = ModelCompiler().parse(SIMPLE_DSL)
    html = build_graph_viewer(model)
    assert html.startswith('<!DOCTYPE html>')
    assert 'mermaid' in html.lower()
    assert 'graph TD' in html


def test_build_graph_viewer_contains_node_info():
    from cyberdsl.graph import build_graph_viewer
    model = ModelCompiler().parse(SIMPLE_DSL)
    html = build_graph_viewer(model)
    assert 'stress' in html
    assert 'a' in html
    assert 'b' in html


def test_save_mermaid(tmp_path):
    from cyberdsl.graph import save_mermaid
    model = ModelCompiler().parse(SIMPLE_DSL)
    out = tmp_path / "model.mmd"
    save_mermaid(model, str(out))
    assert out.exists()
    content = out.read_text()
    assert 'graph TD' in content
    assert '-->' in content


def test_save_graph_viewer(tmp_path):
    from cyberdsl.graph import save_graph_viewer
    model = ModelCompiler().parse(SIMPLE_DSL)
    out = tmp_path / "model_graph.html"
    save_graph_viewer(model, str(out))
    assert out.exists()
    assert out.stat().st_size > 3000


def test_dashboard_graph_tab(tmp_path):
    from cyberdsl.dashboard import save_dashboard
    model = ModelCompiler().parse(SIMPLE_DSL)
    result = Simulation(model).run(steps=5)
    out = tmp_path / "dash_graph.html"
    save_dashboard(result, str(out), model=model)
    content = out.read_text()
    assert 'panel-graph' in content
    assert 'graph TD' in content
    assert 'mermaid' in content.lower()


def test_mermaid_yaml_model(tmp_path):
    from cyberdsl.graph import model_to_mermaid
    from cyberdsl.parser import parse_yaml
    model = parse_yaml(SIMPLE_YAML)
    mmd = model_to_mermaid(model)
    assert 'graph TD' in mmd
    assert 'a' in mmd and 'b' in mmd
