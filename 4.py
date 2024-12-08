from pathlib import Path

TEST = False
if TEST:
    grid = Path("4_test.txt").read_text().strip().split("\n")
else:
    grid = Path("4.txt").read_text().strip().split("\n")

directions = [(x, y) for x in range(-1, 2) for y in range(-1, 2) if (x, y) != (0, 0)]
starting_positions = [(x, y) for x in range(0, len(grid[0])) for y in range(len(grid))]

def get_value(grid, position):
    (x, y) = position
    if y >= len(grid) or y < 0: return None
    if x >= len(grid[y]) or x < 0: return None
    return grid[y][x]

def add_direction(position, direction):
    (x, y) = position
    (a, b) = direction
    return (x+a, y+b)

# Search 1: How many XMASs can we find (in any direction?)
def find(target, starting_positions, directions):
    for start in starting_positions:
        for direction in directions:
            l = []
            position = start

            # Could short-circuit here, but I'm lazy, and this is already very fast.
            while len(l) < len(target):
                l.append(get_value(grid, position))
                position = add_direction(position, direction)

            if None not in l and "".join(l) == target:
                yield (start, direction)

print(len(list(find("XMAS", starting_positions, directions))))

# Search 2: How many X-MASs can we find (so a "star" made up of MAS?)

# Reuse solution to part 1 to start off with, to find 'MAS'. This isn't the most efficient way, but it works!
diagonal_directions = [d for d in directions if d[0] != 0 and d[1] != 0]
mas_solutions = list(find("MAS", starting_positions, diagonal_directions))

# And then walk over them, seeing how many overlap at the 'A'
a_positions = [add_direction(position, direction) for (position, direction) in mas_solutions]
a_positions_count = {}
for position in a_positions:
    a_positions_count[position] = a_positions_count.get(position, 0) + 1

print(len(list(x for x, y in a_positions_count.items() if y == 2)))



