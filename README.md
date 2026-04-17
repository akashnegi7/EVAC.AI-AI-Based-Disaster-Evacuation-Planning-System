# 🚨 EVAC.AI — AI-Based Disaster Evacuation Planning System

> Intelligent city evacuation routing using 8 search algorithms. Simulates fire, flood, and earthquake scenarios with real-time pathfinding and adversarial disaster modelling.

---

## 📸 Screenshots

| Home Page | Simulation Dashboard | Algorithm Comparison |
|-----------|---------------------|----------------------|
| Animated city preview, algorithm cards | Interactive grid map, real-time simulation | Chart.js comparisons, ranked table |

---

## 🎯 Project Objective

Design an intelligent evacuation system that finds optimal escape routes in a city during disasters. The system models dynamic conditions: blocked roads, spreading fire, congestion, and adversarial disaster behaviour.

---

## 🧠 Algorithms Implemented

### Uninformed Search
| Algorithm | Time | Space | Optimal? | Use Case |
|-----------|------|-------|----------|----------|
| **BFS** | O(V+E) | O(V) | ✅ Yes (unweighted) | Equal-cost evacuation grids |
| **DFS** | O(V+E) | O(V) | ❌ No | Deep city exploration, memory-limited |

### Informed Search
| Algorithm | Time | Space | Optimal? | Use Case |
|-----------|------|-------|----------|----------|
| **Best-First** | O(V log V) | O(V) | ❌ No | Fast time-critical evacuations |
| **A\*** | O(V log V) | O(V) | ✅ Yes (admissible h) | Gold standard — balances cost + risk |

### Advanced Search
| Algorithm | Time | Space | Use Case |
|-----------|------|-------|----------|
| **AO\*** | O(V log V) | O(V) | Multi-goal: AND-OR graph, multiple shelters |
| **Hill Climbing** | O(k·b) | O(1) | Local path optimization, large maps |

### Adversarial Search
| Algorithm | Time | Space | Use Case |
|-----------|------|-------|----------|
| **Minimax** | O(b^d) | O(bd) | Worst-case route against active disaster |
| **Alpha-Beta** | O(b^(d/2)) | O(bd) | Optimized Minimax with branch pruning |

---

## 🏗️ Project Structure

```
disaster_evac/
│
├── backend/
│   ├── app.py                    # Flask API server
│   ├── algorithms/
│   │   ├── bfs.py                # Breadth-First Search
│   │   ├── dfs.py                # Depth-First Search
│   │   ├── best_first.py         # Greedy Best-First Search
│   │   ├── astar.py              # A* Search (Weighted)
│   │   ├── ao_star.py            # AO* AND-OR Search
│   │   ├── hill_climbing.py      # Hill Climbing + Random Restart
│   │   ├── minimax.py            # Minimax (Adversarial)
│   │   └── alpha_beta.py         # Alpha-Beta Pruning
│   └── utils/
│       └── graph_utils.py        # City model, disaster simulation
│
├── frontend/
│   ├── index.html                # Home page (animated preview)
│   ├── dashboard.html            # Simulation dashboard
│   └── comparison.html          # Algorithm comparison page
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### 1. Clone / Extract Project
```bash
cd disaster_evac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Backend
```bash
cd backend
python app.py
```
Server starts at: `http://localhost:5000`

### 4. Open Frontend
Open `frontend/index.html` in your browser, **or** access via Flask:
```
http://localhost:5000/
http://localhost:5000/dashboard
http://localhost:5000/comparison
```

> **Note:** The frontend includes a **demo/offline mode** that works without the backend. All algorithms run client-side in simplified form.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/generate-city` | Generate new city graph |
| POST | `/run-algorithm` | Run a specific algorithm |
| POST | `/compare` | Run all 8 algorithms |
| POST | `/update-map` | Block roads, update city |
| POST | `/simulate-disaster` | Trigger disaster spread |
| POST | `/suggest` | AI algorithm recommendation |

### Example: Run A* Search
```bash
curl -X POST http://localhost:5000/run-algorithm \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "astar",
    "start": 0,
    "goals": [99, 49],
    "params": {"heuristic_weight": 1.0}
  }'
```

### Example Response
```json
{
  "status": "ok",
  "result": {
    "algorithm": "A* Search",
    "path": [0, 1, 2, 12, 22, 33, 44, 54, 64, 74, 84, 94, 99],
    "cost": 912.4,
    "nodes_explored": 41,
    "time_ms": 0.512,
    "memory_kb": 14.2,
    "found": true,
    "heuristic_weight": 1.0
  }
}
```

---

## 🎮 Using the Dashboard

1. **Generate City** — Choose grid size (5×5 to 20×20) and disaster type
2. **Set Mode** — Click START / GOAL / BLOCK then click on the map
3. **Select Algorithm** — Tune parameters (heuristic weight, depth limit, etc.)
4. **Run Simulation** — Watch the animated pathfinding
5. **Dynamic Events** — Trigger fire spread, flooding, road blocks
6. **Compare All** — Jump to comparison page for side-by-side analysis

---

## 📊 Algorithm Comparison Page

The comparison page runs all 8 algorithms simultaneously and displays:
- **Bar charts**: Execution time, path cost
- **Line chart**: Nodes explored
- **Radar chart**: Multi-dimensional normalized performance
- **Score bars**: Composite ranking
- **Ranked table**: Sortable by any metric, highlights best in category

---

## 🔬 Algorithm Details

### A* Heuristic
```
f(n) = g(n) + w × h(n)
h(n) = euclidean_distance(n, nearest_goal) + risk_penalty(n)
risk_penalty(n) = risk_factor[n] × 5
```
- `w = 1.0` → standard optimal A*
- `w > 1.0` → Weighted A* (faster, suboptimal)

### AO* AND-OR Groups
```python
goal_groups = [
  {"shelter_A", "shelter_B"},    # OR: reach one
  {"medical_center"}              # AND: must also reach this
]
```

### Minimax Game Model
- **MAX player (Human)**: maximize safety score
- **MIN player (Disaster)**: block roads, spread fire
- Score: `1000 - depth×10` at goal, `-distance - risk×20` otherwise

### Alpha-Beta Pruning
```
if beta ≤ alpha: PRUNE remaining branches
```
Reduces O(b^d) to O(b^(d/2)) with good move ordering.

---

## 🧪 Test Scenarios

| Scenario | Grid | Disaster | Expected Best |
|----------|------|----------|---------------|
| Small City | 5×5 | Fire | BFS (simple, fast) |
| Medium City | 10×10 | Flood | A* (optimal) |
| Large City | 15×15 | Earthquake | Best-First (fast) |
| Multi-Goal | 10×10 | Fire | AO* (AND-OR) |
| Adversarial | 10×10 | Fire+Spread | Alpha-Beta |

---

## 🎨 UI Design

- **Aesthetic**: Dark command-center / emergency ops room
- **Typography**: Bebas Neue (display) + Space Mono (data) + Inter (body)
- **Color System**:
  - 🔴 Red `#ff2d2d` — Danger zones
  - 🟢 Green `#00ff88` — Safe shelters
  - 🟡 Yellow `#ffd700` — Explored nodes
  - 🔵 Blue `#00aaff` — Final evacuation path
- **Features**: Animated grid background, glowing nodes, scroll reveal, demo mode

---

## 📘 Data Structures

```python
# Graph (Adjacency List)
graph = {
  0: [(1, 60.0, 0.1), (10, 60.0, 0.0)],  # (neighbor, cost, risk)
  1: [(0, 60.0, 0.0), (2, 60.0, 0.3)],
  ...
}

# Node Attributes
node_positions = { 0: (30, 30), 1: (90, 30), ... }  # (x, y)
risk_factors   = { 0: 0.0, 1: 0.7, ... }             # 0=safe, 1=danger
congestion     = { 0: 0.1, 1: 0.4, ... }             # traffic level
node_types     = { 0: 'normal', 1: 'danger', ... }   # normal/shelter/danger
```

---

## 👥 Acknowledgements

Built as an academic AI project demonstrating search algorithms in a real-world disaster response context.

**Technologies**: Python · Flask · NetworkX · HTML5 Canvas · Chart.js · CSS3

---

## 📄 License

For educational and academic use.
