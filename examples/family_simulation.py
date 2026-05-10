"""
examples/family_simulation.py
==============================
Cybernetyczna analiza systemu rodzinnego — małżeństwo i rozwód.

Uruchamia trzy scenariusze (48 kroków = 4 lata każdy):

  A) Stabilne małżeństwo — niski stres, wsparcie terapii
  B) Kryzys małżeński — rosnące napięcia, bez interwencji
  C) Separacja i rozwód — ostry szok, adaptacja porozwodowa

Dla każdego scenariusza oblicza serie czasowe kluczowych obserwabli
i drukuje raport tekstowy.
"""

from __future__ import annotations

import copy
import pathlib
from cyberdsl import ModelCompiler, Simulation

# ─── Wczytaj model bazowy ─────────────────────────────────────────────────────

BASE_DSL = (pathlib.Path(__file__).parent / "family_model.cyberdsl").read_text(encoding="utf-8")
BASE_MODEL = ModelCompiler().parse(BASE_DSL)


def fresh_sim() -> Simulation:
    """Zwraca świeżą symulację (głęboka kopia modelu)."""
    return Simulation(copy.deepcopy(BASE_MODEL))


# ─── Scenariusz A: Stabilne małżeństwo ───────────────────────────────────────

def scenario_stable() -> dict:
    """Niska presja zewnętrzna, sporadyczna terapia, dobre wsparcie społeczne."""
    sim = fresh_sim()
    sim.set_global("external_stress",   0.15)
    sim.set_global("economic_pressure", 0.20)
    sim.set_global("social_support",    0.75)

    timeline = []
    for step in range(1, 49):
        # Miesiąc 12: para decyduje się na terapię prewencyjną
        if step == 12:
            sim.set_global("therapy_effect", 0.30)
        # Miesiąc 24: koniec terapii
        if step == 24:
            sim.set_global("therapy_effect", 0.00)
        snap = sim.step(step)
        timeline.append(snap)

    return {"label": "A: Stabilne małżeństwo", "timeline": timeline, "sim": sim}


# ─── Scenariusz B: Kryzys małżeński ──────────────────────────────────────────

def scenario_crisis() -> dict:
    """Rosnący stres ekonomiczny, utrata pracy ojca w miesiącu 8."""
    sim = fresh_sim()
    sim.set_global("external_stress",   0.45)
    sim.set_global("economic_pressure", 0.55)
    sim.set_global("social_support",    0.40)

    timeline = []
    for step in range(1, 49):
        # Miesiąc 8: ojciec traci pracę — ostry szok
        if step == 8:
            sim.set_global("crisis_event", 0.60)
            sim.apply_shock("father", "stress",    +0.30)
            sim.apply_shock("father", "wellbeing", -0.25)
            sim.apply_shock("marriage", "conflict", +0.20)
        # Miesiąc 9: szok wygasa (ale skutki trwają w stanach)
        if step == 9:
            sim.set_global("crisis_event", 0.00)
        # Miesiąc 16: matka proponuje terapię, ojciec odmawia
        if step == 16:
            sim.set_global("therapy_effect", 0.05)  # minimalna, jednostronna
        # Miesiąc 24: eskalacja konfliktów
        if step == 24:
            sim.set_global("economic_pressure", 0.70)
            sim.apply_shock("marriage", "conflict", +0.15)
        snap = sim.step(step)
        timeline.append(snap)

    return {"label": "B: Kryzys małżeński", "timeline": timeline, "sim": sim}


# ─── Scenariusz C: Separacja i rozwód ────────────────────────────────────────

def scenario_divorce() -> dict:
    """
    Miesiące 1-12:  narastający konflikt (jak scenariusz B).
    Miesiąc 13:     separacja — silny szok systemowy.
    Miesiące 14-30: adaptacja, dzieci w terapii.
    Miesiące 31-48: nowe równowagi — matka główny opiekun.
    """
    sim = fresh_sim()
    sim.set_global("external_stress",   0.50)
    sim.set_global("economic_pressure", 0.60)
    sim.set_global("social_support",    0.45)

    timeline = []
    for step in range(1, 49):

        # ── Faza I: Narastanie (1–12) ──────────────────────────────────
        if step == 6:
            sim.apply_shock("marriage", "conflict",   +0.20)
            sim.apply_shock("marriage", "intimacy",   -0.15)
        if step == 10:
            sim.apply_shock("marriage", "cohesion",   -0.18)
            sim.apply_shock("marriage", "commitment", -0.12)
            sim.apply_shock("child_elder",   "anxiety", +0.15)
            sim.apply_shock("child_younger", "anxiety", +0.18)

        # ── Faza II: Separacja (miesiąc 13) ────────────────────────────
        if step == 13:
            sim.set_global("crisis_event", 0.80)
            # Ojciec wyprowadza się
            sim.apply_shock("father",   "wellbeing",   -0.30)
            sim.apply_shock("father",   "attachment",  -0.20)
            sim.apply_shock("mother",   "stress",      +0.25)
            sim.apply_shock("mother",   "wellbeing",   -0.20)
            sim.apply_shock("marriage", "cohesion",    -0.40)
            sim.apply_shock("marriage", "intimacy",    -0.45)
            sim.apply_shock("marriage", "commitment",  -0.50)
            # Dzieci — szok bezpieczeństwa
            sim.apply_shock("child_elder",   "security", -0.30)
            sim.apply_shock("child_elder",   "anxiety",  +0.35)
            sim.apply_shock("child_younger", "security", -0.38)
            sim.apply_shock("child_younger", "anxiety",  +0.40)

        if step == 14:
            sim.set_global("crisis_event", 0.20)  # wygasanie szoku

        # ── Faza III: Adaptacja (14–30) ─────────────────────────────────
        if step == 15:
            sim.set_global("crisis_event",  0.00)
            sim.set_global("therapy_effect", 0.25)   # dzieci i matka w terapii

        if step == 20:
            # Matka stabilizuje się — wsparcie rodziny rozszerzonej
            sim.set_global("social_support", 0.65)
            sim.apply_shock("mother", "wellbeing", +0.10)

        if step == 24:
            # Ojciec nawiązuje regularny kontakt z dziećmi
            sim.apply_shock("child_elder",   "security", +0.12)
            sim.apply_shock("child_younger", "security", +0.10)
            sim.apply_shock("father",        "wellbeing", +0.08)

        # ── Faza IV: Nowe equilibrium (31–48) ───────────────────────────
        if step == 31:
            sim.set_global("therapy_effect",    0.10)   # terapia sporadyczna
            sim.set_global("economic_pressure", 0.40)   # stabilizacja finansów
            sim.apply_shock("mother",  "autonomy",  +0.15)
            sim.apply_shock("father",  "autonomy",  +0.12)

        if step == 40:
            # Matka wraca do pracy, ojciec partnerski model opieki
            sim.set_global("external_stress", 0.25)
            sim.apply_shock("child_elder",   "wellbeing", +0.08)
            sim.apply_shock("child_younger", "wellbeing", +0.06)

        snap = sim.step(step)
        timeline.append(snap)

    return {"label": "C: Separacja i rozwód", "timeline": timeline, "sim": sim}


# ─── Raport ───────────────────────────────────────────────────────────────────

OBSERVABLES_LABELS = {
    "family_wellbeing":      "Dobrostan rodziny",
    "parental_stress_avg":   "Stres rodziców (śr.)",
    "children_security_avg": "Poczucie bezpieczeństwa dzieci",
    "children_anxiety_avg":  "Lęk dzieci (śr.)",
    "marriage_health":       "Zdrowie małżeństwa",
    "divorce_risk":          "Ryzyko rozpadu",
    "system_resilience":     "Odporność systemu",
}

MILESTONES = {
    # scenariusz C
    12: "koniec Fazy I",
    13: "⚡ separacja",
    15: "terapia start",
    24: "regularny kontakt ojca",
    31: "nowe equilibrium",
    48: "koniec symulacji",
}


def _obs_at(timeline: list, step: int) -> dict:
    return timeline[step - 1]["observables"]


def print_report(result: dict) -> None:
    label = result["label"]
    tl = result["timeline"]
    print(f"\n{'═' * 64}")
    print(f"  {label}")
    print(f"{'═' * 64}")
    print(f"{'Wskaźnik':<32} {'krok 1':>8} {'krok 12':>8} {'krok 24':>8} {'krok 36':>8} {'krok 48':>8}")
    print(f"{'-' * 64}")
    for key, lbl in OBSERVABLES_LABELS.items():
        vals = [_obs_at(tl, s)[key] for s in [1, 12, 24, 36, 48]]
        vals_str = "  ".join(f"{v:6.3f}" for v in vals)
        print(f"  {lbl:<30} {vals_str}")

    # Trend arrow
    print()
    print("  Trendy (krok 1 → 48):")
    for key, lbl in OBSERVABLES_LABELS.items():
        v0 = _obs_at(tl, 1)[key]
        vN = _obs_at(tl, 48)[key]
        diff = vN - v0
        arrow = "▲" if diff > 0.02 else ("▼" if diff < -0.02 else "→")
        print(f"    {lbl:<32} {v0:.3f} → {vN:.3f}  {arrow} ({diff:+.3f})")


def print_comparison(results: list[dict]) -> None:
    """Porównanie końcowych wartości obserwabli między scenariuszami."""
    print(f"\n{'═' * 72}")
    print("  PORÓWNANIE SCENARIUSZY — krok 48")
    print(f"{'═' * 72}")
    labels_short = [r["label"].split(":")[0] for r in results]
    header = f"{'Wskaźnik':<34}" + "".join(f"{l:>12}" for l in labels_short)
    print(header)
    print("-" * 72)
    for key, lbl in OBSERVABLES_LABELS.items():
        row = f"  {lbl:<32}"
        for r in results:
            v = _obs_at(r["timeline"], 48)[key]
            row += f"  {v:8.3f}  "
        print(row)


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 64)
    print("  CyberDSL — Analiza cybernetyczna systemu rodzinnego")
    print("  Model: Rodzina Kowalskich | 4 lata (48 kroków)")
    print("=" * 64)

    print("\nUruchamianie scenariuszy...")
    results = [
        scenario_stable(),
        scenario_crisis(),
        scenario_divorce(),
    ]

    for r in results:
        print_report(r)

    print_comparison(results)

    print(f"\n{'═' * 64}")
    print("  INTERPRETACJA CYBERNETYCZNA")
    print(f"{'═' * 64}")
    print("""
  System rodzinny to układ sprzężeń zwrotnych między podsystemami:
  małżeńskim, rodzicielskim i dziecięcym. Kluczowe mechanizmy:

  1. HOMEOSTAZA (clip):  stany utrzymywane w [0, 1] — system
     szuka równowagi, ale szoki przesuwają punkty równowagi.

  2. OPÓŹNIENIA (delay): skutki konfliktów małżeńskich docierają
     do dzieci z opóźnieniem 1–2 kroków — zgodnie z teorią Bowena.

  3. SPRZĘŻENIE ZWROTNE: lęk dzieci wzmacnia stres rodziców
     (pętla dodatnia), terapia tworzy pętlę ujemną stabilizującą.

  4. ROZWÓD jako dyskretne zdarzenie: silny szok obniża stany
     poniżej progu poprzedniej homeostazy — system musi znaleźć
     nowy punkt równowagi (nowe equilibrium).

  5. ODPORNOŚĆ (resilience): systemy z wyższym social_support
     i therapy_effect szybciej wracają do funkcjonalności.
""")
