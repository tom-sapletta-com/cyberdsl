# CyberDSL


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.2.1-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.15-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-2.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.1500 (1 commits)
- 👤 **Human dev:** ~$200 (2.0h @ $100/h, 30min dedup)

Generated on 2026-05-11 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

CyberDSL to biblioteka Python i mini-język dziedzinowy (DSL) do **modelowania układów cybernetycznych**: społeczności, grup, instytucji i relacji wpływu między nimi — wraz z symulacją krokową w czasie.

## Instalacja

```bash
pip install -e .
# z opcjonalną wizualizacją:
pip install -e ".[viz]"
```

## Składnia DSL

```txt
model:
  name = "Miasto-A"
  steps = 12

globals:
  stress = 0.35
  support = 0.55

nodes:
  youth:group      | state={cohesion:0.45, trust:0.40} | adaptability=0.70
  elders:group     | state={cohesion:0.60, trust:0.65} | adaptability=0.30
  council:institution | state={cohesion:0.75, trust:0.50} | legitimacy=0.80

edges:
  council->youth:influence  | weight=0.30 | delay=1
  youth->council:feedback   | weight=0.25 | delay=0
  elders->youth:stabilize   | weight=0.20 | delay=1

rules:
  youth.cohesion => clip(self['cohesion'] + 0.15*sum_influence - 0.10*globals['stress'])
  youth.trust    => clip(self['trust'] + 0.10*signals['w_council']*signals['sig_council'].get('cohesion',0))
  council.trust  => clip(self['trust'] + 0.12*signals['w_youth']*signals['sig_youth'].get('trust',0))

observables:
  total_trust = (nodes['youth']['trust'] + nodes['elders']['trust'] + nodes['council']['trust']) / 3
```

### Sekcje DSL

| Sekcja | Znaczenie |
|---|---|
| `model:` | Metadane: nazwa i liczba kroków |
| `globals:` | Parametry globalne (np. stress, support) |
| `nodes:` | Aktorzy, grupy, instytucje — ze stanami i parametrami |
| `edges:` | Kanały wpływu i sprzężenia zwrotnego z wagami i opóźnieniami |
| `rules:` | Równania aktualizacji stanu per węzeł per krok |
| `observables:` | Wskaźniki liczone na osi czasu |

### Zmienne dostępne w regułach

| Zmienna | Opis |
|---|---|
| `self` | Aktualny stan węzła `{var: float}` |
| `params` | Parametry węzła |
| `globals` | Parametry globalne |
| `signals` | Sygnały wejściowe: `sig_<src>`, `w_<src>` |
| `sum_influence` | Ważona suma sygnałów wejściowych |
| `clip(x)` | Obcięcie do zakresu `[0, 1]` |
| `math` | Moduł `math` Pythona |
| `nodes` | Pełny słownik stanów wszystkich węzłów |

## Użycie — kod DSL

```python
from cyberdsl import ModelCompiler, Simulation

dsl = open('example.cyberdsl', encoding='utf-8').read()
model = ModelCompiler().parse(dsl)
sim = Simulation(model)
result = sim.run(steps=24)

print(result.summary())
print(result.observables_over_time())
```

## Użycie — translacja opisu naturalnego (LiteLLM)

```python
from cyberdsl import CommunityDSLTranslator, ModelCompiler, Simulation

description = """
Społeczność portowa ma trzy grupy: rybaków, młodzież i urząd miasta.
Rośnie stres ekonomiczny, ale działa lokalny program wsparcia.
Młodzież szybko reaguje na narrację urzędu, rybacy stabilizują normy społeczne.
"""

translator = CommunityDSLTranslator(model='openai/gpt-4o-mini', api_key='YOUR_KEY')
dsl = translator.translate(description)
model = ModelCompiler().parse(dsl)
result = Simulation(model).run(steps=16)
print(result.summary())
```

## Interwencje i szoki

```python
sim = Simulation(model)
sim.run(steps=4)

# Zewnętrzny szok — obniża zaufanie rybaków
sim.apply_shock('fishers', 'trust', -0.20)

# Zmiana parametru globalnego w połowie symulacji
sim.set_global('stress', 0.70)

result = sim.run(steps=8)  # kontynuacja
```

## API runtime

### `ModelCompiler`
- `parse(dsl: str) -> ModelDef` — parsuje i waliduje DSL.

### `Simulation(model)`
- `run(steps=None) -> SimulationResult` — uruchamia pełną symulację.
- `step(step_no) -> dict` — jeden krok ręcznie.
- `apply_shock(node_id, var, delta)` — interwencja zewnętrzna.
- `set_global(key, value)` — zmiana parametru globalnego.

### `SimulationResult`
- `timeline` — lista snapshotów `{step, nodes, observables, globals}`.
- `summary() -> str` — raport tekstowy.
- `observables_over_time() -> dict[str, list[float]]` — serie czasowe.
- `node_state_over_time(node_id, var) -> list[float]` — seria jednej zmiennej.

## Architektura

```
cyberdsl/
├── parser.py          # Leksykalny parser DSL → ModelDef
├── models.py          # ModelCompiler + Simulation runtime
├── litellm_adapter.py # Translacja NL → DSL przez LLM
└── __init__.py        # Public API

example.cyberdsl       # Przykładowy model społeczności portowej
tests/
└── test_cyberdsl.py   # 12 testów jednostkowych
```

## Ograniczenia (v0.1)

- Parser liniowy, bez pełnego AST.
- Reguły ewaluowane przez `eval()` — model DSL powinien pochodzić z zaufanego źródła.
- Brak stochastyki, zdarzeń dyskretnych, kalibracji empirycznej.
- Brak eksportu do CSV / wykresów (planowane w v0.2).

## Kierunki rozwoju

- Walidator i AST / bezpieczny interpreter wyrażeń.
- Sekcja `events:` — zdarzenia, scenariusze, szoki zewnętrzne.
- Eksport timeline do CSV i wykresów matplotlib.
- Kalibracja parametrów na danych empirycznych.
- Wieloagentowe rozszerzenia i symulacje Monte Carlo.


## License

Licensed under Apache-2.0.
