"""
A* Search Algorithm
====================
Optimal informed search using f(n) = g(n) + h(n).
g(n) = actual cost from start, h(n) = heuristic estimate to goal.
With an admissible heuristic, A* is both complete and optimal.
Time: O(V log V), Space: O(V)
"""

import heapq
import math
import time
import tracemalloc


def euclidean_heuristic(node, goals, node_positions, risk_factors, risk_weight=1.0):
    """
    Admissible heuristic: Euclidean distance to nearest goal + risk penalty.
    """
    if node not in node_positions:
        return float('inf')
    
    pos = node_positions[node]
    min_dist = min(
        math.sqrt((pos[0] - node_positions[g][0])**2 + (pos[1] - node_positions[g][1])**2)
        for g in goals if g in node_positions
    ) if goals else float('inf')

    risk_penalty = risk_factors.get(node, 0) * risk_weight * 5
    return min_dist + risk_penalty


def astar(graph, start, goals, node_positions, risk_factors, heuristic_weight=1.0):
    """
    A* Search for optimal evacuation route.
    
    Weighted A*: f(n) = g(n) + w * h(n)
    w=1.0 → standard A* (optimal)
    w>1.0 → faster but suboptimal (Weighted A*)
    
    Args:
        graph: adjacency list {node: [(neighbor, cost, risk), ...]}
        start: start node
        goals: list of safe zone nodes
        node_positions: {node: (x, y)}
        risk_factors: {node: float 0-1}
        heuristic_weight: multiplier w for h(n)
    
    Returns:
        dict with path, cost, nodes_explored, time_ms, memory_kb
    """
    start_time = time.perf_counter()
    tracemalloc.start()

    goals = set(goals)
    
    g_cost = {start: 0}
    h_val = euclidean_heuristic(start, goals, node_positions, risk_factors, heuristic_weight)
    
    # heap: (f_value, tie_breaker, node, path)
    counter = 0
    heap = [(h_val, counter, start, [start])]
    visited = set()
    nodes_explored = 0

    while heap:
        f_val, _, current, path = heapq.heappop(heap)

        if current in visited:
            continue
        visited.add(current)
        nodes_explored += 1

        if current in goals:
            elapsed = (time.perf_counter() - start_time) * 1000
            _, mem_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return {
                "algorithm": "A* Search",
                "path": path,
                "cost": g_cost[current],
                "nodes_explored": nodes_explored,
                "time_ms": round(elapsed, 4),
                "memory_kb": round(mem_peak / 1024, 2),
                "found": True,
                "heuristic_weight": heuristic_weight
            }

        for neighbor, edge_cost, risk in graph.get(current, []):
            if neighbor not in visited:
                # Add risk to edge cost
                risk_adjusted_cost = edge_cost + risk * 2
                tentative_g = g_cost[current] + risk_adjusted_cost

                if neighbor not in g_cost or tentative_g < g_cost[neighbor]:
                    g_cost[neighbor] = tentative_g
                    h = euclidean_heuristic(neighbor, goals, node_positions, risk_factors)
                    f = tentative_g + heuristic_weight * h
                    counter += 1
                    heapq.heappush(heap, (f, counter, neighbor, path + [neighbor]))

    elapsed = (time.perf_counter() - start_time) * 1000
    _, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "algorithm": "A* Search",
        "path": [],
        "cost": float('inf'),
        "nodes_explored": nodes_explored,
        "time_ms": round(elapsed, 4),
        "memory_kb": round(mem_peak / 1024, 2),
        "found": False,
        "heuristic_weight": heuristic_weight
    }
