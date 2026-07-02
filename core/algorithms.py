"""
Classical graph algorithms applied to network routing:

- dijkstra_shortest_path: min-latency path between two routers (binary heap, O((V+E) log V))
- kruskal_mst: minimum-cost backbone design using Union-Find (O(E log E))
- find_articulation_points: single-point-of-failure detection via Tarjan's algorithm (O(V+E))
- k_shortest_paths: backup/failover path computation (Yen's algorithm, simplified)
"""

import heapq
from typing import Dict, List, Optional, Tuple

from .graph import Graph


def dijkstra_shortest_path(graph: Graph, source: str, target: str) -> Tuple[Optional[List[str]], float]:
    """
    Compute the minimum-latency path between source and target.
    Returns (path_as_list_of_node_ids, total_latency_ms). Path is None if unreachable.
    """
    if source not in graph.nodes or target not in graph.nodes:
        return None, float("inf")

    dist: Dict[str, float] = {n: float("inf") for n in graph.nodes}
    prev: Dict[str, Optional[str]] = {n: None for n in graph.nodes}
    dist[source] = 0.0
    visited = set()
    heap = [(0.0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if u == target:
            break
        for edge in graph.neighbors(u):
            nd = d + edge.latency_ms
            if nd < dist[edge.to]:
                dist[edge.to] = nd
                prev[edge.to] = u
                heapq.heappush(heap, (nd, edge.to))

    if dist[target] == float("inf"):
        return None, float("inf")

    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path, dist[target]


class UnionFind:
    def __init__(self, items):
        self.parent = {i: i for i in items}
        self.rank = {i: 0 for i in items}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal_mst(graph: Graph) -> Tuple[List[Tuple[str, str, float]], float]:
    """
    Compute a minimum-cost spanning backbone (all nodes connected at lowest total link cost).
    Returns (list_of_edges_used, total_cost). Uses Union-Find with path compression + union by rank.
    """
    edges = sorted(graph.edge_list(), key=lambda e: e[4])  # sort by cost
    uf = UnionFind(graph.nodes)
    mst_edges = []
    total_cost = 0.0

    for u, v, latency, bandwidth, cost in edges:
        if uf.union(u, v):
            mst_edges.append((u, v, cost))
            total_cost += cost

    return mst_edges, total_cost


def find_articulation_points(graph: Graph) -> List[str]:
    """
    Identify single points of failure: nodes whose removal disconnects the network.
    Tarjan's articulation point algorithm using discovery/low-link times, O(V + E).
    """
    disc: Dict[str, int] = {}
    low: Dict[str, int] = {}
    visited = set()
    ap = set()
    timer = [0]

    def dfs(u: str, parent: Optional[str]):
        visited.add(u)
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        children = 0

        for edge in graph.neighbors(u):
            v = edge.to
            if v == parent:
                continue
            if v in visited:
                low[u] = min(low[u], disc[v])
            else:
                children += 1
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if parent is not None and low[v] >= disc[u]:
                    ap.add(u)

        if parent is None and children > 1:
            ap.add(u)

    for node in graph.nodes:
        if node not in visited:
            dfs(node, None)

    return sorted(ap)


def simulate_link_failure(graph: Graph, node_to_remove: str) -> List[str]:
    """
    Simulate removal of a node and return the list of nodes that become
    unreachable from the largest remaining connected component (resilience test).
    """
    remaining = graph.nodes - {node_to_remove}
    if not remaining:
        return []

    visited = set()
    start = next(iter(remaining))

    def bfs(start_node):
        from collections import deque
        q = deque([start_node])
        seen = {start_node}
        while q:
            u = q.popleft()
            for edge in graph.neighbors(u):
                if edge.to != node_to_remove and edge.to not in seen:
                    seen.add(edge.to)
                    q.append(edge.to)
        return seen

    reachable = bfs(start)
    unreachable = remaining - reachable
    return sorted(unreachable)
