from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Optional
from itertools import permutations

TEST = False
if TEST:
    text = Path("22_test.txt").read_text().strip()
else:
    text = Path("22.txt").read_text().strip()

initial_states = [int(x) for x in text.split("\n")]

PRUNE_MODULUS = 16777216

def step(x):
    y = x * 64
    x ^= y
    x %= PRUNE_MODULUS

    y = x // 32
    x ^= y
    x %= PRUNE_MODULUS

    y = x * 2048
    x ^= y
    x %= PRUNE_MODULUS

    return x

# Part 1
total = 0
for state in initial_states:
    for _ in range(2000):
        state = step(state)
    total += state
print(total)

# Part 2
# A "key" is a tuple of 4 digits
# Nothing intelligent - just loop over each stream of states, calculating what
# each key would give for this monkey, and then sum over each key at the end.
keys_to_prices = {}

for state_index, state in enumerate(initial_states):
    print(state_index, len(initial_states))
    d = {}
    key = (None, None, None, None)
    last_number = state % 10

    for i in range(2000):
        state = step(state)
        number = state % 10

        # Update key
        diff = number - last_number
        key = tuple(list(key)[1:] + [diff])

        # Note down this key (as long as it's complete)
        if key not in d and None not in key:
            d[key] = number

        last_number = number

    for key, value in d.items():
        if key not in keys_to_prices:
            keys_to_prices[key] = [None] * len(initial_states)
        keys_to_prices[key][state_index] = value

best = None
for key, values in keys_to_prices.items():
    s = sum(v for v in values if v is not None)
    if best is None or s > best[1]:
        best = (key, s)
        print(best)
