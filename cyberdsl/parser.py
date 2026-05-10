"""
CyberDSL — lekki parser DSL dla modeli cybernetycznych.

Gramatyka (liniowa, bez pełnego AST):

  model:
    name = "..."
    steps = <int>

  globals:
    key = <float>
    ...

  nodes:
    id:type | state={k:v,...} | param=val ...

  edges:
    src->dst:rel | weight=<float> | delay=<int>

  rules:
    node.var => <expression>

  observables:
    name = <expression>
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ─── Data structures ──────────────────────────────────────────────────────────

@dataclass
class NodeDef:
    id: str
    kind: str = "group"
    state: dict[str, float] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class EdgeDef:
    src: str
    dst: str
    relation: str = "influence"
    weight: float = 1.0
    delay: int = 0


@dataclass
class RuleDef:
    node: str
    var: str
    expr: str


@dataclass
class ModelDef:
    name: str = "unnamed"
    steps: int = 10
    globals: dict[str, float] = field(default_factory=dict)
    nodes: dict[str, NodeDef] = field(default_factory=dict)
    edges: list[EdgeDef] = field(default_factory=list)
    rules: list[RuleDef] = field(default_factory=list)
    observables: dict[str, str] = field(default_factory=dict)


# ─── Parser ───────────────────────────────────────────────────────────────────

class ParseError(Exception):
    pass


def _strip_inline_comment(line: str) -> str:
    """Remove trailing # comments (but not inside strings)."""
    # Very simple: find first # not inside quotes
    in_str = False
    quote_char = None
    for i, ch in enumerate(line):
        if in_str:
            if ch == quote_char:
                in_str = False
        else:
            if ch in ('"', "'"):
                in_str = True
                quote_char = ch
            elif ch == '#':
                return line[:i].rstrip()
    return line


def _parse_dict_literal(s: str) -> dict[str, float]:
    """Parse {k:v, k:v} into dict. Values coerced to float."""
    s = s.strip()
    if s.startswith('{'):
        s = s[1:]
    if s.endswith('}'):
        s = s[:-1]
    result: dict[str, float] = {}
    for pair in s.split(','):
        pair = pair.strip()
        if not pair:
            continue
        if ':' not in pair:
            raise ParseError(f"Bad dict pair: {pair!r}")
        k, v = pair.split(':', 1)
        try:
            result[k.strip()] = float(v.strip())
        except ValueError:
            result[k.strip()] = v.strip()  # type: ignore[assignment]
    return result


def _parse_value(v: str) -> Any:
    v = v.strip()
    if v.startswith('{'):
        return _parse_dict_literal(v)
    if v.startswith(('"', "'")):
        return v.strip('"\'')
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _parse_node_line(line: str) -> NodeDef:
    """
    youth:group | state={cohesion:0.45, trust:0.40} | adaptability=0.70
    """
    parts = [p.strip() for p in line.split('|')]
    id_kind = parts[0]
    if ':' in id_kind:
        node_id, kind = id_kind.split(':', 1)
    else:
        node_id, kind = id_kind, 'group'
    node = NodeDef(id=node_id.strip(), kind=kind.strip())
    for attr in parts[1:]:
        if '=' not in attr:
            continue
        k, v = attr.split('=', 1)
        k, v = k.strip(), v.strip()
        if k == 'state':
            node.state = _parse_dict_literal(v)
        else:
            node.params[k] = _parse_value(v)
    return node


def _parse_edge_line(line: str) -> EdgeDef:
    """
    council->youth:influence | weight=0.30 | delay=1
    """
    parts = [p.strip() for p in line.split('|')]
    src_dst_rel = parts[0]
    # src->dst:rel
    m = re.match(r'(\w+)\s*->\s*(\w+)(?::(\w+))?', src_dst_rel)
    if not m:
        raise ParseError(f"Invalid edge: {src_dst_rel!r}")
    src, dst, rel = m.group(1), m.group(2), m.group(3) or 'influence'
    edge = EdgeDef(src=src, dst=dst, relation=rel)
    for attr in parts[1:]:
        if '=' not in attr:
            continue
        k, v = attr.split('=', 1)
        k, v = k.strip(), v.strip()
        if k == 'weight':
            edge.weight = float(v)
        elif k == 'delay':
            edge.delay = int(v)
    return edge


def parse_dsl(text: str) -> ModelDef:
    """Parse CyberDSL text into a ModelDef."""
    model = ModelDef()
    current_section: str | None = None
    section_keywords = {'model', 'globals', 'nodes', 'edges', 'rules', 'observables'}

    for raw_line in text.splitlines():
        line = _strip_inline_comment(raw_line)
        stripped = line.strip()
        if not stripped:
            continue

        # Section header — no leading whitespace, ends with ':'
        if re.match(r'^[a-z_]+\s*:', stripped) and stripped.rstrip().endswith(':'):
            section = stripped.rstrip(':').strip().lower()
            if section in section_keywords:
                current_section = section
            continue

        if current_section is None:
            continue

        # ── model ──
        if current_section == 'model':
            if '=' in stripped:
                k, v = stripped.split('=', 1)
                k, v = k.strip(), v.strip().strip('"\'')
                if k == 'name':
                    model.name = v
                elif k == 'steps':
                    model.steps = int(v)

        # ── globals ──
        elif current_section == 'globals':
            if '=' in stripped:
                k, v = stripped.split('=', 1)
                model.globals[k.strip()] = float(v.strip())

        # ── nodes ──
        elif current_section == 'nodes':
            node = _parse_node_line(stripped)
            model.nodes[node.id] = node

        # ── edges ──
        elif current_section == 'edges':
            edge = _parse_edge_line(stripped)
            model.edges.append(edge)

        # ── rules ──
        elif current_section == 'rules':
            # node.var => expr
            m = re.match(r'(\w+)\.(\w+)\s*=>\s*(.+)', stripped)
            if m:
                model.rules.append(RuleDef(
                    node=m.group(1),
                    var=m.group(2),
                    expr=m.group(3).strip(),
                ))

        # ── observables ──
        elif current_section == 'observables':
            if '=' in stripped:
                k, v = stripped.split('=', 1)
                model.observables[k.strip()] = v.strip()

    return model
