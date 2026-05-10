"""
CyberDSL — adapter LiteLLM.

Tłumaczy opis naturalny społeczności / systemu na kod DSL.
"""
from __future__ import annotations

import json
from typing import Any, Optional

SYSTEM_PROMPT = """
You are a CyberDSL expert. Convert natural-language descriptions of communities,
actors, relations, tensions, resources, and time dynamics into valid CyberDSL format.

Rules:
- Return ONLY valid DSL text. No markdown, no code fences, no preamble.
- Model all entities as nodes with id:type format (types: group, institution, subsystem, actor).
- All state variables should be normalized to 0..1 range.
- Include at least one observable that summarizes the system health or cohesion.
- Rules must use valid Python expressions with: self, params, globals, signals, sum_influence, clip, math.
- Edge weights should sum to ≤ 1.0 per target node.
- Always include model: section with name and steps fields.

CyberDSL format:
model:
  name = "..."
  steps = <int>

globals:
  key = <float>

nodes:
  id:type | state={var:val, ...} | param=val

edges:
  src->dst:relation | weight=<float> | delay=<int>

rules:
  node.var => <python expression>

observables:
  name = <python expression using nodes dict>
""".strip()


class CommunityDSLTranslator:
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.2,
    ):
        self.model = model
        self.api_base = api_base
        self.api_key = api_key
        self.temperature = temperature

    def translate(
        self,
        description: str,
        schema_hint: Optional[dict[str, Any]] = None,
        examples: Optional[list[dict[str, str]]] = None,
    ) -> str:
        """
        Translate a natural-language description into CyberDSL text.

        Args:
            description: Free-form description of the social system.
            schema_hint:  Optional dict with expected node ids, global keys, etc.
            examples:     Few-shot examples as list of {description, dsl} dicts.

        Returns:
            CyberDSL source text (not yet parsed).
        """
        try:
            from litellm import completion  # type: ignore
        except ImportError as exc:
            raise RuntimeError("litellm is required: pip install litellm") from exc

        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Few-shot examples
        if examples:
            for ex in examples:
                messages.append({"role": "user", "content": ex["description"]})
                messages.append({"role": "assistant", "content": ex["dsl"]})

        user_content = description
        if schema_hint:
            user_content += "\n\nSchema hint:\n" + json.dumps(schema_hint, ensure_ascii=False, indent=2)

        messages.append({"role": "user", "content": user_content})

        kwargs: dict[str, Any] = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": messages,
        }
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.api_key:
            kwargs["api_key"] = self.api_key

        response = completion(**kwargs)
        raw = response.choices[0].message.content.strip()

        # Strip accidental markdown fences
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(
                line for line in lines
                if not line.strip().startswith("```")
            )
        return raw.strip()

    def translate_and_compile(self, description: str, **kwargs) -> Any:
        """Convenience: translate → parse → return ModelDef."""
        from .models import ModelCompiler
        dsl = self.translate(description, **kwargs)
        return ModelCompiler().parse(dsl), dsl
