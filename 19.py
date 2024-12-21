from dataclasses import dataclass
from pathlib import Path
from functools import cache

TEST = False
if TEST:
    text = Path("19_test.txt").read_text().strip()
else:
    text = Path("19.txt").read_text().strip()

lines = text.split("\n")
towels = lines[0].split(", ")
targets = lines[2:]

@cache
def can_create(target):
    if target == '': return True

    for towel in towels:
        if target.startswith(towel):
            rest = target[len(towel):]
            if can_create(rest): 
                return True

    return False

@cache
def ways_to_create(target):
    if target == '': return 1

    total = 0
    for towel in towels:
        if target.startswith(towel):
            rest = target[len(towel):]
            total += ways_to_create(rest)

    return total

print(len([t for t in targets if can_create(t)]))
print(sum(ways_to_create(t) for t in targets))
