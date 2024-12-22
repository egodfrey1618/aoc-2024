from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Optional

TEST = False
if TEST:
    text = Path("21_test.txt").read_text().strip()
else:
    text = Path("21.txt").read_text().strip()
targets = text.split("\n")

UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4
GO = 5
buttons = [UP, DOWN, LEFT, RIGHT, GO]


def pretty_button(b):
    # just for debugging
    return ["UP", "DOWN", "LEFT", "RIGHT", "GO"][b - 1]


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Position(x=x, y=y)


def position_on_directional_robot(p: Position):
    l = [[None, UP, GO], [LEFT, DOWN, RIGHT]]

    if p.y >= len(l):
        return None
    if p.x >= len(l[0]):
        return None
    if p.x < 0:
        return None
    if p.y < 0:
        return None

    return l[p.y][p.x]


def position_on_number_robot(p: Position) -> Optional[str]:
    l = ["789", "456", "123", [None, "0", "A"]]
    if p.y >= len(l):
        return None
    if p.x >= len(l[0]):
        return None
    if p.x < 0:
        return None
    if p.y < 0:
        return None

    return l[p.y][p.x]


def move_robot(robot, button):
    directions = {
        UP: Position(x=0, y=-1),
        DOWN: Position(x=0, y=1),
        LEFT: Position(x=-1, y=0),
        RIGHT: Position(x=1, y=0),
    }
    direction = directions[button]

    new_robot = robot + direction
    return new_robot


# Part 1, naive solution. Flood fill to figure out minimum distance
# between states where all the directional robots are pointing at "GO", and
# where the last one is. Superceded by solution to part 2.
@dataclass(frozen=True)
class State:
    directional_robots: tuple[Position]
    number_robot: Position


def move(state: State, button) -> Optional[State]:
    """
    How the state progresses if I press a button controlling the first robot.
    """

    def move_directional_robot(robot_index, button):
        robot = state.directional_robots[robot_index]

        new_robot = move_robot(robot, button)

        # Check the robot's in bounds.
        if position_on_directional_robot(new_robot) is None:
            return None

        new_robots = tuple(
            r if i != robot_index else new_robot
            for (i, r) in enumerate(state.directional_robots)
        )

        return State(directional_robots=new_robots, number_robot=state.number_robot)

    if button in (UP, DOWN, LEFT, RIGHT):
        # Simple case - I'm pressing a move button, so we're just moving the first robot.
        return move_directional_robot(0, button)

    elif button == GO:
        # OK, so I'm hitting GO. Some prefix of the robots are pointing to GO - let's say
        # state.directional_robots[:i] are pointing at GO.
        # Then state.directional_robots[i] is pointing at a direction
        # and state.directional_robots[i+1] will then move by that direction.

        # Find the first directional robot that isn't pointing to 'A' (might be None)
        robots_not_pointing_to_go = [
            (i, robot)
            for (i, robot) in enumerate(state.directional_robots)
            if position_on_directional_robot(robot) != GO
        ]

        if robots_not_pointing_to_go == []:
            # All the robots are pointing to GO! So we're going to press the number_robot.
            # This doesn't move the state at all
            return state
        else:
            # One of the intermediate directional robots isn't pointing to GO.
            (first_robot_index, first_robot_position) = robots_not_pointing_to_go[0]
            this_button = position_on_directional_robot(first_robot_position)
            assert this_button is not GO
            if this_button is None:
                return None

            if first_robot_index != len(state.directional_robots) - 1:
                # We're pressing an intermediate robot.
                return move_directional_robot(first_robot_index + 1, this_button)

            else:
                # All but the last directional robot is GO, so we're moving the numberpad robot.
                new_robot = move_robot(state.number_robot, this_button)
                if new_robot is None:
                    return None

                # Check the robot's in bounds.
                if position_on_number_robot(new_robot) is None:
                    return None

                return State(
                    directional_robots=state.directional_robots, number_robot=new_robot
                )


DIRECTIONAL_ROBOT_COUNT = 2

a_position_directional = Position(2, 0)
a_position_number = Position(2, 3)


def character_to_position_on_number_robot(c):
    for x in range(0, 3):
        for y in range(0, 4):
            p = Position(x, y)
            if position_on_number_robot(p) == c:
                return p


def target_state_for_character(c):
    """
    Returns state where all directional robots point at 'A',
    and the number robot points at character [c].
    """
    number_robot_position = character_to_position_on_number_robot(c)
    return State(
        directional_robots=tuple(
            a_position_directional for _ in range(DIRECTIONAL_ROBOT_COUNT)
        ),
        number_robot=number_robot_position,
    )


def distance(state1, state2):
    visited = set([state1])
    boundary = set([state1])

    count = 0
    while boundary and (state2 not in visited):
        count += 1
        new_boundary = set()

        for s in boundary:
            for button in buttons:
                new_state = move(s, button)
                if new_state is not None and new_state not in visited:
                    new_boundary.add(new_state)

        boundary = new_boundary
        visited |= boundary

    if state2 in visited:
        return count
    else:
        return None


total = 0
for target in targets:
    state = target_state_for_character("A")
    cost = 0

    for c in target:
        # We want to move to the next state.
        state2 = target_state_for_character(c)
        cost += distance(state, state2)
        cost += 1  # for pressing GO to get the character

        state = state2
    print(target, cost)

    total += cost * int(target[:-1])
print(total)

# Part 2, harder - now we need to do something smarter!
# Let's define f(i, button1, button2) to be the distance between these states:
# Everything in directional_robots[:i] points to GO
# directional_robots[i] starts at button1, ends at button2
#
# Then there's a fairly simple recursive relation for this.
#
# This is pretty much disjoint from my solution above.
PART2_ROBOT_COUNT = 25


def paths_between_positions(position1, position2, f):
    """
    Calculate up to two paths between [position1] and [position2], such that
    f(p) is not None for everything along the path. Returns the buttons that
    you've have to press to move between them.

    We only need to consider paths that go all one way first then the other.
    E.g. we need to consider RRRUUU and UUURRR, but not interleaving - that
    can't be quicker.
    """
    if position1 == position2:
        yield []
        return

    x1 = position1.x
    y1 = position1.y
    x2 = position2.x
    y2 = position2.y

    if x1 < x2:
        horizontal_dir = RIGHT
    else:
        horizontal_dir = LEFT

    horizontal_path = [horizontal_dir] * abs(x2 - x1)

    if y1 < y2:
        vertical_dir = DOWN
    else:
        vertical_dir = UP

    vertical_path = [vertical_dir] * abs(y2 - y1)

    path1 = horizontal_path + vertical_path
    path2 = vertical_path + horizontal_path

    def path_valid(path):
        p = position1
        valid = True

        for x in path:
            p = move_robot(p, x)
            if f(p) is None:
                return False
        return True

    for path in [path1, path2]:
        if path_valid(path):
            yield path


button_to_position = {}
for x in range(3):
    for y in range(2):
        p = Position(x=x, y=y)
        b = position_on_directional_robot(p)
        if b is not None:
            button_to_position[b] = p

numberpad_to_position = {}
for x in range(3):
    for y in range(4):
        p = Position(x=x, y=y)
        b = position_on_number_robot(p)
        if b is not None:
            numberpad_to_position[b] = p


def best_path(key1, key2, key_to_position, position_to_key, prior_robot_costs):
    # Recursion. Using the cost of moving the prior robot from
    # spot to spot, how long does it take to move from key1
    # to key2? This is always calculating moving from:
    #
    # (GO, GO, ...., GO, key1)
    # to
    # (GO, GO, ...., GO, key2)
    #
    # so we need to make sure the prior robot moves back to GO afterwards.
    if key1 == key2:
        return 0

    p1 = key_to_position[key1]
    p2 = key_to_position[key2]
    paths = list(paths_between_positions(p1, p2, position_to_key))

    if len(paths) == 0:
        print(key1, key2)
        assert False

    assert len(paths) >= 1

    best_cost = None

    for path in paths:
        cost = 0
        last_key = GO

        for key in path:
            cost += prior_robot_costs[(last_key, key)]
            cost += 1  # for pressing this key
            last_key = key

        # For moving the prior robot back to GO
        cost += prior_robot_costs[(key, GO)]

        if best_cost is None or best_cost > cost:
            best_cost = cost
    return best_cost


# Base case: for the keypad I'm pressing, doesn't cost anything
# to move my finger.
distances = {}
for button1 in buttons:
    for button2 in buttons:
        distances[(button1, button2)] = 0

for _ in range(PART2_ROBOT_COUNT):
    # Construct the new distances based on the old
    new_distances = {}

    for button1 in buttons:
        for button2 in buttons:
            new_distances[(button1, button2)] = best_path(
                button1,
                button2,
                button_to_position,
                position_on_directional_robot,
                distances,
            )
    distances = new_distances

numberpad_distances = {}
for x1 in "0123456789A":
    for x2 in "0123456789A":
        numberpad_distances[(x1, x2)] = best_path(
            x1, x2, numberpad_to_position, position_on_number_robot, distances
        )

total = 0
for target in targets:
    state = target_state_for_character("A")
    cost = 0
    prev_button = "A"

    for c in target:
        cost += numberpad_distances[(prev_button, c)]
        cost += 1  # for pressing GO to get the character

        prev_button = c
    print(target, cost)

    total += cost * int(target[:-1])
print(total)
