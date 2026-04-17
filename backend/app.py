"""
AI-Based Disaster Evacuation Planning System
=============================================
Flask Backend API

Endpoints:
  POST /run-algorithm     - Run a specific search algorithm
  POST /compare           - Compare all algorithms
  POST /update-map        - Update map (block roads, etc.)
  POST /simulate-disaster - Trigger disaster events
  GET  /generate-city     - Generate a new city graph
  GET  /suggest           - AI algorithm suggestion
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import time
import tracemalloc
import random

from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.best_first import best_first_search
from algorithms.astar import astar
from algorithms.ao_star import ao_star
from algorithms.hill_climbing import hill_climbing
from algorithms.minimax import minimax
from algorithms.alpha_beta import alpha_beta_pruning
from utils.graph_utils import (
    generate_grid_city, apply_dynamic_change,
    get_best_algorithm_suggestion, serialize_city
)

app = Flask(__name__, static_folder='../frontend', template_folder='../templates')
CORS(app)

# Global city state
current_city = None


def get_city():
    global current_city
    if current_city is None:
        current_city = generate_grid_city(10, 10, "fire")
    return current_city


def parse_city_params(data):
    """Extract algorithm-needed parameters from city data."""
    city = get_city()
    graph = city["graph"]
    node_positions = city["node_positions"]
    risk_factors = city["risk_factors"]
    congestion = city["congestion"]
    shelters = city["shelters"]
    
    # Allow override from request
    start = data.get("start", 0)
    goals = data.get("goals", shelters)
    
    return graph, node_positions, risk_factors, congestion, int(start), [int(g) for g in goals]


@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')


@app.route('/dashboard')
def dashboard():
    return send_from_directory('../frontend', 'dashboard.html')


@app.route('/comparison')
def comparison():
    return send_from_directory('../frontend', 'comparison.html')


@app.route('/frontend/<path:filename>')
def frontend_files(filename):
    return send_from_directory('../frontend', filename)


@app.route('/generate-city', methods=['GET', 'POST'])
def generate_city_endpoint():
    """Generate a new city graph."""
    global current_city
    
    data = request.get_json(silent=True) or {}
    rows = int(data.get("rows", 10))
    cols = int(data.get("cols", 10))
    disaster = data.get("disaster_type", "fire")
    
    rows = max(5, min(rows, 20))
    cols = max(5, min(cols, 20))
    
    current_city = generate_grid_city(rows, cols, disaster)
    
    return jsonify({
        "status": "ok",
        "city": serialize_city(current_city),
        "message": f"Generated {rows}x{cols} city with {disaster} disaster"
    })


@app.route('/run-algorithm', methods=['POST'])
def run_algorithm():
    """Run a specific algorithm and return results."""
    data = request.get_json()
    algorithm = data.get("algorithm", "astar").lower().replace(" ", "_").replace("-", "_")
    
    graph, node_positions, risk_factors, congestion, start, goals = parse_city_params(data)
    
    # Algorithm parameters
    params = data.get("params", {})
    
    result = None
    
    try:
        if algorithm == "bfs":
            result = bfs(graph, start, goals)
            
        elif algorithm == "dfs":
            depth_limit = params.get("depth_limit", None)
            result = dfs(graph, start, goals, depth_limit=depth_limit)
            
        elif algorithm in ("best_first", "best_first_search", "bestfirst"):
            result = best_first_search(graph, start, goals, node_positions, risk_factors)
            
        elif algorithm in ("astar", "a_star", "a*"):
            weight = float(params.get("heuristic_weight", 1.0))
            result = astar(graph, start, goals, node_positions, risk_factors, weight)
            
        elif algorithm in ("ao_star", "aostar", "ao*"):
            # Create goal groups for AND-OR search
            mid = max(1, len(goals) // 2)
            goal_groups = [set(goals[:mid]), set(goals[mid:])] if len(goals) > 1 else [set(goals)]
            result = ao_star(graph, start, goal_groups, node_positions, risk_factors)
            
        elif algorithm in ("hill_climbing", "hillclimbing"):
            iterations = int(params.get("iterations", 500))
            restarts = int(params.get("restarts", 3))
            result = hill_climbing(graph, start, goals, node_positions, risk_factors,
                                   congestion, max_iterations=iterations, restarts=restarts)
            
        elif algorithm == "minimax":
            depth = int(params.get("max_depth", 4))
            result = minimax(graph, start, goals, node_positions, risk_factors, max_depth=depth)
            
        elif algorithm in ("alpha_beta", "alpha_beta_pruning", "alphabeta"):
            depth = int(params.get("max_depth", 5))
            result = alpha_beta_pruning(graph, start, goals, node_positions, risk_factors, max_depth=depth)
            
        else:
            return jsonify({"error": f"Unknown algorithm: {algorithm}"}), 400
    
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500
    
    # Make cost JSON-serializable
    if result.get("cost") == float('inf'):
        result["cost"] = -1
    
    return jsonify({"status": "ok", "result": result})


@app.route('/compare', methods=['POST'])
def compare_algorithms():
    """Run ALL algorithms and return comparison."""
    data = request.get_json() or {}
    graph, node_positions, risk_factors, congestion, start, goals = parse_city_params(data)
    
    results = []
    
    algorithms_to_run = [
        ("BFS", lambda: bfs(graph, start, goals)),
        ("DFS", lambda: dfs(graph, start, goals)),
        ("Best-First", lambda: best_first_search(graph, start, goals, node_positions, risk_factors)),
        ("A*", lambda: astar(graph, start, goals, node_positions, risk_factors)),
        ("AO*", lambda: ao_star(graph, start, [set(goals)], node_positions, risk_factors)),
        ("Hill Climbing", lambda: hill_climbing(graph, start, goals, node_positions, risk_factors, congestion)),
        ("Minimax", lambda: minimax(graph, start, goals, node_positions, risk_factors, max_depth=4)),
        ("Alpha-Beta", lambda: alpha_beta_pruning(graph, start, goals, node_positions, risk_factors, max_depth=5)),
    ]
    
    for name, algo_fn in algorithms_to_run:
        try:
            result = algo_fn()
            if result.get("cost") == float('inf'):
                result["cost"] = -1
            results.append({
                "name": name,
                "path_length": len(result.get("path", [])),
                "cost": result.get("cost", -1),
                "nodes_explored": result.get("nodes_explored", 0),
                "time_ms": result.get("time_ms", 0),
                "memory_kb": result.get("memory_kb", 0),
                "found": result.get("found", False),
                "path": result.get("path", [])
            })
        except Exception as e:
            results.append({
                "name": name,
                "path_length": 0,
                "cost": -1,
                "nodes_explored": 0,
                "time_ms": 0,
                "memory_kb": 0,
                "found": False,
                "error": str(e),
                "path": []
            })
    
    return jsonify({"status": "ok", "results": results})


@app.route('/update-map', methods=['POST'])
def update_map():
    """Apply dynamic changes to the city map."""
    global current_city
    data = request.get_json() or {}
    change_type = data.get("change_type", "block_road")
    
    city = get_city()
    updated = apply_dynamic_change(city, change_type)
    current_city = updated
    
    return jsonify({
        "status": "ok",
        "message": f"Applied change: {change_type}",
        "city": serialize_city(current_city)
    })


@app.route('/simulate-disaster', methods=['POST'])
def simulate_disaster():
    """Trigger progressive disaster simulation."""
    global current_city
    data = request.get_json() or {}
    disaster_type = data.get("disaster_type", "fire")
    intensity = float(data.get("intensity", 0.5))
    
    city = get_city()
    
    # Apply multiple changes based on intensity
    changes = int(intensity * 5) + 1
    for _ in range(changes):
        if disaster_type == "fire":
            apply_dynamic_change(city, "spread_fire")
        elif disaster_type == "flood":
            apply_dynamic_change(city, "block_road")
        elif disaster_type == "earthquake":
            apply_dynamic_change(city, "block_road")
            apply_dynamic_change(city, "increase_traffic")
        else:
            apply_dynamic_change(city, "increase_traffic")
    
    current_city = city
    
    return jsonify({
        "status": "ok",
        "disaster_type": disaster_type,
        "intensity": intensity,
        "city": serialize_city(current_city)
    })


@app.route('/suggest', methods=['POST'])
def suggest_algorithm():
    """AI suggestion for best algorithm."""
    data = request.get_json() or {}
    city = get_city()
    
    num_goals = int(data.get("num_goals", len(city["shelters"])))
    
    # Calculate disaster intensity from risk factors
    risks = list(city["risk_factors"].values())
    avg_risk = sum(risks) / len(risks) if risks else 0
    
    suggestion, reason = get_best_algorithm_suggestion(city, num_goals, avg_risk)
    
    return jsonify({
        "status": "ok",
        "suggested_algorithm": suggestion,
        "reason": reason,
        "disaster_intensity": round(avg_risk, 3)
    })


if __name__ == '__main__':
    print("🚨 Disaster Evacuation System Backend Starting...")
    print("📡 API running at http://localhost:5000")
    app.run(debug=True, port=5000)
