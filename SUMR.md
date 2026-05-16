# CyberDSL

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `cyberdsl`
- **version**: `0.2.1`
- **python_requires**: `>=3.10`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(6 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: cyberdsl;
  version: 0.2.1;
}

dependencies {
  runtime: litellm>=1.0.0;
  dev: "pytest>=7.0, pytest-cov, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="cyberdsl"] {

}

deploy {
  target: pip;
}

environment[name="local"] {
  runtime: python;
  env_file: .env;
  python_version: >=3.10;
}
```

### Source Modules

- `cyberdsl.dashboard`
- `cyberdsl.graph`
- `cyberdsl.litellm_adapter`
- `cyberdsl.models`
- `cyberdsl.parser`
- `cyberdsl.webapp`

## Dependencies

### Runtime

```text markpact:deps python
litellm>=1.0.0
```

### Development

```text markpact:deps python scope=dev
pytest>=7.0
pytest-cov
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `cyberdsl.models` (`cyberdsl/models.py`)

```python
def _safe_clip(x, lo, hi)  # CC=1, fan=3
def run_monte_carlo(model, n_runs, steps, noise_std, seed)  # CC=6, fan=12
class ModelCompiler:
    def parse(dsl)  # CC=1
    def _validate(model)  # CC=6
class SimulationResult:
    def observables_over_time()  # CC=3
    def node_state_over_time(node_id, var)  # CC=2
    def summary()  # CC=7
    def to_csv()  # CC=9
    def save_csv(path)  # CC=1
class Simulation:
    def __init__(model)  # CC=2
    def _build_signals(node_id, step)  # CC=5
    def _push_signals()  # CC=5
    def _eval_rules(step)  # CC=4
    def _eval_observables()  # CC=3
    def step(step_no)  # CC=1
    def run(steps)  # CC=3
    def apply_shock(node_id, var, delta)  # CC=3
    def set_global(key, value)  # CC=1
    def run_scenario(shock_at, global_at, steps)  # CC=9
class MonteCarloResult:
    def mean_observable(name)  # CC=5
    def std_observable(name)  # CC=5
    def percentile_observable(name, p)  # CC=6
```

### `cyberdsl.webapp` (`cyberdsl/webapp.py`)

```python
def _parse_model(text, fmt)  # CC=2, fan=3
def _model_meta(model)  # CC=3, fan=4
def _snap_to_json(snap)  # CC=6, fan=5
def _find_example(name)  # CC=3, fan=1
def _list_examples()  # CC=7, fan=7
def handle_favicon(request)  # CC=1, fan=2
def handle_index(request)  # CC=1, fan=2
def handle_static(request)  # CC=4, fan=6
def handle_parse(request)  # CC=3, fan=10
def handle_simulate(request)  # CC=5, fan=14
def handle_simulate_stream(request)  # CC=6, fan=20
def handle_mermaid(request)  # CC=3, fan=9
def handle_list_examples(request)  # CC=1, fan=2
def handle_get_example(request)  # CC=3, fan=5
def access_log_middleware(request, handler)  # CC=1, fan=2
def create_app()  # CC=1, fan=3
def run(host, port)  # CC=1, fan=3
```

### `cyberdsl.parser` (`cyberdsl/parser.py`)

```python
def _strip_inline_comment(line)  # CC=6, fan=2
def _parse_dict_literal(s)  # CC=7, fan=6
def _parse_value(v)  # CC=5, fan=5
def _parse_node_line(line)  # CC=6, fan=5
def _parse_edge_line(line)  # CC=8, fan=8
def parse_dsl(text)  # CC=19, fan=16 ⚠
def parse_yaml(text)  # CC=8, fan=12
def dsl_to_yaml(text)  # CC=5, fan=3
class NodeDef:
class EdgeDef:
class RuleDef:
class ModelDef:
class ParseError:
```

### `cyberdsl.dashboard` (`cyberdsl/dashboard.py`)

```python
def _hex_alpha(hex_color, alpha)  # CC=1, fan=2
def _steps_labels(result)  # CC=2, fan=0
def _obs_datasets(result, mc)  # CC=4, fan=9
def _node_datasets(result)  # CC=4, fan=7
def build_dashboard(result, mc, model)  # CC=6, fan=9
def save_dashboard(result, path, mc, model)  # CC=1, fan=3
```

### `cyberdsl.graph` (`cyberdsl/graph.py`)

```python
def _node_shape(kind, label)  # CC=1, fan=1
def model_to_mermaid(model, direction)  # CC=8, fan=4
def build_graph_viewer(model, yaml_source)  # CC=7, fan=8
def save_mermaid(model, path, direction)  # CC=1, fan=3
def save_graph_viewer(model, path, yaml_source)  # CC=1, fan=3
```

## Call Graph

*76 nodes · 88 edges · 8 modules · CC̄=3.4*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `parse_yaml` *(in cyberdsl.parser)* | 8 | 2 | 42 | **44** |
| `scenario_divorce` *(in examples.family_simulation)* | 11 ⚠ | 0 | 40 | **40** |
| `parse_dsl` *(in cyberdsl.parser)* | 19 ⚠ | 2 | 32 | **34** |
| `handle_simulate_stream` *(in cyberdsl.webapp)* | 6 | 0 | 32 | **32** |
| `streamSimulation` *(in cyberdsl.static.app)* | 16 ⚠ | 0 | 29 | **29** |
| `_obs_datasets` *(in cyberdsl.dashboard)* | 4 | 1 | 19 | **20** |
| `handle_simulate` *(in cyberdsl.webapp)* | 5 | 0 | 19 | **19** |
| `build_graph_viewer` *(in cyberdsl.graph)* | 7 | 1 | 18 | **19** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tom-sapletta-com/cyberdsl
# generated in 0.07s
# nodes: 76 | edges: 88 | modules: 8
# CC̄=3.4

HUBS[20]:
  cyberdsl.parser.parse_yaml
    CC=8  in:2  out:42  total:44
  examples.family_simulation.scenario_divorce
    CC=11  in:0  out:40  total:40
  cyberdsl.parser.parse_dsl
    CC=19  in:2  out:32  total:34
  cyberdsl.webapp.handle_simulate_stream
    CC=6  in:0  out:32  total:32
  cyberdsl.static.app.streamSimulation
    CC=16  in:0  out:29  total:29
  cyberdsl.dashboard._obs_datasets
    CC=4  in:1  out:19  total:20
  cyberdsl.webapp.handle_simulate
    CC=5  in:0  out:19  total:19
  cyberdsl.graph.build_graph_viewer
    CC=7  in:1  out:18  total:19
  cyberdsl.graph.model_to_mermaid
    CC=8  in:6  out:13  total:19
  cyberdsl.dashboard.build_dashboard
    CC=6  in:1  out:18  total:19
  cyberdsl.static.app.initStreamCharts
    CC=2  in:5  out:13  total:18
  cyberdsl.static.app.renderMermaid
    CC=5  in:8  out:8  total:16
  cyberdsl.static.app.totalSteps
    CC=10  in:0  out:16  total:16
  cyberdsl.static.app.decoder
    CC=10  in:0  out:16  total:16
  cyberdsl.static.app.reader
    CC=10  in:0  out:16  total:16
  examples.family_simulation.scenario_crisis
    CC=6  in:0  out:15  total:15
  cyberdsl.webapp._snap_to_json
    CC=6  in:2  out:13  total:15
  cyberdsl.static.app.runSimulation
    CC=6  in:0  out:15  total:15
  cyberdsl.static.app.renderModelInfo
    CC=2  in:7  out:8  total:15
  cyberdsl.parser._parse_dict_literal
    CC=7  in:2  out:12  total:14

MODULES:
  cyberdsl.__main__  [7 funcs]
    _load_model  CC=2  out:6
    cmd_csv  CC=3  out:8
    cmd_dashboard  CC=3  out:8
    cmd_monte  CC=4  out:11
    cmd_serve  CC=1  out:1
    cmd_simulate  CC=2  out:5
    cmd_visualize  CC=3  out:8
  cyberdsl.dashboard  [6 funcs]
    _hex_alpha  CC=1  out:4
    _node_datasets  CC=4  out:12
    _obs_datasets  CC=4  out:19
    _steps_labels  CC=2  out:0
    build_dashboard  CC=6  out:18
    save_dashboard  CC=1  out:3
  cyberdsl.graph  [4 funcs]
    build_graph_viewer  CC=7  out:18
    model_to_mermaid  CC=8  out:13
    save_graph_viewer  CC=1  out:3
    save_mermaid  CC=1  out:3
  cyberdsl.models  [5 funcs]
    parse  CC=1  out:2
    apply_shock  CC=3  out:1
    run  CC=3  out:4
    _safe_clip  CC=1  out:3
    run_monte_carlo  CC=6  out:12
  cyberdsl.parser  [7 funcs]
    _parse_dict_literal  CC=7  out:12
    _parse_node_line  CC=6  out:11
    _parse_value  CC=5  out:7
    _strip_inline_comment  CC=6  out:2
    dsl_to_yaml  CC=5  out:3
    parse_dsl  CC=19  out:32
    parse_yaml  CC=8  out:42
  cyberdsl.static.app  [29 funcs]
    clearError  CC=1  out:1
    clearResults  CC=2  out:3
    data  CC=3  out:2
    decoder  CC=10  out:16
    destroyAllCharts  CC=1  out:3
    ds  CC=1  out:3
    initStreamCharts  CC=2  out:13
    labels  CC=1  out:3
    makeChart  CC=3  out:4
    md  CC=2  out:2
  cyberdsl.webapp  [12 funcs]
    _find_example  CC=3  out:1
    _list_examples  CC=7  out:7
    _parse_model  CC=2  out:3
    _snap_to_json  CC=6  out:13
    create_app  CC=1  out:10
    handle_get_example  CC=3  out:6
    handle_list_examples  CC=1  out:2
    handle_mermaid  CC=3  out:13
    handle_parse  CC=3  out:13
    handle_simulate  CC=5  out:19
  examples.family_simulation  [6 funcs]
    _obs_at  CC=1  out:0
    fresh_sim  CC=1  out:2
    print_comparison  CC=5  out:10
    scenario_crisis  CC=6  out:15
    scenario_divorce  CC=11  out:40
    scenario_stable  CC=4  out:9

EDGES:
  examples.family_simulation.scenario_stable → examples.family_simulation.fresh_sim
  examples.family_simulation.scenario_crisis → examples.family_simulation.fresh_sim
  examples.family_simulation.scenario_divorce → examples.family_simulation.fresh_sim
  examples.family_simulation.print_comparison → examples.family_simulation._obs_at
  cyberdsl.dashboard._obs_datasets → cyberdsl.dashboard._hex_alpha
  cyberdsl.dashboard.build_dashboard → cyberdsl.dashboard._steps_labels
  cyberdsl.dashboard.build_dashboard → cyberdsl.dashboard._obs_datasets
  cyberdsl.dashboard.build_dashboard → cyberdsl.dashboard._node_datasets
  cyberdsl.dashboard.build_dashboard → cyberdsl.graph.model_to_mermaid
  cyberdsl.dashboard.save_dashboard → cyberdsl.dashboard.build_dashboard
  cyberdsl.graph.build_graph_viewer → cyberdsl.graph.model_to_mermaid
  cyberdsl.graph.save_mermaid → cyberdsl.graph.model_to_mermaid
  cyberdsl.graph.save_graph_viewer → cyberdsl.graph.build_graph_viewer
  cyberdsl.__main__._load_model → cyberdsl.parser.parse_yaml
  cyberdsl.__main__.cmd_simulate → cyberdsl.__main__._load_model
  cyberdsl.__main__.cmd_dashboard → cyberdsl.__main__._load_model
  cyberdsl.__main__.cmd_dashboard → cyberdsl.dashboard.save_dashboard
  cyberdsl.__main__.cmd_csv → cyberdsl.__main__._load_model
  cyberdsl.__main__.cmd_monte → cyberdsl.__main__._load_model
  cyberdsl.__main__.cmd_monte → cyberdsl.models.run_monte_carlo
  cyberdsl.__main__.cmd_monte → cyberdsl.dashboard.save_dashboard
  cyberdsl.__main__.cmd_serve → cyberdsl.models.Simulation.run
  cyberdsl.__main__.cmd_visualize → cyberdsl.__main__._load_model
  cyberdsl.__main__.cmd_visualize → cyberdsl.graph.save_mermaid
  cyberdsl.__main__.cmd_visualize → cyberdsl.graph.save_graph_viewer
  cyberdsl.parser._parse_value → cyberdsl.parser._parse_dict_literal
  cyberdsl.parser._parse_node_line → cyberdsl.parser._parse_dict_literal
  cyberdsl.parser.parse_dsl → cyberdsl.parser._strip_inline_comment
  cyberdsl.parser.dsl_to_yaml → cyberdsl.parser.parse_dsl
  cyberdsl.models.ModelCompiler.parse → cyberdsl.parser.parse_dsl
  cyberdsl.models.Simulation.apply_shock → cyberdsl.models._safe_clip
  cyberdsl.webapp._parse_model → cyberdsl.parser.parse_yaml
  cyberdsl.webapp.handle_parse → cyberdsl.webapp._parse_model
  cyberdsl.webapp.handle_simulate → cyberdsl.webapp._parse_model
  cyberdsl.webapp.handle_simulate → cyberdsl.webapp._snap_to_json
  cyberdsl.webapp.handle_simulate_stream → cyberdsl.webapp._parse_model
  cyberdsl.webapp.handle_mermaid → cyberdsl.webapp._parse_model
  cyberdsl.webapp.handle_mermaid → cyberdsl.graph.model_to_mermaid
  cyberdsl.webapp.handle_list_examples → cyberdsl.webapp._list_examples
  cyberdsl.webapp.handle_get_example → cyberdsl.webapp._find_example
  cyberdsl.webapp.run → cyberdsl.webapp.create_app
  cyberdsl.static.app.data → cyberdsl.static.app.showError
  cyberdsl.static.app.data → cyberdsl.static.app.setBadge
  cyberdsl.static.app.name → cyberdsl.static.app.showError
  cyberdsl.static.app.name → cyberdsl.static.app.clearResults
  cyberdsl.static.app.name → cyberdsl.static.app.parseModel
  cyberdsl.static.app.parseModel → cyberdsl.static.app.clearError
  cyberdsl.static.app.parseModel → cyberdsl.static.app.setBadge
  cyberdsl.static.app.parseModel → cyberdsl.static.app.showError
  cyberdsl.static.app.parseModel → cyberdsl.static.app.renderModelInfo
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tom-sapletta-com/cyberdsl
# generated in 0.07s
# nodes: 76 | edges: 88 | modules: 8
# CC̄=3.4

HUBS[20]:
  cyberdsl.parser.parse_yaml
    CC=8  in:2  out:42  total:44
  examples.family_simulation.scenario_divorce
    CC=11  in:0  out:40  total:40
  cyberdsl.parser.parse_dsl
    CC=19  in:2  out:32  total:34
  cyberdsl.webapp.handle_simulate_stream
    CC=6  in:0  out:32  total:32
  cyberdsl.static.app.streamSimulation
    CC=16  in:0  out:29  total:29
  cyberdsl.dashboard._obs_datasets
    CC=4  in:1  out:19  total:20
  cyberdsl.webapp.handle_simulate
    CC=5  in:0  out:19  total:19
  cyberdsl.graph.build_graph_viewer
    CC=7  in:1  out:18  total:19
  cyberdsl.graph.model_to_mermaid
    CC=8  in:6  out:13  total:19
  cyberdsl.dashboard.build_dashboard
    CC=6  in:1  out:18  total:19
  cyberdsl.static.app.initStreamCharts
    CC=2  in:5  out:13  total:18
  cyberdsl.static.app.renderMermaid
    CC=5  in:8  out:8  total:16
  cyberdsl.static.app.totalSteps
    CC=10  in:0  out:16  total:16
  cyberdsl.static.app.decoder
    CC=10  in:0  out:16  total:16
  cyberdsl.static.app.reader
    CC=10  in:0  out:16  total:16
  examples.family_simulation.scenario_crisis
    CC=6  in:0  out:15  total:15
  cyberdsl.webapp._snap_to_json
    CC=6  in:2  out:13  total:15
  cyberdsl.static.app.runSimulation
    CC=6  in:0  out:15  total:15
  cyberdsl.static.app.renderModelInfo
    CC=2  in:7  out:8  total:15
  cyberdsl.parser._parse_dict_literal
    CC=7  in:2  out:12  total:14

MODULES:
  cyberdsl.__main__  [7 funcs]
    _load_model  CC=2  out:6
    cmd_csv  CC=3  out:8
    cmd_dashboard  CC=3  out:8
    cmd_monte  CC=4  out:11
    cmd_serve  CC=1  out:1
    cmd_simulate  CC=2  out:5
    cmd_visualize  CC=3  out:8
  cyberdsl.dashboard  [6 funcs]
    _hex_alpha  CC=1  out:4
    _node_datasets  CC=4  out:12
    _obs_datasets  CC=4  out:19
    _steps_labels  CC=2  out:0
    build_dashboard  CC=6  out:18
    save_dashboard  CC=1  out:3
  cyberdsl.graph  [4 funcs]
    build_graph_viewer  CC=7  out:18
    model_to_mermaid  CC=8  out:13
    save_graph_viewer  CC=1  out:3
    save_mermaid  CC=1  out:3
  cyberdsl.models  [5 funcs]
    parse  CC=1  out:2
    apply_shock  CC=3  out:1
    run  CC=3  out:4
    _safe_clip  CC=1  out:3
    run_monte_carlo  CC=6  out:12
  cyberdsl.parser  [7 funcs]
    _parse_dict_literal  CC=7  out:12
    _parse_node_line  CC=6  out:11
    _parse_value  CC=5  out:7
    _strip_inline_comment  CC=6  out:2
    dsl_to_yaml  CC=5  out:3
    parse_dsl  CC=19  out:32
    parse_yaml  CC=8  out:42
  cyberdsl.static.app  [29 funcs]
    clearError  CC=1  out:1
    clearResults  CC=2  out:3
    data  CC=3  out:2
    decoder  CC=10  out:16
    destroyAllCharts  CC=1  out:3
    ds  CC=1  out:3
    initStreamCharts  CC=2  out:13
    labels  CC=1  out:3
    makeChart  CC=3  out:4
    md  CC=2  out:2
  cyberdsl.webapp  [12 funcs]
    _find_example  CC=3  out:1
    _list_examples  CC=7  out:7
    _parse_model  CC=2  out:3
    _snap_to_json  CC=6  out:13
    create_app  CC=1  out:10
    handle_get_example  CC=3  out:6
    handle_list_examples  CC=1  out:2
    handle_mermaid  CC=3  out:13
    handle_parse  CC=3  out:13
    handle_simulate  CC=5  out:19
  examples.family_simulation  [6 funcs]
    _obs_at  CC=1  out:0
    fresh_sim  CC=1  out:2
    print_comparison  CC=5  out:10
    scenario_crisis  CC=6  out:15
    scenario_divorce  CC=11  out:40
    scenario_stable  CC=4  out:9

EDGES:
  examples.family_simulation.scenario_stable → examples.family_simulation.fresh_sim
  examples.family_simulation.scenario_crisis → examples.family_simulation.fresh_sim
  examples.family_simulation.scenario_divorce → examples.family_simulation.fresh_sim
  examples.family_simulation.print_comparison → examples.family_simulation._obs_at
  cyberdsl.dashboard._obs_datasets → cyberdsl.dashboard._hex_alpha
  cyberdsl.dashboard.build_dashboard → cyberdsl.dashboard._steps_labels
  cyberdsl.dashboard.build_dashboard → cyberdsl.dashboard._obs_datasets
  cyberdsl.dashboard.build_dashboard → cyberdsl.dashboard._node_datasets
  cyberdsl.dashboard.build_dashboard → cyberdsl.graph.model_to_mermaid
  cyberdsl.dashboard.save_dashboard → cyberdsl.dashboard.build_dashboard
  cyberdsl.graph.build_graph_viewer → cyberdsl.graph.model_to_mermaid
  cyberdsl.graph.save_mermaid → cyberdsl.graph.model_to_mermaid
  cyberdsl.graph.save_graph_viewer → cyberdsl.graph.build_graph_viewer
  cyberdsl.__main__._load_model → cyberdsl.parser.parse_yaml
  cyberdsl.__main__.cmd_simulate → cyberdsl.__main__._load_model
  cyberdsl.__main__.cmd_dashboard → cyberdsl.__main__._load_model
  cyberdsl.__main__.cmd_dashboard → cyberdsl.dashboard.save_dashboard
  cyberdsl.__main__.cmd_csv → cyberdsl.__main__._load_model
  cyberdsl.__main__.cmd_monte → cyberdsl.__main__._load_model
  cyberdsl.__main__.cmd_monte → cyberdsl.models.run_monte_carlo
  cyberdsl.__main__.cmd_monte → cyberdsl.dashboard.save_dashboard
  cyberdsl.__main__.cmd_serve → cyberdsl.models.Simulation.run
  cyberdsl.__main__.cmd_visualize → cyberdsl.__main__._load_model
  cyberdsl.__main__.cmd_visualize → cyberdsl.graph.save_mermaid
  cyberdsl.__main__.cmd_visualize → cyberdsl.graph.save_graph_viewer
  cyberdsl.parser._parse_value → cyberdsl.parser._parse_dict_literal
  cyberdsl.parser._parse_node_line → cyberdsl.parser._parse_dict_literal
  cyberdsl.parser.parse_dsl → cyberdsl.parser._strip_inline_comment
  cyberdsl.parser.dsl_to_yaml → cyberdsl.parser.parse_dsl
  cyberdsl.models.ModelCompiler.parse → cyberdsl.parser.parse_dsl
  cyberdsl.models.Simulation.apply_shock → cyberdsl.models._safe_clip
  cyberdsl.webapp._parse_model → cyberdsl.parser.parse_yaml
  cyberdsl.webapp.handle_parse → cyberdsl.webapp._parse_model
  cyberdsl.webapp.handle_simulate → cyberdsl.webapp._parse_model
  cyberdsl.webapp.handle_simulate → cyberdsl.webapp._snap_to_json
  cyberdsl.webapp.handle_simulate_stream → cyberdsl.webapp._parse_model
  cyberdsl.webapp.handle_mermaid → cyberdsl.webapp._parse_model
  cyberdsl.webapp.handle_mermaid → cyberdsl.graph.model_to_mermaid
  cyberdsl.webapp.handle_list_examples → cyberdsl.webapp._list_examples
  cyberdsl.webapp.handle_get_example → cyberdsl.webapp._find_example
  cyberdsl.webapp.run → cyberdsl.webapp.create_app
  cyberdsl.static.app.data → cyberdsl.static.app.showError
  cyberdsl.static.app.data → cyberdsl.static.app.setBadge
  cyberdsl.static.app.name → cyberdsl.static.app.showError
  cyberdsl.static.app.name → cyberdsl.static.app.clearResults
  cyberdsl.static.app.name → cyberdsl.static.app.parseModel
  cyberdsl.static.app.parseModel → cyberdsl.static.app.clearError
  cyberdsl.static.app.parseModel → cyberdsl.static.app.setBadge
  cyberdsl.static.app.parseModel → cyberdsl.static.app.showError
  cyberdsl.static.app.parseModel → cyberdsl.static.app.renderModelInfo
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 27f 4341L | yaml:15,python:9,toml:1,shell:1,javascript:1 | 2026-05-16
# generated in 0.01s
# CC̄=3.4 | critical:2/134 | dups:0 | cycles:0

HEALTH[2]:
  🟡 CC    parse_dsl CC=19 (limit:15)
  🟡 CC    streamSimulation CC=16 (limit:15)

REFACTOR[1]:
  1. split 2 high-CC methods  (CC>15)

PIPELINES[84]:
  [1] Src [scenario_stable]: scenario_stable → fresh_sim
      PURITY: 100% pure
  [2] Src [scenario_crisis]: scenario_crisis → fresh_sim
      PURITY: 100% pure
  [3] Src [scenario_divorce]: scenario_divorce → fresh_sim
      PURITY: 100% pure
  [4] Src [print_report]: print_report → _obs_at
      PURITY: 100% pure
  [5] Src [print_comparison]: print_comparison → _obs_at
      PURITY: 100% pure

LAYERS:
  examples/                       CC̄=5.0    ←in:0  →out:0
  │ family_simulation          281L  0C    7m  CC=11     ←0
  │ 04_family_baseline.yaml     60L  0C    0m  CC=0.0    ←0
  │ 05_family_crisis_therapy.yaml    58L  0C    0m  CC=0.0    ←0
  │ 02_port_crisis.yaml         48L  0C    0m  CC=0.0    ←0
  │ 03_port_recovery.yaml       48L  0C    0m  CC=0.0    ←0
  │ 06_school_polarization.yaml    46L  0C    0m  CC=0.0    ←0
  │ 09_municipal_protest.yaml    45L  0C    0m  CC=0.0    ←0
  │ 07_hospital_overload.yaml    45L  0C    0m  CC=0.0    ←0
  │ 10_disinformation_network.yaml    44L  0C    0m  CC=0.0    ←0
  │ 01_port_baseline.yaml       44L  0C    0m  CC=0.0    ←0
  │ 08_company_restructuring.yaml    39L  0C    0m  CC=0.0    ←0
  │
  cyberdsl/                       CC̄=3.4    ←in:0  →out:0
  │ !! app.js                     509L  0C   57m  CC=16     ←0
  │ dashboard                  381L  0C    6m  CC=6      ←1
  │ models                     359L  4C   22m  CC=9      ←1
  │ !! parser                     321L  5C    8m  CC=19     ←3
  │ webapp                     292L  0C   17m  CC=7      ←0
  │ graph                      245L  0C    5m  CC=8      ←3
  │ __main__                   179L  0C    9m  CC=4      ←0
  │ litellm_adapter            121L  1C    3m  CC=10     ←0
  │ __init__                    51L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ planfile.yaml              383L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                91L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              56L  0C    0m  CC=0.0    ←0
  │ project.sh                  54L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    10L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 6 groups | 10f 2511L | 2026-05-16

SUMMARY:
  files_scanned: 10
  total_lines:   2511
  dup_groups:    6
  dup_fragments: 12
  saved_lines:   166
  scan_ms:       4702

HOTSPOTS[2] (files with most duplication):
  examples/family/family_simulation.py  dup=166L  groups=6  frags=6  (6.6%)
  examples/family_simulation.py  dup=166L  groups=6  frags=6  (6.6%)

DUPLICATES[6] (ranked by impact):
  [f7167363db6c1e77] ! EXAC  scenario_divorce  L=78 N=2 saved=78 sim=1.00
      examples/family/family_simulation.py:91-168  (scenario_divorce)
      examples/family_simulation.py:91-168  (scenario_divorce)
  [111d409543721b52]   EXAC  scenario_crisis  L=29 N=2 saved=29 sim=1.00
      examples/family/family_simulation.py:58-86  (scenario_crisis)
      examples/family_simulation.py:58-86  (scenario_crisis)
  [41ac043f62d4e8bd]   EXAC  print_report  L=22 N=2 saved=22 sim=1.00
      examples/family/family_simulation.py:198-219  (print_report)
      examples/family_simulation.py:198-219  (print_report)
  [dedefcf0902cc5ff]   EXAC  scenario_stable  L=19 N=2 saved=19 sim=1.00
      examples/family/family_simulation.py:35-53  (scenario_stable)
      examples/family_simulation.py:35-53  (scenario_stable)
  [2154c74232c09632]   EXAC  print_comparison  L=15 N=2 saved=15 sim=1.00
      examples/family/family_simulation.py:222-236  (print_comparison)
      examples/family_simulation.py:222-236  (print_comparison)
  [ce31a6b121912e8a]   EXAC  fresh_sim  L=3 N=2 saved=3 sim=1.00
      examples/family/family_simulation.py:28-30  (fresh_sim)
      examples/family_simulation.py:28-30  (fresh_sim)

REFACTOR[6] (ranked by priority):
  [1] ◐ extract_module     → examples/utils/scenario_divorce.py
      WHY: 2 occurrences of 78-line block across 2 files — saves 78 lines
      FILES: examples/family/family_simulation.py, examples/family_simulation.py
  [2] ○ extract_function   → examples/utils/scenario_crisis.py
      WHY: 2 occurrences of 29-line block across 2 files — saves 29 lines
      FILES: examples/family/family_simulation.py, examples/family_simulation.py
  [3] ○ extract_function   → examples/utils/print_report.py
      WHY: 2 occurrences of 22-line block across 2 files — saves 22 lines
      FILES: examples/family/family_simulation.py, examples/family_simulation.py
  [4] ○ extract_function   → examples/utils/scenario_stable.py
      WHY: 2 occurrences of 19-line block across 2 files — saves 19 lines
      FILES: examples/family/family_simulation.py, examples/family_simulation.py
  [5] ○ extract_function   → examples/utils/print_comparison.py
      WHY: 2 occurrences of 15-line block across 2 files — saves 15 lines
      FILES: examples/family/family_simulation.py, examples/family_simulation.py
  [6] ○ extract_function   → examples/utils/fresh_sim.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: examples/family/family_simulation.py, examples/family_simulation.py

QUICK_WINS[4] (low risk, high savings — do first):
  [2] extract_function   saved=29L  → examples/utils/scenario_crisis.py
      FILES: family_simulation.py, family_simulation.py
  [3] extract_function   saved=22L  → examples/utils/print_report.py
      FILES: family_simulation.py, family_simulation.py
  [4] extract_function   saved=19L  → examples/utils/scenario_stable.py
      FILES: family_simulation.py, family_simulation.py
  [5] extract_function   saved=15L  → examples/utils/print_comparison.py
      FILES: family_simulation.py, family_simulation.py

EFFORT_ESTIMATE (total ≈ 6.8h):
  hard   scenario_divorce                    saved=78L  ~234min
  medium scenario_crisis                     saved=29L  ~58min
  medium print_report                        saved=22L  ~44min
  medium scenario_stable                     saved=19L  ~38min
  medium print_comparison                    saved=15L  ~30min
  easy   fresh_sim                           saved=3L  ~6min

METRICS-TARGET:
  dup_groups:  6 → 0
  saved_lines: 166 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 127 func | 8f | 2026-05-16
# generated in 0.00s

NEXT[4] (ranked by impact):
  [1] !! SPLIT           cyberdsl/static/app.js
      WHY: 509L, 0 classes, max CC=16
      EFFORT: ~4h  IMPACT: 8144

  [2] !  SPLIT-FUNC      streamSimulation  CC=16  fan=29
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 464

  [3] !  SPLIT-FUNC      parse_dsl  CC=19  fan=20
      WHY: CC=19 exceeds 15
      EFFORT: ~1h  IMPACT: 380

  [4] !! SPLIT           goal.yaml
      WHY: 511L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting goal.yaml may break 0 import paths
  ⚠ Splitting cyberdsl/static/app.js may break 57 import paths

METRICS-TARGET:
  CC̄:          3.4 → ≤2.4
  max-CC:      19 → ≤9
  god-modules: 2 → 0
  high-CC(≥15): 2 → ≤1
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=3.4 → now CC̄=3.4
```

## Intent

Cybernetic DSL and runtime for social-system simulations
