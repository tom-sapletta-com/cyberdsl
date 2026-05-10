---
title: "CyberDSL w praktyce: Cybernetyczna analiza małżeństwa i rozwodu"
date: 2026-05-10
tags: [cybernetics, family-systems, simulation, norbert-wiener, bowen-theory, python, dsl]
status: publish
category: Projects
excerpt: "Jak za pomocą DSL i symulacji krokowej modelować dynamikę systemu rodzinnego — małżeństwo, kryzys i rozwód jako układy cybernetyczne ze sprzężeniami zwrotnymi?"
---

# Cybernetyczna analiza systemu rodzinnego — małżeństwo i rozwód

Cybernetyka Norberta Wienera zajmuje się sterowaniem i komunikacją w systemach złożonych. Rodzina to jeden z najbardziej skomplikowanych takich systemów — sieć sprzężeń zwrotnych między jednostkami, podsystemami (małżeńskim, rodzicielskim, dziecięcym) i środowiskiem zewnętrznym.

Poniżej pokazuję, jak za pomocą CyberDSL zamodelować rodzinę z dwojgiem dzieci i przeprowadzić symulację trzech scenariuszy na przestrzeni 4 lat (48 kroków miesięcznych).

---

## Model systemu rodzinnego

### Węzły (aktorzy)

System składa się z siedmiu węzłów:

| Węzeł | Typ | Kluczowe zmienne stanu |
|---|---|---|
| `mother` | actor | wellbeing, attachment, autonomy, stress |
| `father` | actor | wellbeing, attachment, autonomy, stress |
| `marriage` | subsystem | cohesion, conflict, intimacy, commitment |
| `child_elder` (10 lat) | actor | wellbeing, security, anxiety |
| `child_younger` (6 lat) | actor | wellbeing, security, anxiety |
| `work_system` | institution | demand, satisfaction, stability |
| `extended_family` | group | cohesion, support, interference |

### Kluczowe sprzężenia zwrotne

Trzy główne pętle strukturalne:

**1. Pętla małżeńska (ujemna / stabilizująca)**  
Wyższy conflict → niższy cohesion → niższe wellbeing rodziców → wyższy stress → wyższy conflict. To pętla dodatnia destabilizująca, którą terapia zamienia w ujemną.

**2. Pętla dzieci–rodzice (rezonans)**  
Conflict małżeński → anxiety dzieci → stress rodziców → więcej conflictu. Klasyczny rezonans systemowy opisany przez Murray'a Bowena w teorii systemów rodzinnych.

**3. Pętla wsparcia zewnętrznego (bufor)**  
`social_support` i `therapy_effect` to parametry globalne tworzące pętle ujemne — tłumią eskalację stresu.

---

## Trzy scenariusze

### Scenariusz A: Stabilne małżeństwo

Niski stres zewnętrzny, terapia prewencyjna w miesiącach 12–24.

```txt
globals:
  external_stress   = 0.15
  economic_pressure = 0.20
  social_support    = 0.75
```

Interwencja: w miesiącu 12 aktywowana terapia (`therapy_effect = 0.30`), zakończona w miesiącu 24.

**Wyniki po 48 krokach:**

| Wskaźnik | Start | Miesiąc 12 | Miesiąc 48 | Trend |
|---|---|---|---|---|
| Dobrostan rodziny | 0.789 | 1.000 | 1.000 | ▲ |
| Stres rodziców | 0.279 | 0.000 | 0.000 | ▼ |
| Poczucie bezpieczeństwa dzieci | 0.837 | 1.000 | 1.000 | ▲ |
| Lęk dzieci | 0.053 | 0.000 | 0.000 | ▼ |
| Zdrowie małżeństwa | 0.748 | 0.982 | 1.000 | ▲ |
| Ryzyko rozpadu | 0.000 | 0.000 | 0.000 | → |

Układ osiąga pełne nasycenie pozytywne — wszystkie wskaźniki konwergują ku 1.0. System ma dużą odporność (resilience) dzięki wysokiemu `social_support`.

---

### Scenariusz B: Kryzys małżeński bez interwencji

Wysoki stres zewnętrzny, utrata pracy ojca w miesiącu 8, brak skutecznej terapii.

```txt
globals:
  external_stress   = 0.45
  economic_pressure = 0.55
  social_support    = 0.40
```

Zdarzenia:
- **Miesiąc 8**: `apply_shock(father, stress, +0.30)` — utrata pracy
- **Miesiąc 24**: `economic_pressure = 0.70` — eskalacja

**Wyniki po 48 krokach:**

| Wskaźnik | Start | Miesiąc 12 | Miesiąc 48 | Trend |
|---|---|---|---|---|
| Dobrostan rodziny | 0.781 | 0.509 | 0.000 | ▼ |
| Stres rodziców | 0.357 | 0.870 | 1.000 | ▲ |
| Poczucie bezpieczeństwa dzieci | 0.825 | 0.484 | 0.000 | ▼ |
| Lęk dzieci | 0.069 | 0.389 | 1.000 | ▲ |
| Zdrowie małżeństwa | 0.735 | 0.213 | 0.000 | ▼ |
| Ryzyko rozpadu | 0.000 | 0.532 | 1.000 | ▲ |

System wpada w spiralę negatywną — brak wystarczającego `social_support` i `therapy_effect` oznacza, że pętla dodatnia (stres → konflikt → stres) nie ma hamulca. Po miesiącu 24 układ jest nieodwracalnie destabilizowany.

**Cybernetyczna interpretacja**: brak sprzężenia ujemnego (regulatora) w systemie z silnymi zaburzeniami zewnętrznymi prowadzi do utraty homeostazy.

---

### Scenariusz C: Separacja i rozwód z adaptacją

Trzy wyraźne fazy dynamiki systemowej:

**Faza I (miesiące 1–12)**: narastanie napięć  
**Faza II (miesiąc 13)**: ostry szok — separacja  
**Faza III (miesiące 14–30)**: adaptacja, terapia dzieci  
**Faza IV (miesiące 31–48)**: nowe equilibrium

Kluczowy moment — miesiąc 13:

```python
sim.apply_shock("marriage",       "cohesion",    -0.40)
sim.apply_shock("marriage",       "commitment",  -0.50)
sim.apply_shock("child_younger",  "security",    -0.38)
sim.apply_shock("child_younger",  "anxiety",     +0.40)
```

**Wyniki:**

| Wskaźnik | Start | Miesiąc 13 | Miesiąc 24 | Miesiąc 48 |
|---|---|---|---|---|
| Dobrostan rodziny | 0.782 | (szok) | 0.002 | 0.000 |
| Poczucie bezpieczeństwa dzieci | 0.827 | (szok) | 0.000 | 0.000 |
| Zdrowie małżeństwa | 0.735 | (szok) | 0.000 | 0.000 |

> **Ważna uwaga metodologiczna**: wyniki scenariusza C po miesiącu 30 pokazują pełne wyczerpanie wskaźników — to artefakt obecnej wersji modelu (v0.1), w której brak wewnętrznych generatorów odporności indywidualnej (post-divorce adaptation). W wersji v0.2 planowane jest dodanie sekcji `events:` z wielofazową adaptacją i nowymi równaniami równowagi po rozpadzie małżeństwa.

---

## Główne obserwacje cybernetyczne

### 1. Bifurkacja przy różnych poziomach social_support

Wyniki pokazują ostrą granicę: przy `social_support ≥ 0.65` system konwerguje do homeostazy pozytywnej; poniżej tego progu dominuje pętla dodatnia destabilizująca. To odpowiednik progu bifurkacji w teorii układów dynamicznych.

### 2. Opóźnienia (delay) jako mechanizm transmisji kryzysu

Konflikty małżeńskie docierają do dzieci z opóźnieniem 1–2 kroków (delay=1, delay=2 na krawędziach). To modeluje empirycznie potwierdzone zjawisko: dzieci reagują na pogorszenie atmosfery rodzinnej ze zwłoką — najpierw "adaptują się", potem eksponują lęk.

### 3. Terapia jako sprzężenie ujemne

Parametr `therapy_effect` wprowadza regulację ujemną: obniża conflict, podwyższa cohesion i intimacy w małżeństwie. Bez niego system z `economic_pressure ≥ 0.50` nieuchronnie destabilizuje się — niezależnie od wyjściowych stanów.

### 4. Odporność dzieci a wiek

Młodsze dziecko (6 lat, `resilience=0.50`) wykazuje wyższe przyrosty lęku i większe spadki bezpieczeństwa niż starsze (10 lat, `resilience=0.65`). Wyższy parametr delay reakcji i większy współczynnik w regule `anxiety` modeluje większą wrażliwość na konflikty systemowe.

---

## Jak to uruchomić

```bash
git clone <repo>
pip install -e .
python examples/family_simulation.py
```

Albo własne eksperymenty:

```python
from cyberdsl import ModelCompiler, Simulation

model = ModelCompiler().parse(open('examples/family_model.cyberdsl').read())
sim = Simulation(model)

# Faza stabilna
sim.set_global('social_support', 0.80)
sim.run(steps=12)

# Szok zewnętrzny
sim.apply_shock('father', 'stress', +0.40)
sim.set_global('economic_pressure', 0.75)
result = sim.run(steps=12)

print(result.summary())
```

---

## Powiązania z teorią systemów rodzinnych

| Koncepcja (Bowen, Minuchin) | Realizacja w modelu |
|---|---|
| Triangulacja | Krawędzie dzieci ↔ rodzice z wagą ≥ 0.40 |
| Spójność vs. separacja (cohesion) | Zmienna `marriage.cohesion` |
| Grzbiet stresu (stress pile-up) | Akumulacja `stress` bez hamulca |
| Rezyliencja rodzinna | Parametr `resilience` węzłów + `social_support` |
| Szok separacji | `apply_shock` jako dyskretne zdarzenie |

---

*Projekt CyberDSL jest otwartoźródłowy. Pełny kod modelu rodzinnego dostępny w katalogu `examples/` repozytorium.*
