# CyberDSL YAML — Dokumentacja dla LLM

## Cel

CyberDSL to język do modelowania **złożonych systemów społecznych, psychologicznych i instytucjonalnych** jako sieci węzłów ze stanami, połączonych krawędziami wpływu, ewoluujących w czasie zgodnie z regułami cybernetycznymi.

Format YAML pozwala LLM na tworzenie takich modeli w sposób ustrukturyzowany, walidowalny i czytelny.

---

## Kiedy używać CyberDSL YAML

Użyj tego formatu gdy problem zawiera:

- **Wielu aktorów** (osoby, grupy, instytucje) z wewnętrznymi stanami psychologicznymi lub społecznymi
- **Wzajemne oddziaływania** — kto na kogo wpływa, z jaką siłą i opóźnieniem
- **Dynamikę czasową** — jak stany zmieniają się krok po kroku
- **Zmienne globalne** — kontekst (stres ekonomiczny, kryzys, wsparcie)
- **Obserwowalne wskaźniki** — co chcemy śledzić w czasie

**Przykłady dziedzin:** rodzina, społeczność lokalna, organizacja, konflikt polityczny, zdrowie publiczne, ekosystem, rynek.

---

## Struktura pliku YAML

```yaml
model:
  name: "Nazwa modelu"
  steps: <liczba kroków czasowych>

globals:
  <parametr>: <float 0.0–1.0>

nodes:
  <id_węzła>:
    kind: <group|actor|institution|subsystem>
    state:
      <zmienna>: <float 0.0–1.0>
    params:           # opcjonalne parametry stałe węzła
      <parametr>: <wartość>

edges:
  - src: <id_węzła_źródłowego>
    dst: <id_węzła_docelowego>
    relation: <nazwa_relacji>
    weight: <float 0.0–1.0>
    delay: <int ≥ 0>

rules:
  - node: <id_węzła>
    var: <zmienna_stanu>
    expr: "<wyrażenie Python>"

observables:
  <nazwa_wskaźnika>: "<wyrażenie Python>"
```

---

## Sekcje — szczegółowy opis

### `model`

```yaml
model:
  name: "Kryzys-Miejski-2024"
  steps: 24       # 24 kroki = np. 24 miesiące
```

- `name` — identyfikator modelu (string)
- `steps` — domyślna liczba kroków symulacji (int)

---

### `globals`

Parametry środowiskowe wspólne dla całego systemu. Wartości w zakresie `[0.0, 1.0]`.

```yaml
globals:
  stress: 0.40          # stres zewnętrzny (0=brak, 1=maksymalny)
  support: 0.55         # wsparcie instytucjonalne/społeczne
  crisis_event: 0.00    # nagłe zdarzenie (0=brak, 1=pełny kryzys)
  therapy_effect: 0.00  # efekt interwencji terapeutycznej
```

**Zasada:** globale opisują **kontekst systemowy**, nie stany aktorów. Zmieniaj je przez `sim.set_global()` podczas scenariuszy.

---

### `nodes`

Każdy węzeł to aktor systemu z **wewnętrznym stanem** (zmienne dynamiczne) i opcjonalnymi **parametrami stałymi**.

```yaml
nodes:
  youth:
    kind: group
    state:
      cohesion: 0.45      # spójność grupy
      trust: 0.40         # zaufanie do instytucji
      activism: 0.60      # poziom aktywizmu
    params:
      adaptability: 0.75  # zdolność adaptacji (stała)

  city_hall:
    kind: institution
    state:
      cohesion: 0.80
      trust: 0.50
      legitimacy: 0.70
    params:
      authority: 0.80
```

#### Rodzaje węzłów (`kind`)

| Kind | Zastosowanie |
|---|---|
| `actor` | Pojedyncza osoba (matka, ojciec, lider) |
| `group` | Zbiorowość (młodzież, rybacy, pracownicy) |
| `institution` | Organizacja formalna (urząd, szpital, szkoła) |
| `subsystem` | Abstrakcyjny podsystem (małżeństwo, rynek, więź) |

#### Zmienne stanu

- Zawsze w zakresie `[0.0, 1.0]` — wymuszone przez funkcję `clip()`
- Reprezentują natężenie cechy: `0.0` = minimum, `1.0` = maksimum
- Typowe zmienne: `wellbeing`, `trust`, `stress`, `cohesion`, `conflict`, `anxiety`, `security`, `legitimacy`, `activism`

---

### `edges`

Kanały przepływu wpływu między węzłami.

```yaml
edges:
  - src: city_hall
    dst: youth
    relation: influence
    weight: 0.35
    delay: 1

  - src: youth
    dst: city_hall
    relation: feedback
    weight: 0.30
    delay: 0

  - src: marriage
    dst: child_elder
    relation: parental_climate
    weight: 0.45
    delay: 1
```

| Pole | Znaczenie |
|---|---|
| `src` | Węzeł źródłowy (nadawca sygnału) |
| `dst` | Węzeł docelowy (odbiorca) |
| `relation` | Nazwa typu relacji (dowolna, opisowa) |
| `weight` | Siła wpływu `[0.0–1.0]` |
| `delay` | Opóźnienie w krokach (0 = natychmiastowe) |

**Wzorce relacji:**
- `delay=0` — natychmiastowe sprzężenie (emocje, reakcja w tej samej chwili)
- `delay=1` — opóźnienie jednego kroku (np. miesięczna odpowiedź instytucji)
- `delay=2` — wolne procesy (np. wpływ konfliktu na dzieci)

---

### `rules`

Równania aktualizacji stanu. Każda reguła oblicza **nową wartość jednej zmiennej** dla jednego węzła.

```yaml
rules:
  - node: youth
    var: trust
    expr: "clip(self['trust'] + 0.08*signals.get('w_city_hall',0)*signals.get('sig_city_hall',{}).get('legitimacy',0) - 0.09*globals['stress'])"

  - node: marriage
    var: conflict
    expr: "clip(self['conflict'] + 0.10*nodes['mother']['stress'] + 0.10*nodes['father']['stress'] - 0.15*globals['therapy_effect'])"
```

#### Zmienne dostępne w wyrażeniach

| Zmienna | Typ | Opis |
|---|---|---|
| `self` | `dict` | Stan bieżącego węzła: `self['zmienna']` |
| `globals` | `dict` | Parametry globalne: `globals['stress']` |
| `nodes` | `dict` | Stany wszystkich węzłów: `nodes['youth']['trust']` |
| `signals` | `dict` | Sygnały wejściowe z krawędzi |
| `sum_influence` | `float` | Ważona suma wszystkich sygnałów wejściowych |
| `clip(x)` | `float` | Obcięcie do `[0, 1]` — **zawsze używaj!** |
| `math` | moduł | `math.exp()`, `math.log()` itp. |
| `min`, `max`, `abs` | func | Standardowe funkcje Python |
| `params` | `dict` | Stałe parametry węzła |

#### Dostęp do sygnałów z krawędzi

Gdy krawędź `src → dst` istnieje, w regułach `dst` dostępne są:
- `signals.get('sig_<src>', {})` — słownik stanu węzła `src` (z opóźnieniem)
- `signals.get('w_<src>', 0)` — waga krawędzi `src → dst`

```python
# Przykład: wpływ legitimacy urzędu na trust młodzieży
"clip(self['trust'] + 0.08 * signals.get('w_city_hall', 0) * signals.get('sig_city_hall', {}).get('legitimacy', 0))"
```

#### Wzorce reguł

```python
# Wzrost pod wpływem sygnału zewnętrznego
"clip(self['x'] + 0.10 * sum_influence - 0.05 * globals['stress'])"

# Sprzężenie zwrotne ujemne (homeostaza)
"clip(self['cohesion'] - 0.15 * self['conflict'] + 0.08 * globals['therapy_effect'])"

# Zależność od stanu innego węzła
"clip(self['anxiety'] + 0.12 * nodes['marriage']['conflict'] - 0.08 * nodes['marriage']['cohesion'])"

# Efekt interwencji zewnętrznej
"clip(self['wellbeing'] - 0.12 * self['stress'] + 0.06 * globals['therapy_effect'] - 0.10 * globals['crisis_event'])"

# Średnia z dwóch węzłów
"clip((nodes['mother']['wellbeing'] + nodes['father']['wellbeing']) / 2)"
```

---

### `observables`

Wskaźniki liczone po każdym kroku — nie zmieniają stanów, tylko je agregują.

```yaml
observables:
  avg_trust: "(nodes['fishers']['trust'] + nodes['youth']['trust'] + nodes['city_hall']['trust']) / 3"
  social_resilience: "(nodes['fishers']['cohesion'] + nodes['youth']['trust'] + nodes['city_hall']['legitimacy']) / 3"
  tension_index: "globals['stress'] * (1 - nodes['fishers']['trust']) * nodes['youth']['activism']"
  marriage_health: "(nodes['marriage']['cohesion'] + nodes['marriage']['intimacy'] + (1 - nodes['marriage']['conflict'])) / 3"
  divorce_risk: "clip((nodes['marriage']['conflict'] - nodes['marriage']['commitment'] * 0.5) * (1 - nodes['marriage']['cohesion']))"
```

**Zasada:** obserwable to **pytania badawcze** modelu — co chcemy śledzić w czasie.

---

## Kompletny przykład — system społeczności portowej

```yaml
model:
  name: "Społeczność-portowa"
  steps: 16

globals:
  stress: 0.40
  support: 0.50
  external_shock: 0.0

nodes:
  fishers:
    kind: group
    state:
      cohesion: 0.65
      trust: 0.55
      activism: 0.30
    params:
      adaptability: 0.40

  youth:
    kind: group
    state:
      cohesion: 0.45
      trust: 0.40
      activism: 0.60
    params:
      adaptability: 0.75

  city_hall:
    kind: institution
    state:
      cohesion: 0.80
      trust: 0.50
      legitimacy: 0.70
    params:
      authority: 0.80

edges:
  - src: city_hall
    dst: youth
    relation: influence
    weight: 0.35
    delay: 1
  - src: city_hall
    dst: fishers
    relation: policy
    weight: 0.20
    delay: 2
  - src: fishers
    dst: youth
    relation: stabilize
    weight: 0.25
    delay: 1
  - src: youth
    dst: city_hall
    relation: feedback
    weight: 0.30
    delay: 0
  - src: fishers
    dst: city_hall
    relation: lobby
    weight: 0.15
    delay: 1

rules:
  - node: youth
    var: cohesion
    expr: "clip(self['cohesion'] + 0.12*sum_influence - 0.10*globals['stress'] + 0.07*globals['support'])"
  - node: youth
    var: trust
    expr: "clip(self['trust'] + 0.08*signals.get('w_city_hall',0)*signals.get('sig_city_hall',{}).get('legitimacy',0) - 0.09*globals['stress'])"
  - node: youth
    var: activism
    expr: "clip(self['activism'] + 0.15*globals['stress'] - 0.10*globals['support'])"
  - node: fishers
    var: cohesion
    expr: "clip(self['cohesion'] + 0.05*sum_influence - 0.08*globals['stress'])"
  - node: fishers
    var: trust
    expr: "clip(self['trust'] + 0.06*globals['support'] - 0.10*globals['stress'] - 0.05*globals['external_shock'])"
  - node: city_hall
    var: trust
    expr: "clip(self['trust'] + 0.10*signals.get('w_youth',0)*signals.get('sig_youth',{}).get('trust',0) - 0.07*globals['stress'] + 0.05*globals['support'])"
  - node: city_hall
    var: legitimacy
    expr: "clip(self['legitimacy'] + 0.08*signals.get('w_youth',0)*signals.get('sig_youth',{}).get('trust',0) - 0.12*(1 - globals['support']))"

observables:
  avg_trust: "(nodes['fishers']['trust'] + nodes['youth']['trust'] + nodes['city_hall']['trust']) / 3"
  avg_cohesion: "(nodes['fishers']['cohesion'] + nodes['youth']['cohesion'] + nodes['city_hall']['cohesion']) / 3"
  social_resilience: "(nodes['fishers']['cohesion'] + nodes['youth']['trust'] + nodes['city_hall']['legitimacy']) / 3"
  tension_index: "globals['stress'] * (1 - nodes['fishers']['trust']) * nodes['youth']['activism']"
```

---

## Kompletny przykład — system rodzinny

```yaml
model:
  name: "Rodzina-Kowalskich"
  steps: 48

globals:
  external_stress: 0.25
  economic_pressure: 0.30
  social_support: 0.60
  therapy_effect: 0.00
  crisis_event: 0.00

nodes:
  mother:
    kind: actor
    state:
      wellbeing: 0.70
      attachment: 0.75
      autonomy: 0.65
      stress: 0.30
    params:
      resilience: 0.60
      role: parent

  father:
    kind: actor
    state:
      wellbeing: 0.65
      attachment: 0.70
      autonomy: 0.70
      stress: 0.35
    params:
      resilience: 0.55
      role: parent

  marriage:
    kind: subsystem
    state:
      cohesion: 0.72
      conflict: 0.20
      intimacy: 0.65
      commitment: 0.80
    params:
      age_years: 8

  child_elder:
    kind: actor
    state:
      wellbeing: 0.80
      security: 0.75
      anxiety: 0.15
    params:
      age: 10
      resilience: 0.65

  child_younger:
    kind: actor
    state:
      wellbeing: 0.82
      security: 0.78
      anxiety: 0.10
    params:
      age: 6
      resilience: 0.50

edges:
  - {src: mother, dst: father, relation: emotional_influence, weight: 0.40, delay: 0}
  - {src: father, dst: mother, relation: emotional_influence, weight: 0.38, delay: 0}
  - {src: mother, dst: marriage, relation: parental_input, weight: 0.45, delay: 1}
  - {src: father, dst: marriage, relation: parental_input, weight: 0.45, delay: 1}
  - {src: marriage, dst: mother, relation: couple_feedback, weight: 0.35, delay: 1}
  - {src: marriage, dst: father, relation: couple_feedback, weight: 0.35, delay: 1}
  - {src: mother, dst: child_elder, relation: parenting, weight: 0.40, delay: 1}
  - {src: father, dst: child_elder, relation: parenting, weight: 0.35, delay: 1}
  - {src: mother, dst: child_younger, relation: parenting, weight: 0.45, delay: 1}
  - {src: father, dst: child_younger, relation: parenting, weight: 0.30, delay: 1}
  - {src: child_elder, dst: mother, relation: child_feedback, weight: 0.20, delay: 2}
  - {src: child_younger, dst: mother, relation: child_feedback, weight: 0.22, delay: 2}

rules:
  - node: mother
    var: stress
    expr: "clip(self['stress'] + 0.08*globals['external_stress'] + 0.10*globals['economic_pressure'] - 0.07*globals['social_support'] - 0.05*signals.get('sig_marriage',{}).get('cohesion',0) + 0.15*globals['crisis_event'])"
  - node: mother
    var: wellbeing
    expr: "clip(self['wellbeing'] - 0.12*self['stress'] + 0.08*signals.get('sig_marriage',{}).get('intimacy',0) + 0.06*globals['therapy_effect'] - 0.10*globals['crisis_event'])"
  - node: marriage
    var: conflict
    expr: "clip(self['conflict'] + 0.10*nodes['mother']['stress'] + 0.10*nodes['father']['stress'] - 0.15*globals['therapy_effect'] + 0.20*globals['crisis_event'])"
  - node: marriage
    var: cohesion
    expr: "clip(self['cohesion'] - 0.15*self['conflict'] + 0.06*(nodes['mother']['attachment']+nodes['father']['attachment'])/2 + 0.08*globals['therapy_effect'] - 0.12*globals['crisis_event'])"
  - node: child_elder
    var: anxiety
    expr: "clip(self['anxiety'] + 0.12*nodes['marriage']['conflict'] - 0.08*nodes['marriage']['cohesion'] + 0.10*globals['crisis_event'] - 0.04*globals['social_support'])"
  - node: child_elder
    var: security
    expr: "clip(self['security'] + 0.10*nodes['marriage']['cohesion'] - 0.15*nodes['marriage']['conflict'] - 0.12*globals['crisis_event'])"

observables:
  family_wellbeing: "(nodes['mother']['wellbeing'] + nodes['father']['wellbeing'] + nodes['child_elder']['wellbeing'] + nodes['child_younger']['wellbeing']) / 4"
  parental_stress_avg: "(nodes['mother']['stress'] + nodes['father']['stress']) / 2"
  marriage_health: "(nodes['marriage']['cohesion'] + nodes['marriage']['intimacy'] + nodes['marriage']['commitment'] + (1 - nodes['marriage']['conflict'])) / 4"
  divorce_risk: "clip((nodes['marriage']['conflict'] - nodes['marriage']['commitment']*0.5) * (1 - nodes['marriage']['cohesion']))"
  children_security_avg: "(nodes['child_elder']['security'] + nodes['child_younger']['security']) / 2"
  system_resilience: "(nodes['mother']['wellbeing'] + nodes['father']['wellbeing'] + nodes['marriage']['cohesion'] + nodes['child_elder']['security'] + nodes['child_younger']['security']) / 5"
```

---

## Przewodnik projektowania dla LLM

### Krok 1 — Zidentyfikuj aktorów systemu

Pytania pomocnicze:
- Kto jest w tym systemie? (osoby, grupy, instytucje, procesy)
- Jakie mają wewnętrzne stany (cechy psychologiczne/społeczne)?
- Co je napędza lub hamuje?

### Krok 2 — Zdefiniuj zmienne stanu

Każda zmienna stanu powinna być:
- **Znormalizowana** `[0, 1]`: 0 = minimum cechy, 1 = maksimum
- **Interpretowalnie nazwana**: `trust`, `cohesion`, `stress`, `wellbeing`, `conflict`
- **Mierzalna** konceptualnie — co znaczy 0.3 vs 0.7 dla tej zmiennej?

### Krok 3 — Zmapuj oddziaływania (edges)

Dla każdej pary aktorów zapytaj:
- Czy A wpływa na B? Jak silnie (`weight`)? Z jakim opóźnieniem (`delay`)?
- Czy jest sprzężenie zwrotne B → A?
- Jaki jest charakter relacji (`relation`)? (influence, feedback, control, support, conflict)

### Krok 4 — Napisz reguły

Każda reguła ma postać:
```
nowy_stan = clip(stary_stan + efekty_pozytywne - efekty_negatywne)
```

Typowe składniki:
- `+ 0.05 * globals['support']` — wzmocnienie przez wsparcie systemowe
- `- 0.10 * globals['stress']` — osłabienie przez stres
- `+ 0.08 * signals.get('w_<src>', 0) * signals.get('sig_<src>', {}).get('<var>', 0)` — wpływ konkretnego sąsiada
- `- 0.15 * self['conflict']` — samozatrzymanie przez wewnętrzny stan

**Kalibracja współczynników:**
- `0.01–0.05` — słaby efekt (tło)
- `0.05–0.15` — umiarkowany efekt (typowy)
- `0.15–0.30` — silny efekt (kryzys, interwencja)
- `> 0.30` — bardzo silny (szok systemowy)

### Krok 5 — Zdefiniuj obserwable

Obserwable to odpowiedzi na pytania badawcze:
- Jaki jest ogólny dobrostan systemu?
- Gdzie gromadzi się ryzyko?
- Jak zmienia się odporność/resilience?

---

## Użycie z API Python

```python
from cyberdsl import parse_yaml, dsl_to_yaml, Simulation, ModelCompiler

# Wczytaj model z YAML
yaml_text = open("model.yaml", encoding="utf-8").read()
model = parse_yaml(yaml_text)

# Uruchom symulację
result = Simulation(model).run()
print(result.summary())

# Serie czasowe obserwabli
ot = result.observables_over_time()
# ot["avg_trust"] → lista floatów, jeden na krok

# Interwencje mid-simulation
sim = Simulation(model)
sim.run(steps=12)
sim.apply_shock("youth", "activism", +0.20)   # zewnętrzny szok
sim.set_global("crisis_event", 0.60)           # zmiana kontekstu
sim.run(steps=12)                              # kontynuacja

# Konwersja .cyberdsl → YAML
yaml_out = dsl_to_yaml(open("model.cyberdsl").read())
```

---

## Częste błędy i jak ich unikać

| Błąd | Rozwiązanie |
|---|---|
| Brak `clip()` w regule | Zawsze otaczaj wyrażenie: `clip(...)` |
| Odwołanie do węzła nieistniejącego w `edges` | Każdy `src`/`dst` w edges musi być w `nodes` |
| Zbyt duże współczynniki | System eksploduje — trzymaj sumy efektów < 0.5 na krok |
| `signals.get('sig_X')` gdy X nie ma krawędzi do tego węzła | Używaj `.get()` z defaultem: `signals.get('sig_X', {}).get('var', 0)` |
| Ujemne wartości stanu | `clip()` zapobiega — sprawdź czy go nie pominąłeś |
| Zbyt wiele reguł dla jednego węzła | OK, ale upewnij się że każda `var` jest w `state` węzła |

---

## Skrócony szablon do kopiowania

```yaml
model:
  name: "NAZWA"
  steps: 20

globals:
  stress: 0.30
  support: 0.50

nodes:
  aktor_a:
    kind: group
    state:
      trust: 0.50
      cohesion: 0.60

  aktor_b:
    kind: institution
    state:
      legitimacy: 0.70
      trust: 0.55

edges:
  - src: aktor_b
    dst: aktor_a
    relation: influence
    weight: 0.30
    delay: 1
  - src: aktor_a
    dst: aktor_b
    relation: feedback
    weight: 0.25
    delay: 0

rules:
  - node: aktor_a
    var: trust
    expr: "clip(self['trust'] + 0.08*signals.get('w_aktor_b',0)*signals.get('sig_aktor_b',{}).get('legitimacy',0) - 0.06*globals['stress'])"
  - node: aktor_b
    var: legitimacy
    expr: "clip(self['legitimacy'] + 0.05*sum_influence + 0.04*globals['support'] - 0.08*globals['stress'])"

observables:
  avg_trust: "(nodes['aktor_a']['trust'] + nodes['aktor_b']['trust']) / 2"
  system_health: "(nodes['aktor_a']['cohesion'] + nodes['aktor_b']['legitimacy']) / 2"
```
