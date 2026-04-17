"""
Minimax Algorithm
==================
Models disaster evacuation as a two-player adversarial game:
- MAX player (Human): tries to find the SAFEST, fastest route
- MIN player (Disaster): tries to BLOCK routes, spread fire/flood

Game tree alternates between human moves and disaster events.
Returns the path that maximizes safety even under worst-case disaster moves.

State: (current_node, blocked_edges, disaster_zones, depth)
"""

import math
import time
import tracemalloc
import random


def evaluate_state(node, goals, node_positions, risk_factors, blocked, depth):
    """
    Evaluate game state from human's perspective (higher = better).
    
    Returns positive score if near goal, negative if in danger zone.
    """
    if node in goals:
        return 1000 - depth * 10  # Reached goal faster = better

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


def minimax(graph, start, goals, node_positions, risk_factors,
            max_depth=5, is_max_turn=True, path=None,
            blocked=None, disaster_spread_factor=0.3):
    """
    Minimax search for disaster vs human game.
    
    Args:
        graph: adjacency list
        start: current node
        goals: safe zones
        node_positions: {node: (x,y)}
        risk_factors: {node: float}
        max_depth: search depth limit
        is_max_turn: True = human move, False = disaster move
        path: current path being built
        blocked: set of currently blocked nodes
        disaster_spread_factor: probability disaster blocks a neighbor
    
    Returns:
        dict with best_path, score, nodes_explored, time_ms
    """
    start_time = time.perf_counter()
    tracemalloc.start()

    goals = set(goals)
    if blocked is None:
        blocked = set()
    if path is None:
        path = [start]

    nodes_explored = [0]

    def _minimax(node, depth, is_max, current_path, current_blocked, current_risks):
        nodes_explored[0] += 1

        # Terminal conditions
        if node in goals:
            return evaluate_state(node, goals, node_positions, current_risks, current_blocked, depth), current_path

        if depth == 0:
            return evaluate_state(node, goals, node_positions, current_risks, current_blocked, depth), current_path

        neighbors = [
            (n, c, r) for n, c, r in graph.get(node, [])
            if n not in current_blocked
        ]

        if not neighbors:
            return -500, current_path  # No moves available

        if is_max:
            # Human player: maximize score, pick best neighbor
            best_score = -math.inf
            best_path = current_path

            for neighbor, cost, risk in neighbors:
                score, found_path = _minimax(
                    neighbor, depth - 1, False,
                    current_path + [neighbor], current_blocked, current_risks
                )
                if score > best_score:
                    best_score = score
                    best_path = found_path

            return best_score, best_path

        else:
            # Disaster player: minimize score, block some edges
            worst_score = math.inf
            worst_path = current_path

            # Disaster tries blocking random neighbors
            disaster_options = []
            for neighbor, cost, risk in neighbors:
                new_blocked = set(current_blocked)
                # Disaster can block this neighbor with some probability
                if random.random() < disaster_spread_factor:
                    new_blocked.add(neighbor)
                disaster_options.append((neighbor, new_blocked))

            if not disaster_options:
                disaster_options = [(n, current_blocked) for n, c, r in neighbors]

            for neighbor, new_blocked in disaster_options[:3]:  # Limit branching
                new_risks = dict(current_risks)
                # Disaster increases risk of nearby nodes
                new_risks[neighbor] = min(1.0, new_risks.get(neighbor, 0) + 0.3)

                score, found_path = _minimax(
                    neighbor, depth - 1, True,
                    current_path + [neighbor], new_blocked, new_risks
                )
                if score < worst_score:
                    worst_score = score
                    worst_path = found_path

            return worst_score, worst_path

    best_score, best_path = _minimax(start, max_depth, is_max_turn, path, blocked, dict(risk_factors))

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
        "algorithm": "Minimax",
        "path": best_path,
        "cost": cost,
        "score": best_score,
        "nodes_explored": nodes_explored[0],
        "time_ms": round(elapsed, 4),
        "memory_kb": round(mem_peak / 1024, 2),
        "found": found,
        "max_depth": max_depth
    }
