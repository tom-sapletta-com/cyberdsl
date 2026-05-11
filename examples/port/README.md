# Port — Społeczność portowa

Modele cybernetyczne społeczności portowej: rybacy, młodzież, instytucje miejskie.

## Pliki

| Plik | Format | Opis |
|---|---|---|
| `harbor_community.cyberdsl` | DSL | Pełny model 6 węzłów (36 kroków) — robotnicy, kupcy, młodzież, rada, port, media |
| `01_port_baseline.yaml` | YAML | Stan bazowy — niska presja, umiarkowane wsparcie |
| `02_port_crisis.yaml` | YAML | Kryzys gospodarczy, erozja zaufania, eskalacja protestów |
| `03_port_recovery.yaml` | YAML | Interwencja i odbudowa zaufania po kryzysie |

## Obserwable

- `avg_trust` — średnie zaufanie społeczne
- `social_resilience` — odporność systemu społecznego
- `tension_index` — indeks napięcia (stres × nieufność × aktywizm)
- `protest_pressure` — presja protestów (scenariusze kryzysowe)
- `institutional_fragility` — kruchość instytucji

## Uruchomienie

```python
from cyberdsl import parse_yaml, Simulation
import pathlib

model = parse_yaml(pathlib.Path("01_port_baseline.yaml").read_text())
result = Simulation(model).run()
print(result.summary())
```

## Scenariusze porównawcze

Trzy pliki YAML tworzą serię: baseline → kryzys → odbudowa.
Porównuj `avg_trust` i `social_resilience` między scenariuszami.
