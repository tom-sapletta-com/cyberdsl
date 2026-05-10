"""
CyberDSL Runtime — silnik symulacji krokowej.

Każdy krok:
  1. Zbiera sygnały opóźnione (delay).
  2. Buduje środowisko ewaluacji reguł.
  3. Oblicza nowe stany węzłów (atomowo).
  4. Liczy obserwable.
  5. Zapisuje snapshot do timeline.
"""
from __future__ import annotations

import copy
import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any

from .parser import ModelDef, parse_dsl


# ─── Compiler (walidacja + normalizacja) ──────────────────────────────────────

class ModelCompiler:
    def parse(self, dsl: str) -> ModelDef:
        model = parse_dsl(dsl)
        self._validate(model)
        return model

    def _validate(self, model: ModelDef) -> None:
        edge_node_ids = {e.src for e in model.edges} | {e.dst for e in model.edges}
        unknown = edge_node_ids - set(model.nodes)
        if unknown:
            raise ValueError(f"Krawędzie odwołują się do nieznanych węzłów: {unknown}")
        rule_node_ids = {r.node for r in model.rules}
        unknown_rule = rule_node_ids - set(model.nodes)
        if unknown_rule:
            raise ValueError(f"Reguły odwołują się do nieznanych węzłów: {unknown_rule}")


# ─── Simulation ───────────────────────────────────────────────────────────────

@dataclass
class SimulationResult:
    model_name: str
    steps_run: int
    timeline: list[dict[str, Any]] = field(default_factory=list)

    def observables_over_time(self) -> dict[str, list[float]]:
        result: dict[str, list[float]] = defaultdict(list)
        for snap in self.timeline:
            for k, v in snap.get('observables', {}).items():
                result[k].append(v)
        return dict(result)

    def node_state_over_time(self, node_id: str, var: str) -> list[float]:
        return [
            snap['nodes'].get(node_id, {}).get(var, float('nan'))
            for snap in self.timeline
        ]

    def summary(self) -> str:
        if not self.timeline:
            return "Brak danych symulacji."
        last = self.timeline[-1]
        lines = [f"=== {self.model_name} | krok {self.steps_run} ==="]
        lines.append("Obserwable końcowe:")
        for k, v in last.get('observables', {}).items():
            lines.append(f"  {k} = {v:.4f}" if isinstance(v, float) else f"  {k} = {v}")
        lines.append("Stany węzłów końcowe:")
        for nid, state in last.get('nodes', {}).items():
            parts = ", ".join(f"{k}={v:.3f}" for k, v in state.items() if isinstance(v, float))
            lines.append(f"  {nid}: {parts}")
        return "\n".join(lines)


def _safe_clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


class Simulation:
    def __init__(self, model: ModelDef):
        self.model = model
        # Current node states: {node_id: {var: float}}
        self._states: dict[str, dict[str, float]] = {
            nid: copy.deepcopy(node.state)
            for nid, node in model.nodes.items()
        }
        # Signal buffers for delayed edges: deque per (src, dst)
        self._signal_buffer: dict[tuple[str, str], deque] = defaultdict(deque)

    def _build_signals(self, node_id: str, step: int) -> dict[str, Any]:
        """Build the `signals` dict for a given node's rule evaluation."""
        signals: dict[str, Any] = {}
        weight_sum = 0.0
        influence_sum = 0.0

        for edge in self.model.edges:
            if edge.dst != node_id:
                continue
            key = (edge.src, edge.dst)
            buf = self._signal_buffer[key]
            # The buffered signal at the right delay slot
            if len(buf) > edge.delay:
                src_state = buf[edge.delay]
            else:
                src_state = copy.deepcopy(self._states.get(edge.src, {}))

            src_label = edge.src
            signals[f'sig_{src_label}'] = src_state
            signals[f'w_{src_label}'] = edge.weight

            # Aggregate weighted influence (first state variable)
            first_val = next(iter(src_state.values()), 0.0) if src_state else 0.0
            influence_sum += edge.weight * first_val
            weight_sum += edge.weight

        signals['sum_influence'] = influence_sum
        signals['total_weight'] = weight_sum
        return signals

    def _push_signals(self) -> None:
        """Snapshot current states into delay buffers."""
        for edge in self.model.edges:
            key = (edge.src, edge.dst)
            buf = self._signal_buffer[key]
            buf.appendleft(copy.deepcopy(self._states.get(edge.src, {})))
            # Keep buffer at max needed depth
            max_delay = max(
                (e.delay for e in self.model.edges if (e.src, e.dst) == key),
                default=0
            ) + 1
            while len(buf) > max_delay + 1:
                buf.pop()

    def _eval_rules(self, step: int) -> dict[str, dict[str, float]]:
        """Calculate new states atomically."""
        new_states = copy.deepcopy(self._states)

        for rule in self.model.rules:
            node = self.model.nodes.get(rule.node)
            if node is None:
                continue
            self_state = self._states.get(rule.node, {})
            signals = self._build_signals(rule.node, step)

            local_env = {
                'self': self_state,
                'params': node.params,
                'globals': self.model.globals,
                'signals': signals,
                'sum_influence': signals['sum_influence'],
                'clip': _safe_clip,
                'math': math,
                'min': min,
                'max': max,
                'abs': abs,
                'nodes': self._states,
                'step': step,
            }
            try:
                result = eval(rule.expr, {"__builtins__": {}}, local_env)  # noqa: S307
                new_states.setdefault(rule.node, {})[rule.var] = float(result)
            except Exception as exc:
                # Reguła zawodzi → zostawiamy poprzedni stan
                pass  # noqa: S110

        return new_states

    def _eval_observables(self) -> dict[str, Any]:
        obs: dict[str, Any] = {}
        for name, expr in self.model.observables.items():
            local_env = {
                'nodes': self._states,
                'globals': self.model.globals,
                'clip': _safe_clip,
                'math': math,
                'min': min,
                'max': max,
                'abs': abs,
            }
            try:
                obs[name] = eval(expr, {"__builtins__": {}}, local_env)  # noqa: S307
            except Exception:
                obs[name] = None
        return obs

    def step(self, step_no: int) -> dict[str, Any]:
        """Perform one simulation step and return a snapshot."""
        self._push_signals()
        new_states = self._eval_rules(step_no)
        self._states = new_states
        obs = self._eval_observables()
        return {
            'step': step_no,
            'nodes': copy.deepcopy(self._states),
            'observables': obs,
            'globals': copy.deepcopy(self.model.globals),
        }

    def run(self, steps: int | None = None) -> SimulationResult:
        """Run the full simulation."""
        n_steps = steps if steps is not None else self.model.steps
        result = SimulationResult(model_name=self.model.name, steps_run=n_steps)
        for i in range(1, n_steps + 1):
            snap = self.step(i)
            result.timeline.append(snap)
        return result

    def apply_shock(self, node_id: str, var: str, delta: float) -> None:
        """Apply an external shock to a node variable (interwencja)."""
        if node_id in self._states and var in self._states[node_id]:
            self._states[node_id][var] = _safe_clip(
                self._states[node_id][var] + delta
            )

    def set_global(self, key: str, value: float) -> None:
        """Override a global parameter mid-simulation."""
        self.model.globals[key] = value
