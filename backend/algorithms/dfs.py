"""
Depth-First Search (DFS) Algorithm
=====================================
Explores graph by going deep before backtracking. Uses a stack.
Supports optional depth limit. Not guaranteed to find shortest path.
Time: O(V+E), Space: O(V)
"""

import time
import tracemalloc


def dfs(graph, start, goals, depth_limit=None):
    """
    DFS for evacuation routing with optional depth limit.
    
    Args:
        graph: dict adjacency list {node: [(neighbor, cost, risk), ...]}
        start: starting node
        goals: set/list of safe destination nodes
        depth_limit: maximum depth to explore (None = unlimited)
    
    Returns:
        dict with path, cost, nodes_explored, time_ms, memory_kb
    """
    start_time = time.perf_counter()
    tracemalloc.start()

    goals = set(goals)
    # Stack holds (current_node, path, cost, depth)
    stack = [(start, [start], 0, 0)]
    visited = set()
    nodes_explored = 0
    best_result = None

    while stack:
        current, path, cost, depth = stack.pop()

        if current in visited:
            continue
        visited.add(current)
        nodes_explored += 1

        # Check goal
        if current in goals:
            elapsed = (time.perf_counter() - start_time) * 1000
            _, mem_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return {
                "algorithm": "DFS",
                "path": path,
                "cost": cost,
                "nodes_explored": nodes_explored,
                "time_ms": round(elapsed, 4),
                "memory_kb": round(mem_peak / 1024, 2),
                "found": True,
                "depth_limit": depth_limit
            }

        # Respect depth limit
        if depth_limit is not None and depth >= depth_limit:
            continue

        # Push neighbors onto stack (reversed for consistent ordering)
        neighbors = graph.get(current, [])
        for neighbor, edge_cost, risk in reversed(neighbors):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor], cost + edge_cost, depth + 1))

    elapsed = (time.perf_counter() - start_time) * 1000
    _, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "algorithm": "DFS",
        "path": [],
        "cost": float('inf'),
        "nodes_explored": nodes_explored,
        "time_ms": round(elapsed, 4),
        "memory_kb": round(mem_peak / 1024, 2),
        "found": False,
        "depth_limit": depth_limit
    }
