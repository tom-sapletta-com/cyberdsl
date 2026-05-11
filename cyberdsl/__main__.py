"""
CyberDSL CLI — python -m cyberdsl <command> [options]

Commands:
  simulate   Run simulation, print summary.
  dashboard  Run simulation and save an HTML dashboard.
  csv        Run simulation and export timeline as CSV.
  monte      Run Monte Carlo analysis and save HTML dashboard with bands.
  translate  Translate natural-language description to DSL (requires LiteLLM key).
"""
from __future__ import annotations

import argparse
import sys


def _load_model(path: str):
    text = open(path, encoding='utf-8').read()
    if path.endswith(('.yaml', '.yml')):
        from cyberdsl.parser import parse_yaml
        return parse_yaml(text)
    from cyberdsl.models import ModelCompiler
    return ModelCompiler().parse(text)


def cmd_simulate(args):
    model = _load_model(args.model)
    from cyberdsl.models import Simulation
    sim = Simulation(model)
    result = sim.run(steps=args.steps or None)
    print(result.summary())


def cmd_dashboard(args):
    model = _load_model(args.model)
    from cyberdsl.models import Simulation
    from cyberdsl.dashboard import save_dashboard
    sim = Simulation(model)
    result = sim.run(steps=args.steps or None)
    out = args.output or (args.model.rsplit('.', 1)[0] + '_dashboard.html')
    save_dashboard(result, out, model=model)
    print(f"Dashboard saved → {out}")
    print(result.summary())


def cmd_csv(args):
    model = _load_model(args.model)
    from cyberdsl.models import Simulation
    sim = Simulation(model)
    result = sim.run(steps=args.steps or None)
    out = args.output or (args.model.rsplit('.', 1)[0] + '_timeline.csv')
    result.save_csv(out)
    print(f"CSV saved → {out}")
    print(result.summary())


def cmd_monte(args):
    model = _load_model(args.model)
    from cyberdsl.models import Simulation, run_monte_carlo
    from cyberdsl.dashboard import save_dashboard

    mc = run_monte_carlo(
        model,
        n_runs=args.runs,
        steps=args.steps or None,
        noise_std=args.noise,
        seed=args.seed,
    )
    baseline_model = _load_model(args.model)
    result = Simulation(baseline_model).run(steps=args.steps or None)

    out = args.output or (args.model.rsplit('.', 1)[0] + '_monte.html')
    save_dashboard(result, out, mc=mc, model=baseline_model)
    print(f"Monte Carlo dashboard saved → {out}")
    print(f"Runs: {args.runs}, noise_std: {args.noise}")
    print(result.summary())


def cmd_serve(args):
    from cyberdsl.webapp import run
    run(host=args.host, port=args.port)


def cmd_visualize(args):
    model = _load_model(args.model)
    from cyberdsl.graph import save_mermaid, save_graph_viewer
    base = args.model.rsplit('.', 1)[0]
    # .mmd file
    mmd_out = args.mmd_output or (base + '.mmd')
    save_mermaid(model, mmd_out, direction=args.direction)
    print(f"Mermaid saved → {mmd_out}")
    # HTML viewer
    html_out = args.output or (base + '_graph.html')
    src = open(args.model, encoding='utf-8').read()
    save_graph_viewer(model, html_out, yaml_source=src)
    print(f"Graph viewer saved → {html_out}")


def cmd_translate(args):
    from cyberdsl.litellm_adapter import CommunityDSLTranslator
    if not args.api_key:
        print("ERROR: --api-key required for translate command", file=sys.stderr)
        sys.exit(1)
    text = open(args.description, encoding='utf-8').read()
    t = CommunityDSLTranslator(model=args.llm_model, api_key=args.api_key)
    dsl = t.translate(text)
    out = args.output or args.description.rsplit('.', 1)[0] + '.cyberdsl'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(dsl)
    print(f"DSL saved → {out}")
    print(dsl[:800])


def main():
    parser = argparse.ArgumentParser(
        prog='cyberdsl',
        description='CyberDSL — cybernetic social-system simulator',
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # simulate
    p = sub.add_parser('simulate', help='Run simulation and print summary')
    p.add_argument('model', help='Path to .cyberdsl file')
    p.add_argument('--steps', type=int, default=0, help='Override number of steps')
    p.set_defaults(func=cmd_simulate)

    # dashboard
    p = sub.add_parser('dashboard', help='Run simulation and save HTML dashboard')
    p.add_argument('model', help='Path to .cyberdsl file')
    p.add_argument('--steps', type=int, default=0)
    p.add_argument('--output', '-o', help='Output .html path')
    p.set_defaults(func=cmd_dashboard)

    # csv
    p = sub.add_parser('csv', help='Run simulation and export CSV timeline')
    p.add_argument('model', help='Path to .cyberdsl file')
    p.add_argument('--steps', type=int, default=0)
    p.add_argument('--output', '-o', help='Output .csv path')
    p.set_defaults(func=cmd_csv)

    # monte
    p = sub.add_parser('monte', help='Monte Carlo analysis with HTML dashboard')
    p.add_argument('model', help='Path to .cyberdsl file')
    p.add_argument('--runs', type=int, default=200, help='Number of MC runs (default: 200)')
    p.add_argument('--steps', type=int, default=0)
    p.add_argument('--noise', type=float, default=0.02, help='Gaussian noise std-dev (default: 0.02)')
    p.add_argument('--seed', type=int, default=None)
    p.add_argument('--output', '-o', help='Output .html path')
    p.set_defaults(func=cmd_monte)

    # serve
    p = sub.add_parser('serve', help='Start the CyberDSL web app (browser UI)')
    p.add_argument('--host', default='127.0.0.1', help='Bind host (default: 127.0.0.1)')
    p.add_argument('--port', type=int, default=8080, help='Port (default: 8080)')
    p.set_defaults(func=cmd_serve)

    # visualize
    p = sub.add_parser('visualize', help='Generate Mermaid graph + HTML viewer for a model')
    p.add_argument('model', help='Path to .cyberdsl or .yaml model file')
    p.add_argument('--direction', '-d', default='TD', choices=['TD', 'LR', 'BT', 'RL'],
                   help='Mermaid graph direction (default: TD)')
    p.add_argument('--output', '-o', help='Output .html path for graph viewer')
    p.add_argument('--mmd-output', help='Output .mmd path for Mermaid source')
    p.set_defaults(func=cmd_visualize)

    # translate
    p = sub.add_parser('translate', help='Translate natural language to DSL via LiteLLM')
    p.add_argument('description', help='Path to .txt description file')
    p.add_argument('--llm-model', default='openai/gpt-4o-mini')
    p.add_argument('--api-key', default=None)
    p.add_argument('--output', '-o', help='Output .cyberdsl path')
    p.set_defaults(func=cmd_translate)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
