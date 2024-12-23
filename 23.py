from pathlib import Path
import itertools
import sys

TEST = False
if TEST:
    text = Path("23_test.txt").read_text().strip()
else:
    text = Path("23.txt").read_text().strip()

graph = {}
all_nodes = set()

def add_link(left, right):
    all_nodes.add(left)
    all_nodes.add(right)

    if left not in graph:
        graph[left] = set()
    if right not in graph:
        graph[right] = set()

    graph[left].add(right)
    graph[right].add(left)


lines = text.split("\n")
for line in lines:
    left, right = line.split("-")
    add_link(left, right)

# Part 1 - count the triangles containing a node starting with t.
triangles = set()

for node in all_nodes:
    if not node.startswith("t"): continue

    for n1 in graph[node]:
        for n2 in graph[node]:
            # If n1 and n2 are connected, this forms a triangle.
            # This is double-counting quite a lot, but we're chucking things
            # into a set so it's fine.
            if n2 in graph[n1]:
                triangles.add(frozenset([node, n1, n2]))

print(len(triangles))

# Part 2 - find the largest clique. An NP-complete problem :O
# Every node has degree 13, so the largest we're going to be able to find is 14.
# And by inspection, most pairs of nodes don't have many things in common. So
# a search with backtracking should be fine.
best = None

def search(current_clique, available_nodes):
    # Part of the recursive search:
    # - The next index we're considering is [index] into [nodes_list]
    # - Our current clique is [current_clique]
    # - Available_nodes is [available_nodes]
    global best

    # Optimisation: Don't bother continuing if there's no way we can beat the best
    if best is not None and len(available_nodes) + len(current_clique) < len(best):
        return

    # Base case: If we're collected all that we can, yield it.
    if len(available_nodes) == 0:
        if best is None or len(best) < len(current_clique):
            best = current_clique.copy()
        return

    # Recursive step. Try both including and not including the next node.
    node = available_nodes.pop()
    
    # Try including it. 
    current_clique.add(node)
    available_nodes1 = available_nodes & graph[node]
    search(current_clique, available_nodes1)
    current_clique.remove(node)

    # Try not including it.
    search(current_clique, available_nodes)

    # And set [available_nodes] back to what it was before.
    available_nodes.add(node)

search(set(), all_nodes)
print(",".join(sorted(list(best))))
