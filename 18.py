from dataclasses import dataclass
from pathlib import Path

TEST = False
if TEST:
    text = Path("18_test.txt").read_text().strip()
    GRID_SIZE = 6
    COUNT = 12
else:
    text = Path("18.txt").read_text().strip()
    GRID_SIZE = 70
    COUNT = 1024

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Position(x=x, y=y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Position(x=x, y=y)

def in_grid(position):
    if position.x < 0 or position.x > GRID_SIZE: return False
    if position.y < 0 or position.y > GRID_SIZE: return False
    return True

def neighbours(position):
    directions = [
            Position(1, 0),
            Position(-1, 0),
            Position(0, 1),
            Position(0, -1)
    ]

    for d in directions:
        new_position = position + d
        if in_grid(new_position):
            yield new_position

falling_positions = []
for line in text.split("\n"):
    (x, y) = (int(x) for x in line.split(","))
    falling_positions.append(Position(x, y))

# Part 1: Flood fill from the starting position to the end.
start_position = Position(x=0, y=0)
end_position = Position(x=GRID_SIZE, y=GRID_SIZE)
    
def flood_fill(blocked_count):
    blocked = set(falling_positions[:blocked_count])
    
    distance = {start_position: 0}
    boundary = set([start_position])
    count = 0
    while boundary:
        count += 1
        new_boundary = set()
        for position in boundary:
            for neighbour in neighbours(position):
                if neighbour in blocked:
                    continue
                if neighbour in distance:
                    continue
    
                new_boundary.add(neighbour)
    
        boundary = new_boundary
        for position in boundary:
            distance[position] = count
    return distance.get(end_position, None)

print(flood_fill(COUNT))

# Part 2: What's the first byte that blocks us from the exit?
# There's almost certainly a smarter way to do this, but I'm going to be lazy, and 
# binary search to find it.
lower = COUNT
upper = len(falling_positions) 

assert flood_fill(upper) is None

while upper > lower:
    mid = (lower + upper) // 2

    if flood_fill(mid) is None:
        # mid was enough to block off the exit
        upper = mid
    else:
        # lower wasn't enough to block off the exit, so we need to search higher
        lower = mid + 1

assert flood_fill(lower) is None
assert flood_fill(lower - 1) is not None

print(falling_positions[lower-1])
