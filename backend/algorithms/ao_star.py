"""
AO* Search Algorithm
======================
Searches AND-OR graphs. Used when reaching the goal requires satisfying
multiple sub-goals (OR = choose one path, AND = must complete all sub-goals).

In disaster evacuation:
- AND nodes: must evacuate ALL groups (family members, injured, etc.)
- OR nodes: can choose any available safe route

This implementation models multi-shelter planning where all required
zones must be reached (AND) or the best of several alternatives (OR).
"""

import math
import time
import tracemalloc
from collections import defaultdict


def euclidean_dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


def ao_star(graph, start, goal_groups, node_positions, risk_factors):
    """
    AO* for multi-goal evacuation planning.
    
    goal_groups: list of goal sets. Each group is an AND requirement.
    Example: [{'shelter_A', 'shelter_B'}, {'medical_center'}]
    Means: must reach shelter_A OR shelter_B, AND must reach medical_center.
    
    Args:
        graph: adjacency list {node: [(neighbor, cost, risk), ...]}
        start: start node
        goal_groups: list of sets, each containing acceptable goals for that group
        node_positions: {node: (x, y)}
        risk_factors: {node: float}
    
    Returns:
        dict with paths (one per group), total_cost, nodes_explored, time_ms
    """
    start_time = time.perf_counter()
    tracemalloc.start()
    
    nodes_explored = 0
    all_paths = []
    total_cost = 0
    all_found = True

    # For each AND-required group, find best OR-path using A*-like approach
    for group_idx, goal_set in enumerate(goal_groups):
        result = _ao_star_single(graph, start, goal_set, node_positions, risk_factors)
        nodes_explored += result["nodes_explored"]
        
        if result["found"]:
            all_paths.append({
                "group": group_idx,
                "goals": list(goal_set),
                "path": result["path"],
                "cost": result["cost"]
            })
            total_cost += result["cost"]
        else:
            all_found = False
            all_paths.append({
                "group": group_idx,
                "goals": list(goal_set),
                "path": [],
                "cost": float('inf')
            })

    elapsed = (time.perf_counter() - start_time) * 1000
    _, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # For frontend compatibility, return the best single path
    best_path = []
    best_cost = float('inf')
    if all_paths and all_paths[0]["path"]:
        best_path = all_paths[0]["path"]
        best_cost = all_paths[0]["cost"]

    return {
        "algorithm": "AO* Search",
        "path": best_path,
        "cost": best_cost,
        "total_cost": total_cost,
        "group_paths": all_paths,
        "nodes_explored": nodes_explored,
        "time_ms": round(elapsed, 4),
        "memory_kb": round(mem_peak / 1024, 2),
        "found": all_found,
        "num_groups": len(goal_groups)
    }


def _ao_star_single(graph, start, goals, node_positions, risk_factors):
    """Internal A*-like search for a single OR-group."""
    import heapq
    
    goals = set(goals)
    g_cost = {start: 0}
    
    def h(node):
        if node not in node_positions:
            return float('inf')
        pos = node_positions[node]
        dists = [
            euclidean_dist(pos, node_positions[g])
            for g in goals if g in node_positions
        ]
        return min(dists) if dists else float('inf')

    counter = 0
    heap = [(h(start), counter, start, [start])]
    visited = set()
    nodes_explored = 0

    while heap:
        f, _, current, path = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        nodes_explored += 1

        if current in goals:
            return {"path": path, "cost": g_cost[current], "nodes_explored": nodes_explored, "found": True}

        for neighbor, cost, risk in graph.get(current, []):
            if neighbor not in visited:
                new_g = g_cost[current] + cost + risk * 2
                if neighbor not in g_cost or new_g < g_cost[neighbor]:
                    g_cost[neighbor] = new_g
                    counter += 1
                    heapq.heappush(heap, (new_g + h(neighbor), counter, neighbor, path + [neighbor]))

    return {"path": [], "cost": float('inf'), "nodes_explored": nodes_explored, "found": False}
