"""
Generates realistic synthetic network topologies for testing/benchmarking:
a core-distribution-access hierarchy similar to real enterprise/ISP networks
(this is the standard 3-tier topology Cisco documentation itself uses).
"""

import random
from .graph import Graph


def generate_hierarchical_topology(
    core_count: int = 4,
    dist_count: int = 12,
    access_count: int = 90,
    seed: int = 42,
) -> Graph:
    """
    Build a 3-tier core/distribution/access topology with redundant links
    at the core and distribution layers (matches real enterprise network design).
    """
    rng = random.Random(seed)
    g = Graph()

    core_nodes = [f"core-{i}" for i in range(core_count)]
    dist_nodes = [f"dist-{i}" for i in range(dist_count)]
    access_nodes = [f"access-{i}" for i in range(access_count)]

    for n in core_nodes + dist_nodes + access_nodes:
        g.add_node(n)

    # Full mesh at core (redundant backbone)
    for i in range(core_count):
        for j in range(i + 1, core_count):
            g.add_edge(
                core_nodes[i], core_nodes[j],
                latency_ms=rng.uniform(1, 3),
                bandwidth_mbps=100000,
                cost=rng.uniform(50, 100),
            )

    # Each distribution node connects to 2 core nodes (redundancy)
    for d in dist_nodes:
        chosen = rng.sample(core_nodes, k=min(2, core_count))
        for c in chosen:
            g.add_edge(
                d, c,
                latency_ms=rng.uniform(2, 6),
                bandwidth_mbps=10000,
                cost=rng.uniform(20, 40),
            )

    # Each access node connects to 1-2 distribution nodes
    for a in access_nodes:
        k = 1 if rng.random() < 0.7 else 2  # 30% have redundant uplinks
        chosen = rng.sample(dist_nodes, k=min(k, dist_count))
        for d in chosen:
            g.add_edge(
                a, d,
                latency_ms=rng.uniform(3, 10),
                bandwidth_mbps=1000,
                cost=rng.uniform(5, 15),
            )

    return g
