from dataclasses import dataclass
from pathlib import Path
from functools import cache

TEST = False
if TEST:
    text = Path("11_test.txt").read_text().strip()
else:
    text = Path("11.txt").read_text().strip()

stones = [int(x) for x in text.split()]

@cache
def f(n, k):
    # Let f(n, k) be the number of stones that get produced by number n, after k blinks.
    # Order doesn't matter, so we have this recursive relation - this is textbook dynamic
    # programming.
    if k == 0:
        return 1

    if n == 0:
        return f(1, k-1)

    s = str(n)
    if len(s) % 2 == 0:
        n1 = int(s[:len(s)//2])
        n2 = int(s[len(s)//2:])
        return f(n1, k-1) + f(n2, k-1)

    return f(n * 2024, k - 1)

print(sum(f(s, 25) for s in stones))
print(sum(f(s, 75) for s in stones))
