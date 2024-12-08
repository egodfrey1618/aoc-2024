from pathlib import Path

TEST = False
if TEST:
    grid = Path("6_test.txt").read_text().strip().split("\n")
else:
    grid = Path("6.txt").read_text().strip().split("\n")

grid = [list(line) for line in grid]

def get_value(grid, position):
    (x, y) = position
    if y >= len(grid) or y < 0: return None
    if x >= len(grid[y]) or x < 0: return None
    return grid[y][x]

def set_value(grid, position, value):
    (x, y) = position
    grid[y][x] = value

def add_direction(position, direction):
    (x, y) = position
    (a, b) = direction
    return (x+a, y+b)

UP = (0, -1)
RIGHT = (1, 0)
DOWN = (0, 1)
LEFT = (-1, 0)

def rotate_right(position):
    if position == UP:
        return RIGHT
    elif position == RIGHT:
        return DOWN
    elif position == DOWN:
        return LEFT
    elif position == LEFT:
        return UP
    else:
        raise Exception("Unknown direction")

grid_positions = [(x, y) for x in range(0, len(grid[0])) for y in range(len(grid))]

# Find the guard position, save it, and replace it on the grid.
possible_guard_positions = [p for p in grid_positions if get_value(grid, p) == "^"]
assert len(possible_guard_positions) == 1
initial_guard_position = possible_guard_positions[0]
set_value(grid, initial_guard_position, ".")
initial_guard_direction = UP

# Part 1: Map out where the guard goes, until they leave the grid.
def run_simulation(grid, guard_position, guard_direction):
    """
    Run a simulation. Returns a set of visited positions, and a boolean saying whether we went
    into a loop or not.
    """
    visited_states = set()

    while True:
        state = (guard_position, guard_direction)
        if state in visited_states:
            # We've looped!
            return visited_states, True

        visited_states.add(state)

        new_position = add_direction(guard_position, guard_direction)
        new_position_value = get_value(grid, new_position)
    
        if new_position_value is None:
            # Guard has walked out of grid. 
            return visited_states, False
    
        if new_position_value == "#":
            # Guard has walked into something. Don't move, instead rotate.
            guard_direction = rotate_right(guard_direction)
        
        if new_position_value == ".":
            # Guard can move!
            guard_position = new_position

states, looped = run_simulation(grid, initial_guard_position, initial_guard_direction)
if looped:
    raise Exception("We were told Part 1 would exit the grid")
# Print the number of positions visited. (Not the number of states.)
visited_positions = set(s[0] for s in states)
print(len(visited_positions))

# Part 2: Interesting. How many places can we put 1 obstacle to make the guard go into a loop?
# Lazy - brute-force each solution, and use the same loop code above. We only need to consider places on the guard's path. 
# This takes ~7s to run on my laptop - there's probably a smarter way to do this, but I'm happy enough with this.
count = 0

for position in visited_positions:
    if position != initial_guard_position:
        set_value(grid, position, "#")
        _, looped = run_simulation(grid, initial_guard_position, initial_guard_direction)
        if looped:
            count += 1
        set_value(grid, position, ".")
print(count)

