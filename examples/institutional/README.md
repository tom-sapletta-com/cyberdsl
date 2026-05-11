# Institutional — Systemy instytucjonalne

Modele organizacji formalnych: szkoła, szpital, firma, samorząd.

## Pliki

| Plik | Format | Opis |
|---|---|---|
| `06_school_polarization.yaml` | YAML | Polaryzacja w szkole — uczniowie, nauczyciele, dyrekcja, rodzice |
| `07_hospital_overload.yaml` | YAML | Przeciążenie szpitala — personel, zarząd, pacjenci |
| `08_company_restructuring.yaml` | YAML | Restrukturyzacja firmy — morale, produktywność, zarząd |
| `09_municipal_protest.yaml` | YAML | Protest miejski — obywatele, rada, media, policja |

## Obserwable per scenariusz

| Scenariusz | Kluczowe obserwable |
|---|---|
| Szkoła | `school_tension`, `governance_stability` |
| Szpital | `overload_index`, `care_stability` |
| Firma | `organization_health`, `restructuring_risk` |
| Samorząd | `unrest_index`, `public_legitimacy` |

## Uruchomienie

```python
from cyberdsl import parse_yaml, Simulation
import pathlib

for fname in ["06_school_polarization.yaml", "07_hospital_overload.yaml",
              "08_company_restructuring.yaml", "09_municipal_protest.yaml"]:
    model = parse_yaml(pathlib.Path(fname).read_text())
    result = Simulation(model).run()
    print(result.summary())
    print()
```

## Wspólne wzorce

- Instytucja ma zmienne `legitimacy`, `authority`, `responsiveness`
- Grupy nacisku mają `mobilization`, `trust`, `cohesion`
- Sprzężenie: presja oddolna ↑ → responsiveness instytucji ↑ lub legitimacy ↓
