from pathlib import Path
from dataclasses import dataclass

TEST = False
if TEST:
    grid = Path("8_test.txt").read_text().strip().split("\n")
else:
    grid = Path("8.txt").read_text().strip().split("\n")

grid = [list(line) for line in grid]

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        return Position(x=self.x+other.x, y=self.y+other.y)

    def __sub__(self, other):
        return Position(x=self.x-other.x, y=self.y-other.y)
    
    def __rmul__(self, other):
        assert type(other) == int
        return Position(x=self.x*other, y=self.y*other)

    
def position_in_grid(grid, position):
    if position.x < 0 or position.x >= len(grid[0]): return False
    if position.y < 0 or position.y >= len(grid): return False
    return True

# First step: Find where the antennas are, and clear them out from the grid.
antennas = {}

for y in range(len(grid)):
    for x in range(len(grid[y])):
        if grid[y][x] != ".":
            key = grid[y][x]
            if key not in antennas: antennas[key] = []
            antennas[key].append(Position(x=x, y=y))

# Part 1: Find the antinodes.
antinodes = set()

for key, antennas_with_key in antennas.items():
    for i in range(len(antennas_with_key)):
        for j in range(i+1, len(antennas_with_key)):
            antenna1 = antennas_with_key[i]
            antenna2 = antennas_with_key[j]

            antinodes.add(antenna1 + (antenna1 - antenna2))
            antinodes.add(antenna1 + -2*(antenna1 - antenna2))

antinodes = [a for a in antinodes if position_in_grid(grid, a)]
print(len(antinodes))

# Part 2: Find the antinodes again. This time anything in line counts.
antinodes = set()

for key, antennas_with_key in antennas.items():
    for i in range(len(antennas_with_key)):
        for j in range(i+1, len(antennas_with_key)):
            antenna1 = antennas_with_key[i]
            antenna2 = antennas_with_key[j]

            # Under the new definition, these are always in.
            antinodes.add(antenna1)
            antinodes.add(antenna2)

            # Count forwards (in the direction of antenna1)
            k = 0
            while True:
                k += 1
                position = antenna1 + k * (antenna1 - antenna2)
                if position_in_grid(grid, position):
                    antinodes.add(position)
                else:
                    break

            # Count the ones backwards (in the direction of antenna2)
            k = -1
            while True:
                k -= 1
                position = antenna1 + k * (antenna1 - antenna2)
                if position_in_grid(grid, position):
                    antinodes.add(position)
                else:
                    break
print(len(antinodes))
