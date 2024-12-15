from dataclasses import dataclass
from pathlib import Path

TEST = False
if TEST:
    text = Path("15_test.txt").read_text().strip()
else:
    text = Path("15.txt").read_text().strip()

lines = text.split("\n")
i = 0
grid = []
while lines[i] != "":
    grid.append(lines[i])
    i += 1
i += 1

moves = "".join(lines[i:])

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        x = self.x + other.x 
        y = self.y + other.y
        return Position(x, y)

    def __sub__(self, other):
        x = self.x - other.x 
        y = self.y - other.y
        return Position(x, y)


# Part 1
# Reparse the grid into sets, it'll be easier to maintain
WALL = 1
BOX = 2
FREE_SPACE = 3
states = {}

robot = None

for x in range(len(grid[0])):
    for y in range(len(grid)):
        position = Position(x, y)
        value = grid[y][x]
        if value == "@":
            robot = position
            states[position] = FREE_SPACE
        elif value == "O":
            states[position] = BOX
        elif value == "#":
            states[position] = WALL
        elif value == ".":
            states[position] = FREE_SPACE
            pass
        else:
            assert False, f"Unknown char: {value}"
assert robot is not None, "Failed to find robot in grid"

def print_grid():
    global states

    for y in range(len(grid)):
        line = []
        for x in range(len(grid[0])):
            state = states[Position(x, y)]
            if state == WALL:
                line.append("#")
            elif state == BOX:
                line.append("O")
            elif state == FREE_SPACE and robot != Position(x, y):
                line.append(".")
            elif state == FREE_SPACE and robot == Position(x, y):
                line.append("@")
            else:
                assert False
        print("".join(line))

def move_robot(direction):
    # Try and move the robot in this direction
    # This function relies on the boundary being covered by walls, so we 
    # don't need to think about what walking outside of the box means.
    global walls
    global boxes
    global robot

    next_square = robot + direction
    if states[next_square] == WALL:
        # Do nothing
        return
    elif states[next_square] == FREE_SPACE:
        # Move
        robot = next_square
        return
    elif states[next_square] == BOX:
        # Walk along to see what the end of this box chain is
        end_square = next_square
        while states[end_square] == BOX:
            end_square = end_square + direction

        if states[end_square] == WALL:
            # No luck, can't push the boxes 
            return
        elif states[end_square] == FREE_SPACE:
            # We can push this chain of boxes
            states[end_square] = BOX
            states[next_square] = FREE_SPACE
            robot = next_square
            return
        else:
            # It shouldn't be BOX, because of the while loop above
            assert False
    else:
        assert False, "BUG: Should have covered all states"

for move in moves:
    if move == "<": direction = Position(-1, 0)
    elif move == ">": direction = Position(1, 0)
    elif move == "^": direction = Position(0, -1)
    elif move == "v": direction = Position(0, 1)
    else: assert False

    move_robot(direction)

total = 0
for x in range(len(grid[0])):
    for y in range(len(grid)):
        if states[Position(x, y)] == BOX:
            total += (100 * y + x)
print(total)

# Part 2 - now we have wide boxes! I've just horribly duplicated things here.
WALL = 1
FREE_SPACE = 3
BOX_LEFT = 4
BOX_RIGHT = 5
states = {}

robot = None

for x in range(len(grid[0])):
    for y in range(len(grid)):
        position_left = Position(2*x, y)
        position_right = Position(2*x + 1, y)

        value = grid[y][x]
        if value == "@":
            robot = position_left
            states[position_left] = FREE_SPACE
            states[position_right] = FREE_SPACE
        elif value == "O":
            states[position_left] = BOX_LEFT
            states[position_right] = BOX_RIGHT
        elif value == "#":
            states[position_left] = WALL
            states[position_right] = WALL
        elif value == ".":
            states[position_left] = FREE_SPACE
            states[position_right] = FREE_SPACE
            pass
        else:
            assert False, f"Unknown char: {value}"
assert robot is not None, "Failed to find robot in grid"

def print_grid():
    global states

    for y in range(len(grid)):
        line = []
        for x in range(2 * len(grid[0])):
            state = states[Position(x, y)]
            if robot == Position(x, y):
                line.append("@")
            elif state == WALL:
                line.append("#")
            elif state == BOX_LEFT:
                line.append("[")
            elif state == BOX_RIGHT:
                line.append("]")
            elif state == FREE_SPACE:
                line.append(".")
            else:
                assert False
        print("".join(line))

def move_robot(direction):
    # Try and move the robot in this direction
    # This function relies on the boundary being covered by walls, so we 
    # don't need to think about what walking outside of the box means.
    global walls
    global boxes
    global robot

    next_square = robot + direction
    if states[next_square] == WALL:
        # Do nothing
        return
    elif states[next_square] == FREE_SPACE:
        # Move
        robot = next_square
        return
    elif states[next_square] in (BOX_LEFT, BOX_RIGHT):
        # This is fun.
        # Find the set of points which are going to need to be affected if we push 
        # this box. 

        stack = set([next_square])
        points = set()
        while stack:
            p = stack.pop()
            if p in points: 
                # Already processed, continue
                continue

            points.add(p)

            if states[p] == WALL:
                # We're done. We can't push things into a wall.
                return
            elif states[p] == FREE_SPACE:
                # We don't need to extend from here.
                pass
            elif states[p] == BOX_LEFT:
                # We both need to push this box, and also include the box 
                # to the right.
                stack.add(p + direction)
                stack.add(p + Position(1, 0))
            elif states[p] == BOX_RIGHT:
                # We both need to push this box, and also include the box 
                # to the left.
                stack.add(p + direction)
                stack.add(p + Position(-1, 0))
            else:
                assert False

        # OK, at this point we have the set of affected points.
        # Any box in this set needs to move forward
        new_values = {}
        for p in points:
            if states[p] in (BOX_LEFT, BOX_RIGHT):
                new_values[p+direction] = states[p]

        # Anything in this set which has not had a box moved onto it needs to be cleared
        for p in points:
            if states[p] in (BOX_LEFT, BOX_RIGHT):
                if p not in new_values:
                    new_values[p] = FREE_SPACE

        for i, j in new_values.items():
            states[i] = j
        robot = next_square
    else:
        assert False, "BUG: Should have covered all states"

for move in moves:
    if move == "<": direction = Position(-1, 0)
    elif move == ">": direction = Position(1, 0)
    elif move == "^": direction = Position(0, -1)
    elif move == "v": direction = Position(0, 1)
    else: assert False

    move_robot(direction)

total = 0
for x in range(2*len(grid[0])):
    for y in range(len(grid)):
        if states[Position(x, y)] == BOX_LEFT:
            total += (100 * y + x)
print(total)
