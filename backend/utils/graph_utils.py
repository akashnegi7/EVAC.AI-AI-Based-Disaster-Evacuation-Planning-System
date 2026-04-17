"""
Graph Utilities & City Model
==============================
Generates city graphs for disaster evacuation simulation.
Nodes = locations, Edges = roads with cost/risk/congestion.
"""

import random
import math
import json


def generate_grid_city(rows=10, cols=10, disaster_type="fire"):
    """
    Generate a grid-based city graph.
    
    Args:
        rows, cols: grid dimensions
        disaster_type: 'fire', 'flood', 'earthquake'
    
    Returns:
        graph, node_positions, risk_factors, congestion, node_types
    """
    graph = {}
    node_positions = {}
    risk_factors = {}
    congestion = {}
    node_types = {}  # 'normal', 'shelter', 'hospital', 'danger'

    # Create nodes
    for r in range(rows):
        for c in range(cols):
            node_id = r * cols + c
            node_positions[node_id] = (c * 60 + 30, r * 60 + 30)
            graph[node_id] = []
            risk_factors[node_id] = 0.0
            congestion[node_id] = random.uniform(0, 0.3)
            node_types[node_id] = "normal"

    # Create disaster zone (concentrated in one area)
    if disaster_type == "fire":
        _add_fire_zone(rows, cols, risk_factors, node_types)
    elif disaster_type == "flood":
        _add_flood_zone(rows, cols, risk_factors, node_types)
    elif disaster_type == "earthquake":
        _add_earthquake_damage(rows, cols, risk_factors, node_types)

    # Add shelters at edges/corners
    shelters = _place_shelters(rows, cols)
    for s in shelters:
        node_types[s] = "shelter"
        risk_factors[s] = 0.0  # Shelters are safe

    # Create edges (4-directional grid + some diagonals)
    for r in range(rows):
        for c in range(cols):
            node_id = r * cols + c
            # Right
            if c + 1 < cols:
                neighbor = r * cols + (c + 1)
                cost = _edge_cost(node_id, neighbor, node_positions, risk_factors, congestion)
                graph[node_id].append((neighbor, cost, risk_factors[neighbor]))
                graph[neighbor].append((node_id, cost, risk_factors[node_id]))
            # Down
            if r + 1 < rows:
                neighbor = (r + 1) * cols + c
                cost = _edge_cost(node_id, neighbor, node_positions, risk_factors, congestion)
                graph[node_id].append((neighbor, cost, risk_factors[neighbor]))
                graph[neighbor].append((node_id, cost, risk_factors[node_id]))

    return {
        "graph": graph,
        "node_positions": node_positions,
        "risk_factors": risk_factors,
        "congestion": congestion,
        "node_types": node_types,
        "shelters": shelters,
        "rows": rows,
        "cols": cols
    }


def _edge_cost(n1, n2, positions, risks, congestion):
    """Calculate edge cost = distance * (1 + congestion) * (1 + risk)."""
    p1, p2 = positions[n1], positions[n2]
    dist = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    cong_factor = 1 + congestion.get(n2, 0)
    risk_factor = 1 + risks.get(n2, 0) * 0.5
    return round(dist * cong_factor * risk_factor, 2)


def _add_fire_zone(rows, cols, risk_factors, node_types):
    """Add fire zone in center-left area."""
    center_r, center_c = rows // 3, cols // 3
    for r in range(max(0, center_r-2), min(rows, center_r+3)):
        for c in range(max(0, center_c-2), min(cols, center_c+3)):
            node_id = r * cols + c
            dist = abs(r - center_r) + abs(c - center_c)
            risk_factors[node_id] = max(risk_factors[node_id], max(0, 1.0 - dist * 0.2))
            if dist <= 1:
                node_types[node_id] = "danger"


def _add_flood_zone(rows, cols, risk_factors, node_types):
    """Add flood zone along bottom rows."""
    for r in range(rows - 3, rows):
        for c in range(cols):
            node_id = r * cols + c
            risk_factors[node_id] = max(risk_factors[node_id], (r - (rows-3)) * 0.35)
            if r >= rows - 2:
                node_types[node_id] = "danger"


def _add_earthquake_damage(rows, cols, risk_factors, node_types):
    """Add scattered earthquake damage."""
    random.seed(42)
    damage_spots = random.sample(range(rows * cols), k=min(15, rows * cols // 4))
    for node_id in damage_spots:
        risk_factors[node_id] = random.uniform(0.5, 1.0)
        if risk_factors[node_id] > 0.8:
            node_types[node_id] = "danger"


def _place_shelters(rows, cols):
    """Place shelters at corners and edge midpoints."""
    shelters = []
    # Corners
    shelters.append((rows-1) * cols + (cols-1))  # Bottom-right
    shelters.append((rows-1) * cols)               # Bottom-left
    shelters.append(cols - 1)                       # Top-right
    # Edge midpoints
    shelters.append(rows // 2 * cols + (cols - 1))  # Right middle
    return shelters


def apply_dynamic_change(city_data, change_type="block_road"):
    """
    Apply dynamic disaster changes to city.
    
    change_type: 'block_road', 'spread_fire', 'increase_traffic'
    """
    graph = city_data["graph"]
    risk_factors = city_data["risk_factors"]
    congestion = city_data["congestion"]

    if change_type == "block_road":
        # Randomly block some edges
        nodes = list(graph.keys())
        for _ in range(3):
            node = random.choice(nodes)
            if graph[node]:
                idx = random.randint(0, len(graph[node]) - 1)
                graph[node].pop(idx)

    elif change_type == "spread_fire":
        # Increase risk in high-risk areas
        for node in list(risk_factors.keys()):
            if risk_factors[node] > 0.3:
                neighbors_spread = [
                    n for n, c, r in graph.get(node, [])
                ]
                for neighbor in neighbors_spread[:2]:
                    risk_factors[neighbor] = min(1.0, risk_factors[neighbor] + 0.2)

    elif change_type == "increase_traffic":
        # Increase congestion on random roads
        for node in random.sample(list(congestion.keys()), k=min(10, len(congestion))):
            congestion[node] = min(1.0, congestion[node] + 0.3)

    return city_data


def get_best_algorithm_suggestion(city_data, num_goals, disaster_intensity):
    """
    AI suggestion: recommend best algorithm based on scenario.
    """
    rows = city_data.get("rows", 10)
    cols = city_data.get("cols", 10)
    graph_size = rows * cols
    
    suggestions = []
    
    if num_goals > 1:
        suggestions.append(("AO* Search", "Multiple evacuation targets - AO* handles AND-OR multi-goal planning best"))
    
    if disaster_intensity > 0.7:
        suggestions.append(("Alpha-Beta Pruning", "High disaster intensity - adversarial search prepares for worst-case scenarios"))
    elif disaster_intensity > 0.4:
        suggestions.append(("A* Search", "Moderate disaster - A* finds optimal path balancing speed and risk"))
    else:
        suggestions.append(("A* Search", "Low intensity - A* is optimal and efficient"))
    
    if graph_size > 200:
        suggestions.append(("Best-First Search", "Large city - Best-First is fastest for large graphs"))
    
    return suggestions[0] if suggestions else ("A* Search", "Default optimal choice for evacuation")


def serialize_city(city_data):
    """Convert city data to JSON-serializable format."""
    result = {}
    for key, val in city_data.items():
        if isinstance(val, dict):
            result[key] = {str(k): v for k, v in val.items()}
        elif isinstance(val, list):
            result[key] = [int(x) for x in val]
        else:
            result[key] = val
    
    # Serialize graph with string keys
    result["graph"] = {
        str(k): [(int(n), float(c), float(r)) for n, c, r in v]
        for k, v in city_data["graph"].items()
    }
    result["node_positions"] = {
        str(k): list(v) for k, v in city_data["node_positions"].items()
    }
    return result
