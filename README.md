# Poople Solver 🚀

A Python-based algorithmic solver for the "Poople" game (a variation of the classic Word Ladder puzzle). Given any starting 4-letter word, the program finds the shortest path to the target word ("poop") by changing only one letter at a time.

## 🧠 The Engineering Approach

Instead of just writing a single search algorithm, this project was built as a **race** between multiple graph-search strategies. It runs them side-by-side, compares their results, and displays only the winning (shortest) path.

### Algorithms Implemented:
- **Standard BFS:** The baseline. Guarantees the shortest path but explores the graph blindly.
- **Bidirectional BFS:** Searches from both the start word and the target word simultaneously. Drastically reduces the search space and is usually the fastest.
- **A* (A-Star) with Hamming Distance:** Uses an admissible heuristic to prioritize nodes that are closest to the target.
- **Greedy Best-First:** Fast but not guaranteed to be optimal.
- **Multi-Source BFS:** Expands the search from multiple starting seeds simultaneously.

## ⚙️ Features
- **Optimal Path Guarantee:** By comparing strategies, the true shortest path is always found.
- **Dictionary Validation:** Automatically downloads and caches a 4-letter word list.
- **Pickle Caching:** Caches the BFS distance map to `poop` for instant subsequent queries.
- **Path Visualization:** Prints the winning path as a clean, step-by-step word ladder in the terminal.

## 🛠️ Tech Stack
- **Language:** Python 3
- **Core Concepts:** Graph Theory, Breadth-First Search (BFS), A* Search, Heuristics, Information Entropy, Object-Oriented Design.
- **Libraries:** `collections` (deque, defaultdict), `heapq`, `urllib`.

## 🚀 How to Run
I built this project to be completely frictionless. No need to open a terminal, navigate directories, or remember complex commands.

Clone the repository.

Double-click start_poople.bat (included in the repo).

The launcher will automatically open the terminal, run the Python script, and start the game.

Enter any 4-letter starting word (e.g., cold).

When you type quit, the launcher pauses so you can read the output before closing the window.

(Note: The first run will download a ~15,000-word dictionary to the local directory. Subsequent runs are instant thanks to local caching).
