"""
NetPath REST API - network routing and resilience analysis service.
Run locally with: uv run uvicorn api.service:app --reload
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

from core.graph import Graph
from core.algorithms import dijkstra_shortest_path, kruskal_mst, find_articulation_points, simulate_link_failure
from core.topology_generator import generate_hierarchical_topology

app = FastAPI(title="NetPath - Network Topology Optimizer")

# In-memory topology (regenerated on startup; POST /topology to load a custom one)
STATE = {"graph": generate_hierarchical_topology()}


class EdgeIn(BaseModel):
    a: str
    b: str
    latency_ms: float
    bandwidth_mbps: float
    cost: float


class TopologyIn(BaseModel):
    edges: List[EdgeIn]


class PathRequest(BaseModel):
    source: str
    target: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/topology")
def get_topology():
    g = STATE["graph"]
    edges = [
        {"a": u, "b": v, "latency_ms": round(lat, 2), "bandwidth_mbps": bw, "cost": round(c, 2)}
        for u, v, lat, bw, c in g.edge_list()
    ]
    return {"node_count": g.node_count(), "edge_count": g.edge_count(), "edges": edges, "nodes": sorted(g.nodes)}


@app.post("/topology")
def set_topology(payload: TopologyIn):
    g = Graph()
    for e in payload.edges:
        g.add_edge(e.a, e.b, e.latency_ms, e.bandwidth_mbps, e.cost)
    STATE["graph"] = g
    return {"node_count": g.node_count(), "edge_count": g.edge_count()}


@app.post("/route")
def route(req: PathRequest):
    g = STATE["graph"]
    if req.source not in g.nodes or req.target not in g.nodes:
        raise HTTPException(status_code=404, detail="Unknown node id")
    path, latency = dijkstra_shortest_path(g, req.source, req.target)
    if path is None:
        raise HTTPException(status_code=404, detail="No path exists between nodes")
    return {"path": path, "total_latency_ms": round(latency, 3), "hops": len(path) - 1}


@app.get("/backbone")
def backbone():
    g = STATE["graph"]
    edges, total_cost = kruskal_mst(g)
    return {
        "edges": [{"a": u, "b": v, "cost": round(c, 2)} for u, v, c in edges],
        "total_cost": round(total_cost, 2),
        "edge_count": len(edges),
    }


@app.get("/resilience")
def resilience():
    g = STATE["graph"]
    aps = find_articulation_points(g)
    details = []
    for node in aps:
        unreachable = simulate_link_failure(g, node)
        details.append({"node": node, "nodes_isolated_if_removed": len(unreachable), "isolated": unreachable[:20]})
    return {"single_points_of_failure": aps, "count": len(aps), "impact": details}


static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    def index():
        return FileResponse(str(static_dir / "index.html"))
