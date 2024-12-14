from dataclasses import dataclass
from pathlib import Path
from functools import reduce
from PIL import Image
import re

TEST = False
if TEST:
    text = Path("14_test.txt").read_text().strip()
    width = 11
    height = 7
else:
    text = Path("14.txt").read_text().strip()
    width = 101
    height = 103

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Position(x=x, y=y)

    def make_within_grid(self, width, height):
        x = self.x % width
        y = self.y % height
        return Position(x=x, y=y)

@dataclass
class Robot:
    position: Position
    velocity: Position

robots = []
lines = text.split("\n")
for line in lines:
    position = Position(*(int(x) for x in re.findall(r"p=(-?[0-9]*),(-?[0-9]*)", line)[0]))
    velocity = Position(*(int(x) for x in re.findall(r"v=(-?[0-9]*),(-?[0-9]*)", line)[0]))
    robot = Robot(position, velocity)
    robots.append(robot)

MAX_STEPS = width * height

for i in range(1, MAX_STEPS + 1):
    for robot in robots:
        robot.position += robot.velocity
        robot.position = robot.position.make_within_grid(width, height)

    positions = set(robot.position for robot in robots)

    # Count the number of robots in each quadrant
    counts = {}
    for robot in robots:
        in_left = robot.position.x < width // 2
        in_right = robot.position.x > width // 2
        in_top = robot.position.y < height // 2
        in_bottom = robot.position.y > height // 2
    
        # Ignore robots exactly on a half-way boundary
        if not in_left and not in_right:
            continue
        if not in_top and not in_bottom:
            continue
    
        key = (in_left, in_top)
        counts[key] = counts.get(key, 0) + 1

    if i == 100:
        print("Solution for part 1:", reduce(lambda x, y: x*y, counts.values()))

    # Hacky heuristic for "this doesn't look very random" - if not, write out the image
    # and display it.
    if max(counts.values()) / (min(counts.values()) + 1) > 5:
        print(f"{i} looks unbalanced, writing this out out to check")

        im = Image.new(mode="RGB", size=(width, height))
        for x in range(width):
            for y in range(height):
                if Position(x, y) in positions:
                    im.putpixel((x, y), (0, 255, 0))
                else:
                    im.putpixel((x, y), (60, 60, 60))

        im.save(f"robots/picture_{i}.bmp")
