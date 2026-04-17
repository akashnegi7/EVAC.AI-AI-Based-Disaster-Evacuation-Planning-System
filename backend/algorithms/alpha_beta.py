"""
Alpha-Beta Pruning
===================
Optimized Minimax that prunes branches that cannot affect the final decision.
Reduces worst-case from O(b^d) to O(b^(d/2)) with perfect ordering.

Alpha = best value MAX can guarantee (starts at -inf)
Beta  = best value MIN can guarantee (starts at +inf)

Pruning: if alpha >= beta, prune remaining branches.
"""

import math
import time
import tracemalloc
import random


def evaluate_state(node, goals, node_positions, risk_factors, depth):
    """Evaluate state from human (MAX) perspective."""
    if node in goals:
        return 1000 - depth * 10

    if node not in node_positions:
        return -1000

    pos = node_positions[node]
    goals_list = [g for g in goals if g in node_positions]
    if not goals_list:
        return -500

    min_dist = min(
        math.sqrt((pos[0] - node_positions[g][0])**2 + (pos[1] - node_positions[g][1])**2)
        for g in goals_list
    )
    risk = risk_factors.get(node, 0)
    return -min_dist - risk * 20 - depth * 2


def alpha_beta_pruning(graph, start, goals, node_positions, risk_factors,
                       max_depth=6, disaster_spread_factor=0.3):
    """
    Alpha-Beta Pruning for optimized adversarial evacuation search.
    
    Args:
        graph: adjacency list
        start: current node
        goals: safe zone nodes
        node_positions: {node: (x,y)}
        risk_factors: {node: float}
        max_depth: search depth
        disaster_spread_factor: chance disaster blocks a path
    
    Returns:
        dict with best_path, score, nodes_explored, pruned_count, time_ms
    """
    start_time = time.perf_counter()
    tracemalloc.start()

    goals = set(goals)
    nodes_explored = [0]
    pruned_count = [0]

    def _alpha_beta(node, depth, alpha, beta, is_max, current_path, blocked, risks):
        nodes_explored[0] += 1

        # Terminal conditions
        if node in goals:
            return evaluate_state(node, goals, node_positions, risks, depth), current_path
        if depth == 0:
            return evaluate_state(node, goals, node_positions, risks, depth), current_path

        neighbors = [
            (n, c, r) for n, c, r in graph.get(node, [])
            if n not in blocked
        ]

        if not neighbors:
            return -800, current_path

        if is_max:
            # MAX player (human): maximize
            best_val = -math.inf
            best_path = current_path

            for neighbor, cost, risk in neighbors:
                val, found_path = _alpha_beta(
                    neighbor, depth - 1, alpha, beta, False,
                    current_path + [neighbor], blocked, risks
                )
                if val > best_val:
                    best_val = val
                    best_path = found_path

                alpha = max(alpha, best_val)
                if beta <= alpha:
                    pruned_count[0] += 1
                    break  # Beta cutoff (pruning!)

            return best_val, best_path

        else:
            # MIN player (disaster): minimize
            best_val = math.inf
            best_path = current_path

            for neighbor, cost, risk in neighbors[:3]:  # Limit disaster branching
                new_blocked = set(blocked)
                if random.random() < disaster_spread_factor:
                    new_blocked.add(neighbor)

                new_risks = dict(risks)
                new_risks[neighbor] = min(1.0, new_risks.get(neighbor, 0) + 0.25)

                val, found_path = _alpha_beta(
                    neighbor, depth - 1, alpha, beta, True,
                    current_path + [neighbor], new_blocked, new_risks
                )
                if val < best_val:
                    best_val = val
                    best_path = found_path

                beta = min(beta, best_val)
                if beta <= alpha:
                    pruned_count[0] += 1
                    break  # Alpha cutoff (pruning!)

            return best_val, best_path

    best_score, best_path = _alpha_beta(
        start, max_depth, -math.inf, math.inf, True, [start], set(), dict(risk_factors)
    )

    elapsed = (time.perf_counter() - start_time) * 1000
    _, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    found = bool(best_path) and best_path[-1] in goals

    # Calculate path cost
    cost = 0
    for i in range(len(best_path) - 1):
        for neighbor, edge_cost, risk in graph.get(best_path[i], []):
            if neighbor == best_path[i + 1]:
                cost += edge_cost
                break

    return {
        "algorithm": "Alpha-Beta Pruning",
        "path": best_path,
        "cost": cost,
        "score": best_score,
        "nodes_explored": nodes_explored[0],
        "pruned_branches": pruned_count[0],
        "time_ms": round(elapsed, 4),
        "memory_kb": round(mem_peak / 1024, 2),
        "found": found,
        "max_depth": max_depth
    }
