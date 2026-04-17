"""
Best-First Search (Greedy Best-First)
=======================================
Uses a priority queue ordered by heuristic value h(n).
Greedy: picks the node that looks closest to the goal.
Not optimal but usually fast. Heuristic = Euclidean distance + risk penalty.
Time: O(V log V), Space: O(V)
"""

import heapq
import math
import time
import tracemalloc


def euclidean_distance(pos1, pos2):
    """Calculate Euclidean distance between two (x,y) positions."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def heuristic(node, goals, node_positions, risk_factors, risk_weight=1.0):
    """
    Composite heuristic: min distance to any goal + risk penalty.
    
    Args:
        node: current node id
        goals: set of goal node ids
        node_positions: dict {node_id: (x, y)}
        risk_factors: dict {node_id: float 0-1}
        risk_weight: multiplier for risk penalty
    """
    if node not in node_positions:
        return float('inf')
    
    pos = node_positions[node]
    min_dist = min(
        euclidean_distance(pos, node_positions[g])
        for g in goals if g in node_positions
    ) if goals else float('inf')
    
    risk_penalty = risk_factors.get(node, 0) * risk_weight * 10
    return min_dist + risk_penalty


def best_first_search(graph, start, goals, node_positions, risk_factors, risk_weight=1.0):
    """
    Greedy Best-First Search for evacuation.
    
    Args:
        graph: adjacency list {node: [(neighbor, cost, risk), ...]}
        start: start node
        goals: list of safe zones
        node_positions: {node: (x, y)} for heuristic
        risk_factors: {node: float} risk level 0.0-1.0
        risk_weight: weight for risk in heuristic
    
    Returns:
        dict with path, cost, nodes_explored, time_ms, memory_kb
    """
    start_time = time.perf_counter()
    tracemalloc.start()

    goals = set(goals)
    h_start = heuristic(start, goals, node_positions, risk_factors, risk_weight)
    
    # heap: (h_value, node, path, cost)
    heap = [(h_start, start, [start], 0)]
    visited = set()
    nodes_explored = 0

    while heap:
        h_val, current, path, cost = heapq.heappop(heap)

        if current in visited:
            continue
        visited.add(current)
        nodes_explored += 1

        if current in goals:
            elapsed = (time.perf_counter() - start_time) * 1000
            _, mem_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return {
                "algorithm": "Best-First Search",
                "path": path,
                "cost": cost,
                "nodes_explored": nodes_explored,
                "time_ms": round(elapsed, 4),
                "memory_kb": round(mem_peak / 1024, 2),
                "found": True
            }

        for neighbor, edge_cost, risk in graph.get(current, []):
            if neighbor not in visited:
                h = heuristic(neighbor, goals, node_positions, risk_factors, risk_weight)
                heapq.heappush(heap, (h, neighbor, path + [neighbor], cost + edge_cost))

    elapsed = (time.perf_counter() - start_time) * 1000
    _, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "algorithm": "Best-First Search",
        "path": [],
        "cost": float('inf'),
        "nodes_explored": nodes_explored,
        "time_ms": round(elapsed, 4),
        "memory_kb": round(mem_peak / 1024, 2),
        "found": False
    }
