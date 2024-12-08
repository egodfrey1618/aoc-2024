from pathlib import Path
import re

TEST = False
if TEST:
    file = "3_test.txt"
else:
    file = "3.txt"
text = Path(file).read_text()

instructions = re.findall("(mul\(([0-9]*),([0-9]*)\)|do\(\)|don't\(\))", text)

def run(instructions, ignore_active):
    total = 0
    active = True
    for instruction in instructions:
        if instruction[0] == "do()":
            active = True
        elif instruction[0] == "don't()":
            active = False
        elif instruction[0].startswith("mul") and (active or ignore_active):
            total += int(instruction[1]) * int(instruction[2])
    return total

# Part 1:
print(run(instructions, ignore_active=True))

# Part 2:
print(run(instructions, ignore_active=False))