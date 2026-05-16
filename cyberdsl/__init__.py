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

from .models import ModelCompiler, Simulation, SimulationResult, MonteCarloResult, run_monte_carlo
from .parser import ModelDef, NodeDef, EdgeDef, RuleDef, parse_dsl, parse_yaml, dsl_to_yaml
from .litellm_adapter import CommunityDSLTranslator
from .dashboard import build_dashboard, save_dashboard
from .graph import model_to_mermaid, build_graph_viewer, save_mermaid, save_graph_viewer

__all__ = [
    "ModelCompiler",
    "Simulation",
    "SimulationResult",
    "MonteCarloResult",
    "run_monte_carlo",
    "ModelDef",
    "NodeDef",
    "EdgeDef",
    "RuleDef",
    "parse_dsl",
    "parse_yaml",
    "dsl_to_yaml",
    "CommunityDSLTranslator",
    "build_dashboard",
    "save_dashboard",
    "model_to_mermaid",
    "build_graph_viewer",
    "save_mermaid",
    "save_graph_viewer",
]

__version__ = "0.2.2"
