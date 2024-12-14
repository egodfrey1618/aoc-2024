from dataclasses import dataclass
from pathlib import Path
import re

TEST = False
if TEST:
    text = Path("13_test.txt").read_text().strip()
else:
    text = Path("13.txt").read_text().strip()

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Position(x=x, y=y)

    def __mul__(self, n):
        x = n*self.x
        y = n*self.y
        return Position(x=x, y=y)

    def __rmul__(self, n):
        return self * n

# Urgh, annoying parsing!
@dataclass
class Problem:
    button_a: tuple[int, int]
    button_b: tuple[int, int]
    prize: tuple[int, int]

lines = text.split("\n")
problems = []
for i in range(0, len(lines), 4):
    assert "Button A" in lines[i]
    assert "Button B" in lines[i+1]
    assert "Prize" in lines[i+2]

    button_a = Position(*(int(x) for x in re.findall(r"X\+([0-9]*), Y\+([0-9]*)", lines[i])[0]))
    button_b = Position(*(int(x) for x in re.findall(r"X\+([0-9]*), Y\+([0-9]*)", lines[i+1])[0]))
    prize = Position(*(int(x) for x in re.findall(r"X=([0-9]*), Y=([0-9]*)", lines[i+2])[0]))

    problem = Problem(button_a, button_b, prize)
    problems.append(problem)

def solve(problem):
    # (a b
    #  c d)
    # is the matrix such that when applied to (num_a, num_b), it gives (pos_x, pos_y)
    (a, b, c, d) = (problem.button_a.x, problem.button_b.x, problem.button_a.y, problem.button_b.y)
    determinant = a*d - b*c

    # Invert it, and apply to the prize to recover what the position should be
    (a_inv, b_inv, c_inv, d_inv) = (d, -b, -c, a)

    unscaled_inverse_x = a_inv * problem.prize.x + b_inv * problem.prize.y
    unscaled_inverse_y = c_inv * problem.prize.x + d_inv * problem.prize.y

    if unscaled_inverse_x % determinant == 0 and unscaled_inverse_y % determinant == 0:
        num_a = unscaled_inverse_x // determinant
        num_b = unscaled_inverse_y // determinant
        return (num_a, num_b)
    else:
        return None

# Part 1
total = 0

for problem in problems:
    solution = solve(problem)
    if solution is not None:
        total += (3*solution[0] + solution[1])
print(total)

# Part 2
total = 0
shift = Position(x=10_000_000_000_000, y=10_000_000_000_000)

for p in problems:
    p.prize = p.prize + shift

for problem in problems:
    solution = solve(problem)
    if solution is not None:
        total += (3*solution[0] + solution[1])
print(total)
