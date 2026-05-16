# CyberDSL

Cybernetic DSL and runtime for social-system simulations

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `cyberdsl`
- **version**: `0.2.1`
- **python_requires**: `>=3.10`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(6 mod), project/(2 analysis files)

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

## Interfaces

### CLI Entry Points

- `cyberdsl`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m cyberdsl
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m cyberdsl --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m cyberdsl --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m cyberdsl --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# NOTE: Python pytest files were detected but no convertible HTTP calls or assertions were found.
# To run pytest tests directly, use: pytest <test_file>
```

## Configuration

```yaml
project:
  name: cyberdsl
  version: 0.2.1
  env: local
```

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

## Deployment

```bash markpact:run
pip install cyberdsl

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`cyberdsl`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `cyberdsl/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# cyberdsl | 15f 3930L | python:11,less:1,css:1,javascript:1,shell:1 | 2026-05-16
# stats: 107 func | 10 cls | 15 mod | CC̄=3.9 | critical:3 | cycles:0
# alerts[5]: CC parse_dsl=19; CC scenario_divorce=11; CC model_to_mermaid=8; CC _parse_edge_line=8; fan-out handle_simulate_stream=20
# hotspots[5]: handle_simulate_stream fan=20; parse_dsl fan=16; handle_simulate fan=14; run_monte_carlo fan=12; parse_yaml fan=12
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[15]:
  app.doql.less,29
  cyberdsl/__init__.py,52
  cyberdsl/__main__.py,180
  cyberdsl/dashboard.py,382
  cyberdsl/graph.py,246
  cyberdsl/litellm_adapter.py,122
  cyberdsl/models.py,360
  cyberdsl/parser.py,322
  cyberdsl/static/app.css,316
  cyberdsl/static/app.js,510
  cyberdsl/webapp.py,293
  examples/family/family_simulation.py,282
  examples/family_simulation.py,282
  project.sh,54
  tests/test_cyberdsl.py,500
D:
  cyberdsl/__init__.py:
  cyberdsl/__main__.py:
    e: _load_model,cmd_simulate,cmd_dashboard,cmd_csv,cmd_monte,cmd_serve,cmd_visualize,cmd_translate,main
    _load_model(path)
    cmd_simulate(args)
    cmd_dashboard(args)
    cmd_csv(args)
    cmd_monte(args)
    cmd_serve(args)
    cmd_visualize(args)
    cmd_translate(args)
    main()
  cyberdsl/dashboard.py:
    e: _hex_alpha,_steps_labels,_obs_datasets,_node_datasets,build_dashboard,save_dashboard
    _hex_alpha(hex_color;alpha)
    _steps_labels(result)
    _obs_datasets(result;mc)
    _node_datasets(result)
    build_dashboard(result;mc;model)
    save_dashboard(result;path;mc;model)
  cyberdsl/graph.py:
    e: _node_shape,model_to_mermaid,build_graph_viewer,save_mermaid,save_graph_viewer
    _node_shape(kind;label)
    model_to_mermaid(model;direction)
    build_graph_viewer(model;yaml_source)
    save_mermaid(model;path;direction)
    save_graph_viewer(model;path;yaml_source)
  cyberdsl/litellm_adapter.py:
    e: CommunityDSLTranslator
    CommunityDSLTranslator: __init__(4),translate(3),translate_and_compile(1)
  cyberdsl/models.py:
    e: _safe_clip,run_monte_carlo,ModelCompiler,SimulationResult,Simulation,MonteCarloResult
    ModelCompiler: parse(1),_validate(1)
    SimulationResult: observables_over_time(0),node_state_over_time(2),summary(0),to_csv(0),save_csv(1)
    Simulation: __init__(1),_build_signals(2),_push_signals(0),_eval_rules(1),_eval_observables(0),step(1),run(1),apply_shock(3),set_global(2),run_scenario(3)
    MonteCarloResult: mean_observable(1),std_observable(1),percentile_observable(2)
    _safe_clip(x;lo;hi)
    run_monte_carlo(model;n_runs;steps;noise_std;seed)
  cyberdsl/parser.py:
    e: _strip_inline_comment,_parse_dict_literal,_parse_value,_parse_node_line,_parse_edge_line,parse_dsl,parse_yaml,dsl_to_yaml,NodeDef,EdgeDef,RuleDef,ModelDef,ParseError
    NodeDef:
    EdgeDef:
    RuleDef:
    ModelDef:
    ParseError:
    _strip_inline_comment(line)
    _parse_dict_literal(s)
    _parse_value(v)
    _parse_node_line(line)
    _parse_edge_line(line)
    parse_dsl(text)
    parse_yaml(text)
    dsl_to_yaml(text)
  cyberdsl/webapp.py:
    e: _parse_model,_model_meta,_snap_to_json,_find_example,_list_examples,handle_favicon,handle_index,handle_static,handle_parse,handle_simulate,handle_simulate_stream,handle_mermaid,handle_list_examples,handle_get_example,access_log_middleware,create_app,run
    _parse_model(text;fmt)
    _model_meta(model)
    _snap_to_json(snap)
    _find_example(name)
    _list_examples()
    handle_favicon(request)
    handle_index(request)
    handle_static(request)
    handle_parse(request)
    handle_simulate(request)
    handle_simulate_stream(request)
    handle_mermaid(request)
    handle_list_examples(request)
    handle_get_example(request)
    access_log_middleware(request;handler)
    create_app()
    run(host;port)
  examples/family/family_simulation.py:
    e: fresh_sim,scenario_stable,scenario_crisis,scenario_divorce,_obs_at,print_report,print_comparison
    fresh_sim()
    scenario_stable()
    scenario_crisis()
    scenario_divorce()
    _obs_at(timeline;step)
    print_report(result)
    print_comparison(results)
  examples/family_simulation.py:
    e: fresh_sim,scenario_stable,scenario_crisis,scenario_divorce,_obs_at,print_report,print_comparison
    fresh_sim()
    scenario_stable()
    scenario_crisis()
    scenario_divorce()
    _obs_at(timeline;step)
    print_report(result)
    print_comparison(results)
  tests/test_cyberdsl.py:
    e: test_parse_model_meta,test_parse_globals,test_parse_nodes,test_parse_edges,test_parse_rules,test_parse_observables,test_simulation_runs,test_simulation_observables,test_simulation_clip_bounds,test_shock_api,test_observables_over_time,test_example_file,test_parse_yaml_meta,test_parse_yaml_globals,test_parse_yaml_nodes,test_parse_yaml_edges,test_parse_yaml_rules,test_parse_yaml_observables,test_yaml_simulation_runs,test_dsl_to_yaml_roundtrip,test_dsl_to_yaml_is_valid_yaml,test_csv_export_columns,test_csv_export_step_values,test_save_csv,test_build_dashboard_returns_html,test_save_dashboard,test_dashboard_with_mc,test_monte_carlo_run_count,test_monte_carlo_mean_length,test_monte_carlo_bounds,test_monte_carlo_percentiles,test_monte_carlo_reproducible,test_run_scenario_shock,test_run_scenario_global_change,test_harbor_community_example,test_harbor_community_clip_bounds,test_model_to_mermaid_contains_nodes,test_model_to_mermaid_contains_edges,test_model_to_mermaid_contains_globals,test_model_to_mermaid_directions,test_build_graph_viewer_returns_html,test_build_graph_viewer_contains_node_info,test_save_mermaid,test_save_graph_viewer,test_dashboard_graph_tab,test_mermaid_yaml_model
    test_parse_model_meta()
    test_parse_globals()
    test_parse_nodes()
    test_parse_edges()
    test_parse_rules()
    test_parse_observables()
    test_simulation_runs()
    test_simulation_observables()
    test_simulation_clip_bounds()
    test_shock_api()
    test_observables_over_time()
    test_example_file()
    test_parse_yaml_meta()
    test_parse_yaml_globals()
    test_parse_yaml_nodes()
    test_parse_yaml_edges()
    test_parse_yaml_rules()
    test_parse_yaml_observables()
    test_yaml_simulation_runs()
    test_dsl_to_yaml_roundtrip()
    test_dsl_to_yaml_is_valid_yaml()
    test_csv_export_columns()
    test_csv_export_step_values()
    test_save_csv(tmp_path)
    test_build_dashboard_returns_html()
    test_save_dashboard(tmp_path)
    test_dashboard_with_mc(tmp_path)
    test_monte_carlo_run_count()
    test_monte_carlo_mean_length()
    test_monte_carlo_bounds()
    test_monte_carlo_percentiles()
    test_monte_carlo_reproducible()
    test_run_scenario_shock()
    test_run_scenario_global_change()
    test_harbor_community_example()
    test_harbor_community_clip_bounds()
    test_model_to_mermaid_contains_nodes()
    test_model_to_mermaid_contains_edges()
    test_model_to_mermaid_contains_globals()
    test_model_to_mermaid_directions()
    test_build_graph_viewer_returns_html()
    test_build_graph_viewer_contains_node_info()
    test_save_mermaid(tmp_path)
    test_save_graph_viewer(tmp_path)
    test_dashboard_graph_tab(tmp_path)
    test_mermaid_yaml_model(tmp_path)
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

## Intent

Cybernetic DSL and runtime for social-system simulations
