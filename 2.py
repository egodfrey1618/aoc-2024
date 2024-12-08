from pathlib import Path
import numpy as np

TEST = False
if TEST:
    file = "2_test.txt"
else:
    file = "2.txt"
lines = Path(file).read_text().strip().split("\n")

def parse_report(line):
    return [int(x) for x in line.split()]

def report_is_safe1(report: list[int]) -> bool:
    diffs = [report[i+1] - report[i] for i in range(0, len(report) - 1)]
    diffs = np.array(diffs)

    if diffs[0] < 0:
        diffs *= -1

    if np.any(diffs < 0): return False
    if np.any(diffs == 0): return False
    if np.any(diffs > 3): return False

    # At this point, all are between 1 and 3.
    return True

def report_is_safe2(report: list[int]) -> bool:
    if report_is_safe1(report): return True

    # Try applying the problem dampener.
    # I could do this more intelligently - it's possible to quickly tell if the problem dampener can't help by seeing
    # how many places we have bad diffs - but the problem sizes at this stage are still tiny.
    for i in range(len(report)):
        report_with_one_removed = report[:i] + report[i+1:]
        if report_is_safe1(report_with_one_removed): return True

    return False

reports = [parse_report(line) for line in lines]
print(len([r for r in reports if report_is_safe1(r)]))
print(len([r for r in reports if report_is_safe2(r)]))