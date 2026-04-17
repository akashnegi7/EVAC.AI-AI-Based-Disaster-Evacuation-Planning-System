"""
Breadth-First Search (BFS) Algorithm
=====================================
Explores graph level by level. Guarantees shortest path in unweighted graphs.
Time: O(V+E), Space: O(V)
"""

from collections import deque
import time
import tracemalloc


def bfs(graph, start, goals):
    """
    BFS for evacuation routing.
    
    Args:
        graph: dict adjacency list {node: [(neighbor, cost, risk), ...]}
        start: starting node
        goals: set/list of safe destination nodes
    
    Returns:
        dict with path, cost, nodes_explored, time_ms, memory_kb
    """
    start_time = time.perf_counter()
    tracemalloc.start()

    goals = set(goals)
    queue = deque()
    queue.append((start, [start], 0))  # (current_node, path, cost)
    visited = set([start])
    nodes_explored = 0

    while queue:
        current, path, cost = queue.popleft()
        nodes_explored += 1

        # Check if we've reached a goal
        if current in goals:
            elapsed = (time.perf_counter() - start_time) * 1000
            _, mem_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return {
                "algorithm": "BFS",
                "path": path,
                "cost": cost,
                "nodes_explored": nodes_explored,
                "time_ms": round(elapsed, 4),
                "memory_kb": round(mem_peak / 1024, 2),
                "found": True
            }

        # Explore neighbors
        neighbors = graph.get(current, [])
        for neighbor, edge_cost, risk in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_cost = cost + edge_cost
                queue.append((neighbor, path + [neighbor], new_cost))

    elapsed = (time.perf_counter() - start_time) * 1000
    _, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "algorithm": "BFS",
        "path": [],
        "cost": float('inf'),
        "nodes_explored": nodes_explored,
        "time_ms": round(elapsed, 4),
        "memory_kb": round(mem_peak / 1024, 2),
        "found": False
    }
