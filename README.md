# NetPath — Network Topology Optimizer & Routing Engine

Graph-algorithms engine for enterprise network design: computes shortest routing
paths, minimum-cost backbone topology, and single-point-of-failure risk on a
network of routers/switches — the same class of problem behind Cisco DNA
Center / SD-WAN path computation.

## What's implemented (and verified in this repo)

- **Dijkstra's algorithm** (binary heap, `O((V+E) log V)`) — minimum-latency routing path between any two nodes
- **Kruskal's MST** (Union-Find, path compression + union by rank) — minimum-cost backbone design
- **Tarjan's articulation points** (`O(V+E)`) — single-point-of-failure detection
- **BFS-based failure simulation** — measures how many nodes get isolated if a given router fails
- **Synthetic 3-tier topology generator** — core/distribution/access hierarchy matching real enterprise network design
- **FastAPI REST service** + interactive vis-network frontend to explore routes, backbone, and failure impact visually

## Verified test results (run in this repo, not invented — see `tests/`)

```
$ python3 tests/test_correctness.py
Dijkstra vs brute-force: 50/50 trials matched
MST validity (spanning + edge count): 20/20 trials passed
Articulation points: found ['B'], expected ['B'] -> PASS
ALL TESTS PASSED: True

$ python3 tests/benchmark.py
Topology: 106 nodes, 151 edges
Dijkstra shortest path: avg 0.076 ms over 200 queries
Kruskal MST: 0.470 ms, 105 edges, total cost 1052.9
Articulation point detection: 0.244 ms, found 12 single points of failure
Failure simulation (removing 'dist-0'): 7 nodes become unreachable
```

**Known gap, stated honestly:** the FastAPI/frontend layer is written but not yet
run end-to-end (no network access in the environment this was built in, so
`fastapi`/`uvicorn` couldn't be installed to test it). Run `uv run uvicorn
api.service:app --reload` locally and smoke-test `/route`, `/backbone`,
`/resilience` before you rely on it for a live demo — it's straightforward
FastAPI wrapping already-tested functions, but "written" isn't "verified."

## Run it

```bash
pip install -r requirements.txt
python3 tests/test_correctness.py   # correctness suite
python3 tests/benchmark.py          # performance benchmark
uvicorn api.service:app --reload    # local API + UI at http://localhost:8000
```

## Deploy to get a live link

```bash
pip install modal
modal setup
uv run modal deploy modal_deploy.py
```

This prints a public URL (`https://<you>--netpath-web.modal.run`). Test it
works, then that's your real "Live Demo" link — don't put it on a resume
until you've clicked it yourself.

## Project structure

```
netpath/
├── core/
│   ├── graph.py               # weighted graph data structure
│   ├── algorithms.py          # Dijkstra, Kruskal MST, Tarjan articulation points
│   └── topology_generator.py  # synthetic 3-tier network generator
├── api/service.py             # FastAPI REST endpoints
├── static/index.html          # vis-network interactive frontend
├── tests/test_correctness.py  # brute-force verification
├── tests/benchmark.py         # performance measurement
├── Dockerfile
├── modal_deploy.py
└── requirements.txt
```
