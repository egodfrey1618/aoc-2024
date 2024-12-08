from pathlib import Path
from dataclasses import dataclass

TEST = False
if TEST:
    lines = Path("7_test.txt").read_text().strip().split("\n")
else:
    lines = Path("7.txt").read_text().strip().split("\n")

@dataclass(frozen=True)
class Problem:
    target: int
    numbers: list[int]

def parse(line: str) -> Problem:
    target = int(line.split(":")[0])
    numbers = [int(x) for x in line.split(":")[1].strip().split(" ")]
    return Problem(target=target, numbers=numbers)

problems = [parse(line) for line in lines]

def concat(x, y):
    return int(str(x) + str(y))

def reachable_numbers(problem, allow_concat):
    i = 0
    numbers = set([problem.numbers[0]])

    while i + 1 < len(problem.numbers):
        i += 1
        new_numbers = set()
        next_number = problem.numbers[i]
        for value in numbers:
            new_numbers.add(value + next_number)
            new_numbers.add(value * next_number)

            if allow_concat:
                new_numbers.add(concat(value, next_number))

        # Optimisation: Don't bother considering anything above target. None of our operations can make numbers smaller.
        numbers = set(x for x in new_numbers if x <= problem.target)

    return numbers

# Not too slow - this takes ~2.5s in Python. There are lots of other optimisations I could do here, some ideas:
# - Working backwards, we might be able to deduce some of the last few operations have to be '+'
# - We might be able to bound things better to know that we can't use '+' after some point, which would help. 
# But this works well enough.
print(sum([p.target for p in problems if p.target in reachable_numbers(p, allow_concat=False)]))
print(sum([p.target for p in problems if p.target in reachable_numbers(p, allow_concat=True)]))