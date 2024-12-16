from dataclasses import dataclass
from pathlib import Path

TEST = False
if TEST:
    text = Path("16_test.txt").read_text().strip()
else:
    text = Path("16.txt").read_text().strip()

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

def set_grid(p, value):
    grid[p.y][p.x] = value

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

@dataclass(frozen=True)
class State:
    position: Position
    direction: Position

# Find the start and end, save them, and clear those spots
for x in range(width):
    for y in range(height):
        p = Position(x, y)
        if get_grid(p) == "S":
            start_position = p
            start_direction = Position(1, 0) # We're told the reindeer faces east
            start_state = State(position=start_position, direction=start_direction)
            set_grid(p, ".")

        elif get_grid(p) == "E":
            end_position = p
            set_grid(p, ".")

        else:
            pass
         
def next_states(state, reverse=False):
    # Stepping forward
    if reverse:
        next_ = state.position - state.direction
    else:
        next_ = state.position + state.direction
    if get_grid(next_) == ".":
        yield State(next_, state.direction), 1
         
    # Or turning
    TURNING_COST =  1000
    if state.direction.x != 0:
        yield State(state.position, Position(0, 1)), TURNING_COST
        yield State(state.position, Position(0, -1)), TURNING_COST

    if state.direction.y != 0:
        yield State(state.position, Position(1, 0)), TURNING_COST
        yield State(state.position, Position(-1, 0)), TURNING_COST

# Part 1: Just Dijkstra, where the states on our graph are "position+direction".
best_distances = {}
possible_distances = {start_state: 0}

while possible_distances:
    best = None
    # This ought to be a heap or something, which would be O(log n) to pop from.
    for state, distance in possible_distances.items():
        if best == None:
            best = (state, distance)
        else:
            (current, current_distance) = best
            if distance < current_distance:
                best = (state, distance)

    (state, distance) = best
    possible_distances.pop(state)
    best_distances[state] = distance

    # Add all neighbours of [state] to [possible_distances]
    for neighbour, cost in next_states(state):
        if neighbour in best_distances:
            continue

        if neighbour not in possible_distances or distance + cost < possible_distances[neighbour]:
            possible_distances[neighbour] = distance + cost

endings = [(state, score) for state, score in best_distances.items() if state.position == end_position]
endings.sort(key=lambda x: x[1])
ending = endings[0]
print(ending[1])

# Part 2: Work backwards to find all possible paths
path_elements = set([ending[0]])
stack = [ending[0]]

while stack:
    state = stack.pop()
    for neighbour, cost in next_states(state, reverse=True):
        if best_distances[neighbour] + cost == best_distances[state]:
            # One way to get to [state] is by going through [neighbour]
            if neighbour not in path_elements:
                path_elements.add(neighbour)
                stack.append(neighbour)

positions = {state.position for state in path_elements}
print(len(positions))
