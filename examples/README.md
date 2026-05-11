# CyberDSL — Przykłady

Przykłady modeli cybernetycznych pogrupowane tematycznie. Każdy katalog zawiera własny `README.md`.

## Struktura

```
examples/
├── port/                              # Społeczność portowa
│   ├── harbor_community.cyberdsl      # Pełny model DSL (6 węzłów, 36 kroków)
│   ├── 01_port_baseline.yaml          # Stan bazowy
│   ├── 02_port_crisis.yaml            # Kryzys gospodarczy
│   └── 03_port_recovery.yaml          # Interwencja i odbudowa
│
├── family/                            # System rodzinny
│   ├── family_model.cyberdsl          # Pełny model DSL (7 węzłów, 48 kroków)
│   ├── family_simulation.py           # 3 scenariusze: stabilny / kryzys / rozwód
│   ├── 04_family_baseline.yaml        # Stan bazowy
│   └── 05_family_crisis_therapy.yaml  # Kryzys + terapia
│
├── institutional/                     # Organizacje i instytucje
│   ├── 06_school_polarization.yaml    # Polaryzacja w szkole
│   ├── 07_hospital_overload.yaml      # Przeciążenie szpitala
│   ├── 08_company_restructuring.yaml  # Restrukturyzacja firmy
│   └── 09_municipal_protest.yaml      # Protest miejski
│
├── crisis/                            # Kryzysy informacyjne
│   └── 10_disinformation_network.yaml # Sieć dezinformacji
│
└── scenarios/                         # Oryginalne pliki (archiwum)
    └── *.yaml
```

## Szybki start

```python
from cyberdsl import parse_yaml, Simulation
import pathlib

model = parse_yaml(pathlib.Path("port/01_port_baseline.yaml").read_text())
result = Simulation(model).run()
print(result.summary())
```

Lub przez CLI:

```bash
python -m cyberdsl simulate examples/port/harbor_community.cyberdsl
python -m cyberdsl dashboard examples/port/harbor_community.cyberdsl -o harbor.html
python -m cyberdsl monte examples/family/family_model.cyberdsl --runs 200
```

## Przegląd scenariuszy

| # | Plik | Węzły | Kroki | Kluczowe obserwable |
|---|---|---|---|---|
| 01 | `port/01_port_baseline.yaml` | 3 | 16 | avg_trust, tension_index |
| 02 | `port/02_port_crisis.yaml` | 3 | 20 | avg_trust, protest_pressure |
| 03 | `port/03_port_recovery.yaml` | 3 | 20 | avg_trust, recovery_index |
| 04 | `family/04_family_baseline.yaml` | 5 | 24 | family_wellbeing, marriage_health |
| 05 | `family/05_family_crisis_therapy.yaml` | 5 | 36 | divorce_risk, children_risk |
| 06 | `institutional/06_school_polarization.yaml` | 4 | 18 | school_tension, governance_stability |
| 07 | `institutional/07_hospital_overload.yaml` | 4 | 20 | overload_index, care_stability |
| 08 | `institutional/08_company_restructuring.yaml` | 3 | 18 | organization_health, restructuring_risk |
| 09 | `institutional/09_municipal_protest.yaml` | 4 | 22 | unrest_index, public_legitimacy |
| 10 | `crisis/10_disinformation_network.yaml` | 4 | 20 | information_integrity, panic_index |

## Sugestie eksperymentów

- **Test stabilności:** uruchom scenariusze bazowe, obserwuj czy system dąży do równowagi
- **Test wrażliwości:** zwiększ `stress` o 0.1 i porównaj trajektorie obserwabli
- **Test interwencji:** podnieś `support`, `therapy_effect`, `counter_campaign` w połowie przebiegu
- **Test graniczny:** ustaw `crisis_event=0.9` i sprawdź czy stany pozostają w `[0,1]`
- **Monte Carlo:** uruchom 200 przebiegów z szumem gaussowskim i porównaj przedziały ufności
