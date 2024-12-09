from dataclasses import dataclass
from pathlib import Path

TEST = False
if TEST:
    text = Path("9_test.txt").read_text().strip()
else:
    text = Path("9.txt").read_text().strip()

lengths = [int(x) for x in text]
file_lengths = lengths[::2]
free_space_lengths = lengths[1::2]
assert len(file_lengths) == len(free_space_lengths) + 1

# Part 1: Create the disk as a flat representation
BLANK = -1

size = sum(lengths)
disk = [BLANK] * size

pointer = 0
for i in range(len(file_lengths)):
    for _ in range(file_lengths[i]):
        disk[pointer] = i
        pointer += 1

    if i != len(file_lengths) - 1:
        pointer += free_space_lengths[i]
assert pointer == len(disk)

# Part 1: Do the compaction (with 2 pointers)
left_pointer = 0
right_pointer = len(disk) - 1

while left_pointer < right_pointer:
    if disk[right_pointer] == BLANK:
        right_pointer -= 1
    elif disk[left_pointer] != BLANK: 
        left_pointer += 1
    elif disk[right_pointer] != BLANK and disk[left_pointer] == BLANK:
        disk[left_pointer] = disk[right_pointer]
        disk[right_pointer] = BLANK
        right_pointer -= 1
    else:
        raise Exception("That should cover all the cases")
    
# Part 1: And compute checksum!
checksum = 0
for disk_index, file_index in enumerate(disk):
    if file_index == BLANK: continue
    checksum += (disk_index * file_index)
print(checksum)

# Part 2: Do the smarter compaction. Now it's better to keep a non-flat representation :D
@dataclass
class Block:
    files: list[tuple[int, int]] # (index, size)
    free_space: int

blocks = []
for i, length in enumerate(lengths):
    if i % 2 == 0:
        blocks.append(Block(files=[(i//2, length)], free_space = 0))
    else:
        blocks.append(Block(files=[], free_space = length))

# Work backwards.
right_pointer = len(blocks) - 1
while right_pointer >= 0 and len(blocks[right_pointer].files) <= 1:
    if blocks[right_pointer].files:
        (file_index, file_size) = blocks[right_pointer].files[0]

        # See if we can move this file to the left. This is a linear scan, so the overall algorithm is
        # quadratic. There's definitely smarter things we can do here - for example, save the first
        # block which has at least N space for some values of N - but this works well enough for the
        # problem statement.
        for left_pointer in range(right_pointer):
            block = blocks[left_pointer]
            if block.free_space >= file_size:
                block.free_space -= file_size
                block.files.append((file_index, file_size))
                blocks[right_pointer].files = []
                blocks[right_pointer].free_space += file_size
                break

    right_pointer -= 1

# Reconstruct the disk
disk = []
for block in blocks:
    for (file_index, file_size) in block.files:
        disk.extend([file_index] * file_size)
    disk.extend([BLANK] * block.free_space)
assert len(disk) == sum(lengths)

# Urgh, fails for part 2. TODO: Some sanity checks on the blocks (no file appears twice?)

checksum = 0
for disk_index, file_index in enumerate(disk):
    if file_index == BLANK: continue
    checksum += (disk_index * file_index)
print(checksum)

for i in range(len(disk) // 100):
    print(disk[i*100:i*100+100])
print(blocks)
