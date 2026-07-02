"""
Weighted, undirected graph representation for network topology modeling.
Nodes represent network devices (routers/switches); edges represent links
with bandwidth (Mbps), latency (ms), and cost attributes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Edge:
    to: str
    latency_ms: float
    bandwidth_mbps: float
    cost: float


class Graph:
    """Adjacency-list weighted graph."""

    def __init__(self):
        self.nodes: set[str] = set()
        self.adj: Dict[str, List[Edge]] = {}

    def add_node(self, node_id: str) -> None:
        if node_id not in self.nodes:
            self.nodes.add(node_id)
            self.adj[node_id] = []

    def add_edge(self, a: str, b: str, latency_ms: float, bandwidth_mbps: float, cost: float) -> None:
        self.add_node(a)
        self.add_node(b)
        self.adj[a].append(Edge(b, latency_ms, bandwidth_mbps, cost))
        self.adj[b].append(Edge(a, latency_ms, bandwidth_mbps, cost))

    def neighbors(self, node_id: str) -> List[Edge]:
        return self.adj.get(node_id, [])

    def edge_list(self) -> List[Tuple[str, str, float, float, float]]:
        """Return each undirected edge once as (u, v, latency, bandwidth, cost)."""
        seen = set()
        result = []
        for u in self.adj:
            for e in self.adj[u]:
                key = tuple(sorted((u, e.to)))
                if key not in seen:
                    seen.add(key)
                    result.append((u, e.to, e.latency_ms, e.bandwidth_mbps, e.cost))
        return result

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edge_list())
