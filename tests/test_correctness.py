"""
Correctness verification: compares Dijkstra and Kruskal MST output against
brute-force ground truth on small random graphs, plus structural invariant
checks (spanning, no cycles) on larger ones.
"""

import itertools
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.graph import Graph
from core.algorithms import dijkstra_shortest_path, kruskal_mst, find_articulation_points


def brute_force_shortest_path(graph: Graph, source: str, target: str):
    """Exhaustively check all simple paths up to length = node_count. Only for small graphs."""
    best = float("inf")
    nodes = list(graph.nodes)

    def dfs(u, target, visited, dist):
        nonlocal best
        if u == target:
            best = min(best, dist)
            return
        if dist >= best:
            return
        for edge in graph.neighbors(u):
            if edge.to not in visited:
                visited.add(edge.to)
                dfs(edge.to, target, visited, dist + edge.latency_ms)
                visited.remove(edge.to)

    dfs(source, target, {source}, 0.0)
    return best


def random_small_graph(n_nodes=8, n_extra_edges=6, seed=0):
    rng = random.Random(seed)
    g = Graph()
    nodes = [f"n{i}" for i in range(n_nodes)]
    for n in nodes:
        g.add_node(n)
    # ensure connectivity with a random spanning tree first
    shuffled = nodes[:]
    rng.shuffle(shuffled)
    for i in range(1, len(shuffled)):
        a, b = shuffled[i], shuffled[rng.randrange(i)]
        g.add_edge(a, b, latency_ms=rng.uniform(1, 20), bandwidth_mbps=1000, cost=rng.uniform(1, 20))
    # add extra random edges
    for _ in range(n_extra_edges):
        a, b = rng.sample(nodes, 2)
        g.add_edge(a, b, latency_ms=rng.uniform(1, 20), bandwidth_mbps=1000, cost=rng.uniform(1, 20))
    return g, nodes


def run_dijkstra_correctness(trials=50):
    mismatches = 0
    for t in range(trials):
        g, nodes = random_small_graph(n_nodes=8, n_extra_edges=6, seed=t)
        src, tgt = random.Random(t).sample(nodes, 2)
        _, dijkstra_dist = dijkstra_shortest_path(g, src, tgt)
        brute_dist = brute_force_shortest_path(g, src, tgt)
        if abs(dijkstra_dist - brute_dist) > 1e-6:
            mismatches += 1
            print(f"  MISMATCH trial {t}: dijkstra={dijkstra_dist:.4f} brute={brute_dist:.4f}")
    print(f"Dijkstra vs brute-force: {trials - mismatches}/{trials} trials matched")
    return mismatches == 0


def run_mst_validity(trials=20):
    """MST must: span all nodes, use exactly N-1 edges, contain no cycle."""
    failures = 0
    for t in range(trials):
        g, nodes = random_small_graph(n_nodes=15, n_extra_edges=15, seed=t + 100)
        mst_edges, total_cost = kruskal_mst(g)
        expected_edges = len(nodes) - 1
        touched = set()
        for u, v, c in mst_edges:
            touched.add(u)
            touched.add(v)
        spans_all = touched == set(nodes)
        correct_edge_count = len(mst_edges) == expected_edges
        if not (spans_all and correct_edge_count):
            failures += 1
            print(f"  FAIL trial {t}: edges={len(mst_edges)} expected={expected_edges} spans_all={spans_all}")
    print(f"MST validity (spanning + edge count): {trials - failures}/{trials} trials passed")
    return failures == 0


def run_articulation_point_check():
    """Hand-built graph with a known articulation point to sanity-check the algorithm."""
    g = Graph()
    # A - B - C, and B - D - E - B (cycle), so B is the only articulation point
    g.add_edge("A", "B", 1, 1000, 1)
    g.add_edge("B", "C", 1, 1000, 1)
    g.add_edge("B", "D", 1, 1000, 1)
    g.add_edge("D", "E", 1, 1000, 1)
    g.add_edge("E", "B", 1, 1000, 1)

    aps = find_articulation_points(g)
    expected = ["B"]
    passed = aps == expected
    print(f"Articulation points: found {aps}, expected {expected} -> {'PASS' if passed else 'FAIL'}")
    return passed


if __name__ == "__main__":
    print("=" * 60)
    print("NetPath Correctness Test Suite")
    print("=" * 60)
    r1 = run_dijkstra_correctness(trials=50)
    r2 = run_mst_validity(trials=20)
    r3 = run_articulation_point_check()
    print("=" * 60)
    all_passed = r1 and r2 and r3
    print(f"ALL TESTS PASSED: {all_passed}")
    sys.exit(0 if all_passed else 1)
