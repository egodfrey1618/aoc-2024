from pathlib import Path
from dataclasses import dataclass

TEST = False
if TEST:
    text = Path("5_test.txt").read_text().strip().split("\n")
else:
    text = Path("5.txt").read_text().strip().split("\n")

@dataclass(frozen=True)
class Problem:
    rules: dict[int, set[int]]
    reports: list[int]

def parse(text): 
    rules = []
    reports = []

    for line in text:
        if "|" in line:
            rules.append(tuple(int(x) for x in line.split("|")))
        elif line == "":
            pass
        else:
            reports.append([int(x) for x in line.split(",")])

    # And then put rules into a nicer format to work with
    rules_dict = {}
    for (in_, out) in rules:
        if in_ not in rules_dict: rules_dict[in_] = set()
        rules_dict[in_].add(out)

    return Problem(rules=rules_dict, reports=reports)

problem = parse(text)

# Part 1
def check_report(problem, report):
    for j in range(1, len(report)):
        for i in range(0, j):
            if report[j] in problem.rules and report[i] in problem.rules[report[j]]:
                return False
    return True

valid_reports = [r for r in problem.reports if check_report(problem, r)]

def answer(reports):
    return sum(r[len(r) // 2] for r in reports)

print(answer(valid_reports))

# Part 2 - now we have to order the reports, so topological sort. And I guess the problem's been cooked up so 
# there's a unique valid ordering?
def sort_report(problem, report):
    # Base case
    if report == []: return []

    # Step 1: Find a node which can be at the start.
    possible_start_nodes = set(report)

    for c in report:
        nodes_that_must_come_after = problem.rules.get(c, set()) 
        possible_start_nodes -= nodes_that_must_come_after

    # We've been told there's a unique solution, so...
    assert len(possible_start_nodes) == 1

    start_node = possible_start_nodes.pop()

    # Using list for reports isn't very efficient - I ought to be using something different to recurse - but
    # whatever.
    i = report.index(start_node)
    report.pop(i)

    return [start_node] + sort_report(problem, report)

invalid_reports = [r for r in problem.reports if not check_report(problem, r)]
sorted_reports = [sort_report(problem, report) for report in invalid_reports]
print(answer(sorted_reports))