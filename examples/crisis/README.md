# Crisis — Kryzysy informacyjne i systemowe

Modele kryzysów przekraczających jedną instytucję: dezinformacja, panika społeczna.

## Pliki

| Plik | Format | Opis |
|---|---|---|
| `10_disinformation_network.yaml` | YAML | Sieć dezinformacji — erozja zaufania do mediów i instytucji |

## Model dezinformacji (10)

**Węzły:** `public`, `media`, `institutions`, `disinformation_actors`

**Mechanizm:**
- `disinformation_actors` wysyłają sygnały obniżające `media.credibility`
- Niska wiarygodność mediów → rośnie `public.panic` i spada `public.trust`
- Instytucje tracą `legitimacy` gdy public trust spada
- `counter_campaign` (global) hamuje dezinformację

**Obserwable:**
- `information_integrity` — spójność ekosystemu informacyjnego
- `panic_index` — poziom paniki społecznej

## Uruchomienie

```python
from cyberdsl import parse_yaml, Simulation
import pathlib

model = parse_yaml(pathlib.Path("10_disinformation_network.yaml").read_text())
result = Simulation(model).run()
print(result.summary())
ot = result.observables_over_time()
# ot['information_integrity'] → trajektoria w czasie
```

## Eksperymenty

- Zwiększ `counter_campaign` do 0.6 — obserwuj hamowanie paniki
- Zwiększ `disinformation_strength` do 0.9 — obserwuj kolaps `information_integrity`
- Zmień `delay` w krawędzi `disinformation_actors → media` — efekt opóźnienia propagacji
