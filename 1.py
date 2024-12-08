from pathlib import Path

TEST = False

def parse(line):
    return [int(x) for x in line.split()]

if TEST:
    file = "1_test.txt"
else:
    file = "1.txt"

lines = Path(file).read_text().strip().split("\n")
lines = [parse(line) for line in lines]

# And then rechunk
first = [line[0] for line in lines]
second = [line[1] for line in lines]

# Part 1: Distance between smallest, second-smallest, etc. 
def part1(first, second):
    first = sorted(first)
    second = sorted(second)
    return sum(abs(i-j) for (i, j) in zip(first, second))

print(part1(first, second))

# Part 2: Sum of element in first list times number of times it appears in second list
def part2(first, second):
    counts_in_second = {x: second.count(x) for x in set(second)}
    return sum(x * counts_in_second.get(x, 0) for x in first)

print(part2(first, second))