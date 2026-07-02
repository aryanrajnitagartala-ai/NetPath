"""
Measures real performance of routing algorithms on a synthetic 3-tier
enterprise topology (106 nodes: 4 core + 12 distribution + 90 access,
matching the topology_generator defaults).
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.topology_generator import generate_hierarchical_topology
from core.algorithms import dijkstra_shortest_path, kruskal_mst, find_articulation_points, simulate_link_failure


def benchmark():
    g = generate_hierarchical_topology()
    print(f"Topology: {g.node_count()} nodes, {g.edge_count()} edges")

    # Dijkstra: average over 200 random source/target pairs
    rng = random.Random(1)
    nodes = list(g.nodes)
    times = []
    for _ in range(200):
        src, tgt = rng.sample(nodes, 2)
        t0 = time.perf_counter()
        path, dist = dijkstra_shortest_path(g, src, tgt)
        times.append(time.perf_counter() - t0)
    avg_ms = (sum(times) / len(times)) * 1000
    print(f"Dijkstra shortest path: avg {avg_ms:.3f} ms over 200 queries (206 nodes graph)")

    # MST
    t0 = time.perf_counter()
    mst_edges, total_cost = kruskal_mst(g)
    mst_ms = (time.perf_counter() - t0) * 1000
    print(f"Kruskal MST: {mst_ms:.3f} ms, {len(mst_edges)} edges, total cost {total_cost:.1f}")

    # Articulation points
    t0 = time.perf_counter()
    aps = find_articulation_points(g)
    ap_ms = (time.perf_counter() - t0) * 1000
    print(f"Articulation point detection: {ap_ms:.3f} ms, found {len(aps)} single points of failure")

    # Resilience simulation: remove each articulation point, measure impact
    if aps:
        sample_ap = aps[0]
        unreachable = simulate_link_failure(g, sample_ap)
        print(f"Failure simulation (removing '{sample_ap}'): {len(unreachable)} nodes become unreachable")

    return {
        "nodes": g.node_count(),
        "edges": g.edge_count(),
        "dijkstra_avg_ms": round(avg_ms, 3),
        "mst_ms": round(mst_ms, 3),
        "articulation_ms": round(ap_ms, 3),
        "articulation_points_found": len(aps),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("NetPath Performance Benchmark")
    print("=" * 60)
    results = benchmark()
    print("=" * 60)
    print(results)
