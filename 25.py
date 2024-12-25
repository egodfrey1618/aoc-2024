from pathlib import Path

TEST = False
if TEST:
    text = Path("25_test.txt").read_text().strip()
else:
    text = Path("25.txt").read_text().strip()

lines = text.split("\n")
chunks = []
recent_chunk = []
for line in lines:
    if line == "":
        chunks.append(recent_chunk)
        recent_chunk = []
    else:
        recent_chunk.append(line)
if recent_chunk: chunks.append(recent_chunk)

# Basic sanity-checking - all the chunks are the same shape.
assert len(set(len(chunk) for chunk in chunks)) == 1
assert len(set(len(chunk[0]) for chunk in chunks)) == 1

height = len(chunks[0])
width = len(chunks[0][0])

def parse_chunk(chunk):
    if "#" not in chunk[0]:
        type_ = "key"
    elif "." not in chunk[0]:
        type_ = "lock"
    else:
        assert False

    result = []
    for i in range(width):
        column = [line[i] for line in chunk]
        result.append(sum(1 if c == "#" else 0 for c in column))
    return (type_, result)

keys = []
locks = []
for chunk in chunks:
    (type_, sizes) = parse_chunk(chunk)
    if type_ == "key":
        keys.append(sizes)
    elif type_ == "lock":
        locks.append(sizes)
    else:
        assert False

count = 0
for key in keys:
    for lock in locks:
        if max(i+j for (i, j) in zip(key, lock)) <= height:
            count += 1
print(count)
