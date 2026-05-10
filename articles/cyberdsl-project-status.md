---
title: "CyberDSL – Status projektu: DSL i runtime do symulacji układów cybernetycznych"
date: 2026-05-10
tags: [cybernetics, dsl, python, simulation, litellm, open-source]
status: publish
category: Projects
excerpt: "CyberDSL to biblioteka Python i mini-język dziedzinowy (DSL) umożliwiający modelowanie i symulację społeczności, grup i instytucji jako układów cybernetycznych ze sprzężeniami zwrotnymi i dynamiką w czasie."
---

# CyberDSL – Status projektu

**Wersja:** 0.1.0  
**Repozytorium:** `cyberdsl`  
**Język:** Python 3.10+  
**Zależności:** `litellm>=1.0.0`  
**Stan:** ✅ Aktywny, wersja szkicowa

---

## Czym jest CyberDSL?

CyberDSL to biblioteka Python i mini-język dziedzinowy (DSL) inspirowany cybernetyką Norberta Wienera — nauką o sterowaniu, komunikacji i sprzężeniu zwrotnym w systemach złożonych. Projekt umożliwia:

- **modelowanie** społeczności, grup społecznych, instytucji i subsystemów jako grafów węzłów i krawędzi,
- **definiowanie** stanów, parametrów, reguł aktualizacji i obserwabli w czytelnym języku tekstowym,
- **tłumaczenie** swobodnego opisu słownego na kod DSL za pomocą dowolnego modelu językowego przez LiteLLM,
- **uruchamianie** symulacji krokowej z obsługą opóźnień, sprzężeń zwrotnych i interwencji zewnętrznych.

---

## Architektura

Projekt składa się z czterech głównych modułów:

### `parser.py` — leksykalny parser DSL

Parsuje tekst w formacie CyberDSL do struktury `ModelDef`. Obsługuje sześć sekcji:

| Sekcja | Rola |
|--------|------|
| `model:` | Metadane (nazwa, kroki) |
| `globals:` | Parametry globalne systemu |
| `nodes:` | Węzły — grupy, instytucje, subsystemy |
| `edges:` | Kanały wpływu z wagami i opóźnieniami |
| `rules:` | Równania aktualizacji stanu |
| `observables:` | Wskaźniki liczone w każdym kroku |

### `models.py` — runtime symulacji

Silnik `Simulation` realizuje symulację krokową:

1. Snapshot sygnałów wejściowych do buforów opóźnień.
2. Budowanie środowiska ewaluacji reguł (`self`, `globals`, `signals`, `clip`, `math`).
3. Atomowa aktualizacja stanów węzłów.
4. Obliczenie obserwabli.
5. Zapis snapshotu do `timeline`.

Dostępne są też metody interwencji: `apply_shock()` i `set_global()`, umożliwiające symulację szoków zewnętrznych lub zmian polityki w połowie biegu.

### `litellm_adapter.py` — translacja NL → DSL

Klasa `CommunityDSLTranslator` używa LiteLLM do tłumaczenia swobodnego opisu społeczności na poprawny kod DSL. Obsługuje few-shot examples, schema hints i automatyczne usuwanie markdown z odpowiedzi modelu.

### `__init__.py` — publiczne API

Eksportuje: `ModelCompiler`, `Simulation`, `SimulationResult`, `parse_dsl`, `CommunityDSLTranslator`.

---

## Przykład użycia

Poniższy DSL modeluje społeczność portową z trzema aktorami:

```txt
model:
  name = "Społeczność-portowa"
  steps = 16

globals:
  stress = 0.40
  support = 0.50

nodes:
  fishers:group    | state={cohesion:0.65, trust:0.55, activism:0.30}
  youth:group      | state={cohesion:0.45, trust:0.40, activism:0.60}
  city_hall:institution | state={cohesion:0.80, trust:0.50, legitimacy:0.70}

edges:
  city_hall->youth:influence  | weight=0.35 | delay=1
  fishers->youth:stabilize    | weight=0.25 | delay=1
  youth->city_hall:feedback   | weight=0.30 | delay=0

observables:
  avg_trust = (nodes['fishers']['trust'] + nodes['youth']['trust'] + nodes['city_hall']['trust']) / 3
  tension_index = globals['stress'] * (1 - nodes['fishers']['trust']) * nodes['youth']['activism']
```

Uruchomienie:

```python
from cyberdsl import ModelCompiler, Simulation

model = ModelCompiler().parse(open('example.cyberdsl').read())
result = Simulation(model).run()
print(result.summary())
```

---

## Stan testów

Projekt posiada 12 testów jednostkowych pokrywających:

- parsowanie sekcji `model:`, `globals:`, `nodes:`, `edges:`, `rules:`, `observables:`,
- poprawność symulacji (liczba kroków, wartości w `[0,1]`),
- API interwencji (`apply_shock`),
- serie czasowe obserwabli,
- działanie na pliku `example.cyberdsl`.

**Wynik: 12/12 ✅ — 0.07s**

---

## Ograniczenia wersji 0.1

- Parser liniowy — brak pełnego AST i walidatora składni.
- Reguły ewaluowane przez `eval()` — DSL powinien pochodzić z zaufanego źródła.
- Brak stochastyki, zdarzeń dyskretnych, kalibracji empirycznej.
- Brak eksportu timeline do CSV i wykresów.

---

## Roadmapa — v0.2

- [ ] Walidator i AST / bezpieczny interpreter wyrażeń zamiast `eval`.
- [ ] Sekcja `events:` — szoki zewnętrzne, scenariusze, interwencje.
- [ ] Eksport do CSV i wykresy matplotlib / plotly.
- [ ] Kalibracja parametrów na danych empirycznych.
- [ ] Wieloagentowe rozszerzenia i symulacje Monte Carlo.
- [ ] Pełna dokumentacja API (Sphinx).

---

## Powiązania z cybernetyką Wienera

Projekt realizuje kluczowe postulaty cybernetyki:

| Pojęcie Wienera | Realizacja w CyberDSL |
|---|---|
| Sprzężenie zwrotne | Krawędzie `feedback` z `delay` |
| Sterownik / regulator | Reguły aktualizacji stanu |
| Kanał informacyjny | Krawędzie z wagami |
| Homeostaza | `clip()` trzymające zmienne w `[0,1]` |
| Entropia / zaburzenie | Parametry `stress`, `external_shock` |
| Obserwator | Sekcja `observables:` |

---

*Projekt jest na wczesnym etapie. Wkład, zgłoszenia błędów i propozycje rozszerzeń są mile widziane.*
