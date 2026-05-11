# Family — System rodzinny

Modele cybernetyczne systemu rodzinnego: rodzice, małżeństwo jako subsystem, dzieci.

## Pliki

| Plik | Format | Opis |
|---|---|---|
| `family_model.cyberdsl` | DSL | Pełny model rodziny Kowalskich (48 kroków = 4 lata) |
| `04_family_baseline.yaml` | YAML | Stan bazowy — stabilne małżeństwo, niski stres |
| `05_family_crisis_therapy.yaml` | YAML | Kryzys małżeński + wejście terapii w połowie |
| `family_simulation.py` | Python | Skrypt uruchamiający 3 scenariusze (A: stabilny, B: kryzys, C: rozwód) |

## Węzły modelu

- `mother`, `father` — rodzice (wellbeing, attachment, stress)
- `marriage` — małżeństwo jako subsystem (cohesion, conflict, intimacy, commitment)
- `child_elder`, `child_younger` — dzieci (wellbeing, security, anxiety)
- `work_system`, `extended_family` — systemy zewnętrzne

## Obserwable

- `family_wellbeing` — ogólny dobrostan rodziny
- `marriage_health` — zdrowie związku małżeńskiego
- `divorce_risk` — ryzyko rozpadu
- `children_security_avg` — poczucie bezpieczeństwa dzieci
- `system_resilience` — odporność całego systemu

## Uruchomienie pełnej symulacji

```bash
python examples/family/family_simulation.py
```

## Mechanizmy cybernetyczne

- **Opóźnienia (delay=1–2):** skutki konfliktów docierają do dzieci z opóźnieniem
- **Homeostaza (clip):** stany stabilizują się w [0,1]
- **Szok zewnętrzny:** `sim.apply_shock('marriage', 'conflict', +0.20)`
- **Interwencja:** `sim.set_global('therapy_effect', 0.30)`
