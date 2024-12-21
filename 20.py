from dataclasses import dataclass
from pathlib import Path

TEST = False
if TEST:
    text = Path("20_test.txt").read_text().strip()
else:
    text = Path("20.txt").read_text().strip()

grid = [list(l) for l in text.split("\n")]
width = len(grid[0])
height = len(grid)

def get_grid(p):
    x = p.x
    y = p.y
    if x < 0 or x > width:
        return None
    if y < 0 or x > height:
        return None
    return grid[y][x]

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Position(x=x, y=y)

    def manhattan_distance(self, other):
        d_x = self.x - other.x
        d_y = self.y - other.y
        return abs(d_x) + abs(d_y)

def neighbours(position):
    directions = [
            Position(1, 0),
            Position(-1, 0),
            Position(0, 1),
            Position(0, -1)
    ]

    for d in directions:
        new_position = position + d
        if get_grid(new_position) == '.':
            yield new_position

# Find the 'S', and the path from the 'S' to the 'E' - we're told there's a unique path.
for x in range(len(grid[0])):
    for y in range(len(grid)):
        p = Position(x=x, y=y)
        if get_grid(p) == 'S':
            start_position = p
            grid[y][x] = '.'
        elif get_grid(p) == 'E':
            end_position = p
            grid[y][x] = '.'

path = {start_position: 0}
last_position = start_position
while last_position != end_position:
    next_ = [x for x in neighbours(last_position) if x not in path]
    assert len(next_) == 1
    next_ = next_[0]
    path[next_] = len(path)
    last_position = next_

# Part 1: How many jumps of length 2 save at least 100 picoseconds?
directions = [
        Position(2, 0),
        Position(-2, 0),
        Position(0, 2),
        Position(0, -2)
]

count = 0
for point in path:
    for d in directions:
        next_point = point + d
        if next_point in path:
            time_saved = path[next_point] - path[point] - 2
            if time_saved >= 100:
                count += 1
print(count)

# Part 2: How many jumps of length <= 20 save at least 100 picoseconds?
# Mostly just iterate through pairs of points, but with a little optimisation
# to avoid having to check everything. (I'm pretty sure there's a smarter divide
# and conquer thing we can do, which would be sub-quadratic.)
JUMP_LENGTH = 20
TIME_SAVED = 100

points_sorted_by_x = list(path)
points_sorted_by_x.sort(key=lambda p: p.x)

left_pointer = 0

count = 0
for i, point in enumerate(points_sorted_by_x):
    for j in range(i+1, len(points_sorted_by_x)):
        other_point = points_sorted_by_x[j]

        if other_point.x > point.x + JUMP_LENGTH:
            # We can stop - no points will be near enough.
            break

        if path[point] <= path[other_point]:
            first_point = point
            second_point = other_point
        else:
            first_point = other_point
            second_point = point

        distance = first_point.manhattan_distance(second_point)
        if distance > JUMP_LENGTH: continue

        time_saved = path[second_point] - path[first_point] - distance
        if time_saved >= TIME_SAVED:
            count += 1
print(count)
