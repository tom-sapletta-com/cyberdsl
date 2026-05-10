"""
CyberDSL — Cybernetic DSL and runtime for social-system simulations.

Quick start:

    from cyberdsl import ModelCompiler, Simulation

    dsl = open('model.cyberdsl').read()
    model = ModelCompiler().parse(dsl)
    result = Simulation(model).run()
    print(result.summary())

Translacja opisu naturalnego:

    from cyberdsl import CommunityDSLTranslator, ModelCompiler, Simulation

    translator = CommunityDSLTranslator(model='openai/gpt-4o-mini', api_key='...')
    dsl = translator.translate("Społeczność portowa...")
    model = ModelCompiler().parse(dsl)
    result = Simulation(model).run(steps=24)
"""

from .models import ModelCompiler, Simulation, SimulationResult
from .parser import ModelDef, NodeDef, EdgeDef, RuleDef, parse_dsl
from .litellm_adapter import CommunityDSLTranslator

__all__ = [
    "ModelCompiler",
    "Simulation",
    "SimulationResult",
    "ModelDef",
    "NodeDef",
    "EdgeDef",
    "RuleDef",
    "parse_dsl",
    "CommunityDSLTranslator",
]

__version__ = "0.1.1"
