"""
CyberDSL Web App — aiohttp server.

Endpoints:
  GET  /                     → index.html
  GET  /static/<file>        → static assets
  POST /api/parse            → parse DSL/YAML, return model metadata
  POST /api/simulate         → run full simulation, return timeline JSON
  POST /api/simulate/stream  → SSE: step-by-step simulation stream
  POST /api/mermaid          → return Mermaid source for model
  POST /api/examples         → list built-in example files
  GET  /api/examples         → list built-in example files
  GET  /api/examples/<name>  → return content of example file

Usage:
    python -m cyberdsl serve [--host 0.0.0.0] [--port 8080]
"""
from __future__ import annotations

import asyncio
import json
import logging
import pathlib
import traceback
from typing import Any

from aiohttp import web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("cyberdsl.webapp")

from .parser import parse_dsl, parse_yaml
from .models import ModelCompiler, Simulation
from .graph import model_to_mermaid

STATIC_DIR = pathlib.Path(__file__).parent / "static"
EXAMPLES_DIRS = [
    pathlib.Path(__file__).parent.parent / "examples" / "port",
    pathlib.Path(__file__).parent.parent / "examples" / "family",
    pathlib.Path(__file__).parent.parent / "examples" / "institutional",
    pathlib.Path(__file__).parent.parent / "examples" / "crisis",
    pathlib.Path(__file__).parent.parent / "examples",
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _parse_model(text: str, fmt: str):
    """Parse DSL or YAML text, return ModelDef."""
    if fmt == "yaml":
        return parse_yaml(text)
    model = ModelCompiler().parse(text)
    return model


def _model_meta(model) -> dict:
    return {
        "name": model.name,
        "steps": model.steps,
        "nodes": {
            nid: {"kind": n.kind, "state": n.state, "params": n.params}
            for nid, n in model.nodes.items()
        },
        "edges": [
            {"src": e.src, "dst": e.dst, "relation": e.relation,
             "weight": e.weight, "delay": e.delay}
            for e in model.edges
        ],
        "globals": model.globals,
        "rules_count": len(model.rules),
        "observables": list(model.observables.keys()),
    }


def _snap_to_json(snap: dict) -> dict:
    """Convert a timeline snapshot to JSON-serialisable dict."""
    return {
        "step": snap["step"],
        "nodes": {
            nid: {k: round(float(v), 6) for k, v in state.items()}
            for nid, state in snap["nodes"].items()
        },
        "observables": {
            k: round(float(v), 6) if isinstance(v, float) else v
            for k, v in snap.get("observables", {}).items()
        },
        "globals": {k: round(float(v), 6) for k, v in snap.get("globals", {}).items()},
    }


def _find_example(name: str) -> pathlib.Path | None:
    for d in EXAMPLES_DIRS:
        p = d / name
        if p.exists():
            return p
    return None


def _list_examples() -> list[dict]:
    seen = set()
    out = []
    for d in EXAMPLES_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if f.suffix in (".yaml", ".yml", ".cyberdsl") and f.name not in seen:
                seen.add(f.name)
                out.append({
                    "name": f.name,
                    "fmt": "yaml" if f.suffix in (".yaml", ".yml") else "dsl",
                    "size": f.stat().st_size,
                    "category": d.name,
                })
    return out


# ─── Route handlers ───────────────────────────────────────────────────────────

async def handle_favicon(request: web.Request) -> web.Response:
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
           '<rect width="32" height="32" rx="6" fill="#161b22"/>'
           '<text x="16" y="22" font-size="18" text-anchor="middle" fill="#58a6ff">⬡</text>'
           '</svg>')
    return web.Response(body=svg.encode(), content_type="image/svg+xml")


async def handle_index(request: web.Request) -> web.Response:
    index = STATIC_DIR / "index.html"
    return web.Response(text=index.read_text(encoding="utf-8"), content_type="text/html")


async def handle_static(request: web.Request) -> web.Response:
    filename = request.match_info["filename"]
    path = STATIC_DIR / filename
    if not path.exists() or not path.is_file():
        raise web.HTTPNotFound()
    ct = "text/javascript" if filename.endswith(".js") else "text/css"
    return web.Response(text=path.read_text(encoding="utf-8"), content_type=ct)


async def handle_parse(request: web.Request) -> web.Response:
    try:
        body = await request.json()
        text = body.get("text", "").strip()
        fmt = body.get("fmt", "dsl")
        if not text:
            return web.json_response({"ok": False, "error": "Empty model text"}, status=400)
        model = _parse_model(text, fmt)
        log.info("PARSE ok  model=%s nodes=%d", model.name, len(model.nodes))
        return web.json_response({"ok": True, "model": _model_meta(model)})
    except Exception as e:
        log.warning("PARSE err %s", e)
        return web.json_response({"ok": False, "error": str(e)}, status=400)


async def handle_simulate(request: web.Request) -> web.Response:
    try:
        body = await request.json()
        text = body.get("text", "").strip()
        fmt = body.get("fmt", "dsl")
        steps = body.get("steps") or None
        if not text:
            return web.json_response({"ok": False, "error": "Empty model text"}, status=400)
        model = _parse_model(text, fmt)
        result = Simulation(model).run(steps=steps)
        timeline = [_snap_to_json(s) for s in result.timeline]
        log.info("SIMULATE ok  model=%s steps=%d", model.name, result.steps_run)
        return web.json_response({
            "ok": True,
            "model_name": result.model_name,
            "steps_run": result.steps_run,
            "timeline": timeline,
            "mermaid": model_to_mermaid(model),
            "model": _model_meta(model),
        })
    except Exception as e:
        log.error("SIMULATE err %s\n%s", e, traceback.format_exc())
        return web.json_response({"ok": False, "error": str(e),
                                  "trace": traceback.format_exc()}, status=400)


async def handle_simulate_stream(request: web.Request) -> web.StreamResponse:
    """SSE endpoint: sends one JSON event per simulation step."""
    try:
        body = await request.json()
        text = body.get("text", "").strip()
        fmt = body.get("fmt", "dsl")
        steps = body.get("steps") or None
        if not text:
            return web.Response(text=json.dumps({"ok": False, "error": "Empty model text"}),
                                content_type="application/json", status=400)
        model = _parse_model(text, fmt)
    except Exception as e:
        log.warning("STREAM parse err %s", e)
        return web.Response(text=json.dumps({"ok": False, "error": str(e)}),
                            content_type="application/json", status=400)

    response = web.StreamResponse(headers={
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })
    await response.prepare(request)

    sim = Simulation(model)
    n_steps = steps if steps is not None else model.steps

    log.info("STREAM start  model=%s steps=%d", model.name, n_steps)
    meta_event = json.dumps({"type": "meta", "model": _model_meta(model),
                              "mermaid": model_to_mermaid(model)})
    await response.write(f"data: {meta_event}\n\n".encode())

    for i in range(1, n_steps + 1):
        snap = sim.step(i)
        event = json.dumps({"type": "step", "data": _snap_to_json(snap)})
        await response.write(f"data: {event}\n\n".encode())
        await asyncio.sleep(0)

    done_event = json.dumps({"type": "done", "steps_run": n_steps})
    await response.write(f"data: {done_event}\n\n".encode())
    log.info("STREAM done   model=%s steps=%d", model.name, n_steps)
    return response


async def handle_mermaid(request: web.Request) -> web.Response:
    try:
        body = await request.json()
        text = body.get("text", "").strip()
        fmt = body.get("fmt", "dsl")
        direction = body.get("direction", "TD")
        if not text:
            return web.json_response({"ok": False, "error": "Empty model text"}, status=400)
        model = _parse_model(text, fmt)
        mmd = model_to_mermaid(model, direction=direction)
        log.info("MERMAID ok  model=%s dir=%s", model.name, direction)
        return web.json_response({"ok": True, "mermaid": mmd})
    except Exception as e:
        log.warning("MERMAID err %s", e)
        return web.json_response({"ok": False, "error": str(e)}, status=400)


async def handle_list_examples(request: web.Request) -> web.Response:
    return web.json_response({"ok": True, "examples": _list_examples()})


async def handle_get_example(request: web.Request) -> web.Response:
    name = request.match_info["name"]
    path = _find_example(name)
    if path is None:
        log.warning("EXAMPLE not found: %s", name)
        return web.json_response({"ok": False, "error": f"Not found: {name}"}, status=404)
    fmt = "yaml" if path.suffix in (".yaml", ".yml") else "dsl"
    log.info("EXAMPLE load  %s  fmt=%s", name, fmt)
    return web.json_response({
        "ok": True,
        "name": name,
        "fmt": fmt,
        "text": path.read_text(encoding="utf-8"),
    })


# ─── App factory ──────────────────────────────────────────────────────────────

@web.middleware
async def access_log_middleware(request: web.Request, handler):
    resp = await handler(request)
    log.info("%s %s → %d", request.method, request.path, resp.status)
    return resp


def create_app() -> web.Application:
    app = web.Application(middlewares=[access_log_middleware])
    app.router.add_get("/favicon.ico", handle_favicon)
    app.router.add_get("/", handle_index)
    app.router.add_get("/static/{filename}", handle_static)
    app.router.add_post("/api/parse", handle_parse)
    app.router.add_post("/api/simulate", handle_simulate)
    app.router.add_post("/api/simulate/stream", handle_simulate_stream)
    app.router.add_post("/api/mermaid", handle_mermaid)
    app.router.add_get("/api/examples", handle_list_examples)
    app.router.add_get("/api/examples/{name}", handle_get_example)
    return app


def run(host: str = "127.0.0.1", port: int = 8080) -> None:
    app = create_app()
    log.info("CyberDSL Web App → http://%s:%d", host, port)
    web.run_app(app, host=host, port=port, print=None)
