"""Tests for CyberDSL parser and simulation runtime."""
from __future__ import annotations

import pytest
from cyberdsl.parser import parse_dsl
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
