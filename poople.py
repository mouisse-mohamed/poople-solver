#!/usr/bin/env python3
"""
Poople Game Solver - Multi-Strategy Race Edition

Runs several different search strategies at the same time, compares
their results, and prints ONLY the shortest path found.

Strategies included:
  1. Standard BFS (baseline)
  2. Bidirectional BFS (meets in the middle)
  3. A* with Hamming-distance heuristic
  4. Greedy best-first (fast, not guaranteed optimal)
  5. Multi-source BFS from a few random "nearby" seeds
"""

import os
import string
import urllib.request
import heapq
import random
from collections import deque, defaultdict

DICT_URL = "https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt"
BASE = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE, "words_cache.txt")
TARGET = "poop"
WORD_LEN = 4

FALLBACK_WORDS = {
    "poop","pool","poor","pope","pole","pore","pops","pond","loop","loom",
    "look","loon","boom","book","boot","bold","cool","coop","coot","cope",
    "copy","cops","cape","cave","cage","dope","door","doom","food","fool",
    "foot","good","gold","goad","hoop","hope","hood","hook","hoof","poof",
    "pooh","pomp","prop","plop","plod","ploy","plot","poll","pale","palm",
    "cold","cord","card","care","cure","pure","pour","mood","moon","goop",
    "goof","gook","soot","soon","word","ward","warm","worm","worn","torn",
    "town","gown","down","dawn","yawn","year","bear","beer","deer","dear",
    "fear","near",
}


# ---------------------------------------------------------------------------
# Dictionary + graph setup
# ---------------------------------------------------------------------------

def get_dictionary():
    if not os.path.exists(CACHE_FILE):
        print("Downloading dictionary (first run only)...")
        try:
            urllib.request.urlretrieve(DICT_URL, CACHE_FILE)
        except Exception as e:
            print(f"Download failed ({e}). Using fallback.")
            return set(FALLBACK_WORDS)
    words = set()
    with open(CACHE_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip().lower()
            if len(w) == WORD_LEN and w.isalpha():
                words.add(w)
    return words


def build_wildcard_buckets(dictionary):
    buckets = defaultdict(list)
    for w in dictionary:
        for i in range(WORD_LEN):
            buckets[w[:i] + "_" + w[i+1:]].append(w)
    return buckets


def neighbors(word, buckets):
    seen = set()
    for i in range(WORD_LEN):
        pattern = word[:i] + "_" + word[i+1:]
        for n in buckets.get(pattern, ()):
            if n == word or n in seen:
                continue
            if len(n) != len(word):
                continue
            diffs = sum(1 for a, b in zip(word, n) if a != b)
            if diffs != 1:
                print(f"  [BUG] {word} -> {n} has {diffs} diffs")
                continue
            seen.add(n)
            yield n


def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


# ---------------------------------------------------------------------------
# Strategy 1: Standard BFS
# ---------------------------------------------------------------------------

def bfs(start, target, buckets):
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        word, path = queue.popleft()
        if word == target:
            return path
        for nxt in neighbors(word, buckets):
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))
    return None


# ---------------------------------------------------------------------------
# Strategy 2: Bidirectional BFS
# ---------------------------------------------------------------------------

def bidirectional_bfs(start, target, buckets):
    if start == target:
        return [start]

    front_parent = {start: None}   # from start
    back_parent  = {target: None}  # from target
    front_layer = {start}
    back_layer  = {target}

    def reconstruct(meet):
        # start ... meet
        left = []
        w = meet
        while w is not None:
            left.append(w)
            w = front_parent[w]
        left.reverse()
        # meet ... target (skip meet itself, already in left)
        right = []
        w = back_parent[meet]
        while w is not None:
            right.append(w)
            w = back_parent[w]
        return left + right

    while front_layer and back_layer:
        # Always expand the smaller side
        if len(front_layer) <= len(back_layer):
            expand, parent, other_parent = front_layer, front_parent, back_parent
            is_front = True
        else:
            expand, parent, other_parent = back_layer, back_parent, front_parent
            is_front = False

        next_layer = set()
        for word in expand:
            for nxt in neighbors(word, buckets):
                if nxt in parent:
                    continue
                parent[nxt] = word

                if nxt in other_parent:
                    # Met in the middle — nxt is the meeting word
                    return reconstruct(nxt)
                next_layer.add(nxt)

        if is_front:
            front_layer = next_layer
        else:
            back_layer = next_layer

    return None


# ---------------------------------------------------------------------------
# Strategy 3: A* with Hamming heuristic
# ---------------------------------------------------------------------------

def astar(start, target, buckets):
    open_heap = [(hamming(start, target), 0, start, [start])]
    visited = set()
    while open_heap:
        _, g, word, path = heapq.heappop(open_heap)
        if word == target:
            return path
        if word in visited:
            continue
        visited.add(word)
        for nxt in neighbors(word, buckets):
            if nxt not in visited:
                heapq.heappush(
                    open_heap,
                    (g + 1 + hamming(nxt, target), g + 1, nxt, path + [nxt])
                )
    return None


# ---------------------------------------------------------------------------
# Strategy 4: Greedy best-first (fast, may not be optimal)
# ---------------------------------------------------------------------------

def greedy_best_first(start, target, buckets):
    heap = [(hamming(start, target), start, [start])]
    visited = {start}
    while heap:
        _, word, path = heapq.heappop(heap)
        if word == target:
            return path
        for nxt in neighbors(word, buckets):
            if nxt not in visited:
                visited.add(nxt)
                heapq.heappush(heap, (hamming(nxt, target), nxt, path + [nxt]))
    return None


# ---------------------------------------------------------------------------
# Strategy 5: Multi-source BFS from random "near" seeds
# ---------------------------------------------------------------------------

def multi_source_bfs(start, target, buckets, seeds=5):
    # Pick a few random neighbors of start as alternate launch points
    cand = list(neighbors(start, buckets))
    random.shuffle(cand)
    sources = [start] + cand[:max(0, seeds - 1)]

    visited = set(sources)
    queue = deque((s, [s]) for s in sources)
    while queue:
        word, path = queue.popleft()
        if word == target:
            return path
        for nxt in neighbors(word, buckets):
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))
    return None


# ---------------------------------------------------------------------------
# The race
# ---------------------------------------------------------------------------

STRATEGIES = [
    ("BFS",                  bfs),
    ("Bidirectional BFS",    bidirectional_bfs),
    ("A* (Hamming)",         astar),
    ("Greedy Best-First",    greedy_best_first),
    ("Multi-Source BFS",     multi_source_bfs),
]


def run_race(start, target, buckets):
    """Run every strategy, collect results, return the shortest one."""
    results = []
    print(f"\nRacing {len(STRATEGIES)} strategies from '{start}' → '{target}'...\n")
    print(f"{'Strategy':<22} {'Steps':>6}  Path")
    print("-" * 70)

    for name, fn in STRATEGIES:
        try:
            path = fn(start, target, buckets)
        except Exception as e:
            print(f"{name:<22} {'ERR':>6}  {e}")
            continue

        if path is None:
            print(f"{name:<22} {'—':>6}  no path")
            results.append((None, name, None))
        else:
            steps = len(path) - 1
            preview = " → ".join(path[:6]) + (" …" if len(path) > 6 else "")
            print(f"{name:<22} {steps:>6}  {preview}")
            results.append((steps, name, path))

    # Pick the winner: fewest steps
    valid = [r for r in results if r[0] is not None]
    if not valid:
        return None, None

    best_steps, best_name, best_path = min(valid, key=lambda r: r[0])
    return best_path, (best_name, best_steps)

HISTORY_FILE = os.path.join(BASE, "poople_history.txt")


def log_history(start, path, winner):
    """Append the winning solution to a history file."""
    from datetime import datetime
    name, steps = winner
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path_str = " -> ".join(path)
    line = f"[{timestamp}] {start} -> {TARGET} | {steps} steps | won by: {name}\n"
    line += f"    {path_str}\n"
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print(f"(Couldn't write history: {e})")


def print_winner(path, winner):
    name, steps = winner
    print("\n" + "=" * 70)
    print(f"SHORTEST PATH  —  {steps} step(s)  —  won by: {name}")
    print("=" * 70 + "\n")
    for i, word in enumerate(path):
        marker = "  →" if i > 0 else "   "
        star = "  ⭐" if word == TARGET else ""
        print(f"{marker} {word}{star}")
    print()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    dictionary = get_dictionary()
    print(f"Dictionary: {len(dictionary)} four-letter words.")
    buckets = build_wildcard_buckets(dictionary)

    print("\n=== Poople Game Solver — Race Edition ===")
    print("Every strategy runs, only the shortest result is shown.")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            start = input("Enter starting word: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if start in ("quit", "exit", "q"):
            print("Bye!")
            break
        if len(start) != WORD_LEN or not start.isalpha():
            print(f"Please enter a {WORD_LEN}-letter word.\n")
            continue
        if start not in dictionary:
            print(f"'{start}' isn't in the dictionary.\n")
            continue

        best_path, winner = run_race(start, TARGET, buckets)
        if best_path is None:
            print(f"\nNo path from '{start}' to '{TARGET}'.\n")
        else:
            print_winner(best_path, winner)
            log_history(start, best_path, winner)


if __name__ == "__main__":
    main()
