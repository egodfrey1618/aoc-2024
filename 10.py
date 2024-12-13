from pathlib import Path

TEST = False
if TEST:
    text = Path("10_test.txt").read_text().strip()
else:
    text = Path("10.txt").read_text().strip()

grid = [[int(x) for x in line] for line in text.split("\n")]

def get_value(grid, position):
    (x, y) = position
    if y >= len(grid) or y < 0: return None
    if x >= len(grid[y]) or x < 0: return None
    return grid[y][x]

positions = [(x, y) for x in range(len(grid[0])) for y in range(len(grid))]

nines = [p for p in positions if get_value(grid, p) == 9]

# Step 1: BFS out from the 9s, tracking how many 9s we can reach
def neighbours_one_level_up(grid, position):
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    current_height = get_value(grid, position)

    for d in dirs:
        neighbour = (d[0] + position[0], d[1] + position[1])
        if get_value(grid, neighbour) == current_height + 1:
            yield neighbour

reachable_nines = {p: set([p]) for p in nines}

for height in range(8, -1, -1):
    next_nines = {}
    for p in positions:
        if get_value(grid, p) == height:
            for neighbour in neighbours_one_level_up(grid, p):
                if p not in next_nines: next_nines[p] = set()

                next_nines[p] |= reachable_nines.get(neighbour, set())

    reachable_nines = next_nines

print(sum(len(x) for x in reachable_nines.values()))

# Step 2: Very similar, but tracking the total number of paths to 9s, rather than how many we can reach
score = {p: 1 for p in nines}

for height in range(8, -1, -1):
    next_score = {}
    for p in positions:
        if get_value(grid, p) == height:
            for neighbour in neighbours_one_level_up(grid, p):
                if p not in next_score: next_score[p] = 0

                next_score[p] += score.get(neighbour, 0)

    score = next_score

print(sum(score.values()))

