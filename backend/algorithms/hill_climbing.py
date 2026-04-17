"""
Hill Climbing Algorithm
========================
Local search that always moves to the best neighboring state.
Can get stuck at local optima. Used to locally optimize evacuation paths.

Variants:
- Simple Hill Climbing: first better neighbor
- Steepest Ascent: best of all neighbors
- Random Restart: restart from random node to escape local optima

In evacuation: minimizes f(n) = distance + risk + congestion
"""

import math
import random
import time
import tracemalloc


def evaluate_node(node, goals, node_positions, risk_factors, congestion):
    """
    Evaluate a node. Lower score = better.
    Score = min_distance_to_goal + risk_penalty + congestion_penalty
    """
    if node not in node_positions:
        return float('inf')
    
    pos = node_positions[node]
    min_dist = min(
        math.sqrt((pos[0] - node_positions[g][0])**2 + (pos[1] - node_positions[g][1])**2)
        for g in goals if g in node_positions
    ) if goals else float('inf')
    
    risk = risk_factors.get(node, 0) * 10
    cong = congestion.get(node, 0) * 5
    return min_dist + risk + cong


def hill_climbing(graph, start, goals, node_positions, risk_factors,
                  congestion=None, max_iterations=1000, restarts=3, mode="steepest"):
    """
    Hill Climbing for evacuation route optimization.
    
    Args:
        graph: adjacency list {node: [(neighbor, cost, risk), ...]}
        start: start node
        goals: list/set of safe zone nodes
        node_positions: {node: (x, y)}
        risk_factors: {node: float 0-1}
        congestion: {node: float 0-1}
        max_iterations: maximum steps per run
        restarts: number of random restarts
        mode: "steepest" or "simple"
    
    Returns:
        dict with path, cost, nodes_explored, time_ms, memory_kb
    """
    start_time = time.perf_counter()
    tracemalloc.start()

    goals = set(goals)
    if congestion is None:
        congestion = {}

    nodes_explored = 0
    best_global_path = []
    best_global_cost = float('inf')

    # Try multiple restarts
    for restart in range(restarts):
        current = start if restart == 0 else random.choice(list(graph.keys()))
        path = [current]
        cost = 0
        visited_run = {current}

        for iteration in range(max_iterations):
            nodes_explored += 1

            # Check if goal reached
            if current in goals:
                break

            neighbors = graph.get(current, [])
            if not neighbors:
                break

            # Evaluate all unvisited neighbors
            candidates = [
                (neighbor, edge_cost, evaluate_node(neighbor, goals, node_positions, risk_factors, congestion))
                for neighbor, edge_cost, risk in neighbors
                if neighbor not in visited_run
            ]

            if not candidates:
                break  # Local optimum / stuck

            # Select next node based on mode
            if mode == "steepest":
                # Best of all neighbors
                best_neighbor, best_edge_cost, _ = min(candidates, key=lambda x: x[2])
            else:
                # First neighbor that improves (simple hill climbing)
                current_score = evaluate_node(current, goals, node_positions, risk_factors, congestion)
                improving = [(n, c, s) for n, c, s in candidates if s < current_score]
                if not improving:
                    break
                best_neighbor, best_edge_cost, _ = improving[0]

            current = best_neighbor
            path.append(current)
            cost += best_edge_cost
            visited_run.add(current)

        # Track best result across restarts
        if path[-1] in goals and cost < best_global_cost:
            best_global_path = path
            best_global_cost = cost

    found = bool(best_global_path) and best_global_path[-1] in goals
    elapsed = (time.perf_counter() - start_time) * 1000
    _, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "algorithm": "Hill Climbing",
        "path": best_global_path,
        "cost": best_global_cost if found else float('inf'),
        "nodes_explored": nodes_explored,
        "time_ms": round(elapsed, 4),
        "memory_kb": round(mem_peak / 1024, 2),
        "found": found,
        "mode": mode,
        "restarts": restarts,
        "max_iterations": max_iterations
    }
