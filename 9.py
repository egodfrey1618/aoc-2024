from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
# Store the file structure as a doubly linked list of blocks, where a block is some list of
# files, and (possibly) some free space.
@dataclass
class Block:
    files: list[int, int] # (file_index, file_size)
    free_space: int
    prev_block: Optional["Block"]
    next_block: Optional["Block"]

first_block = None
this_block = None

for i in range(0, len(lengths), 2):
    file_length = lengths[i]
    free_space = lengths[i+1] if i != len(lengths) - 1 else 0
    file_index = i//2

    block = Block(files=[(file_index, file_length)], free_space=free_space, prev_block=this_block, next_block=None)

    if this_block is not None:
        this_block.next_block = block
    this_block = block

    if first_block is None: 
        first_block = block

last_block = this_block

# Work backwards.
right_pointer = last_block
next_file_to_move = len(file_lengths) - 1

while right_pointer is not None and next_file_to_move >= 0:
    files_dict = dict(right_pointer.files)

    if next_file_to_move not in files_dict:
        right_pointer = right_pointer.prev_block
        continue

    file_size = files_dict[next_file_to_move]

    # Loop through every block, seeing if we can find an empty space for the file.  
    # This might scan every block, so the overall algorithm is quadratic - there's probably something
    # smarter to do here.
    block = first_block
    moved = False

    while block is not right_pointer and not moved:
        if block.free_space >= file_size:
            # We've found where we want to move it to! There are two possibilities:
            # (1, easier) The file we're moving is at the end of [right_pointer]. If so,
            # we can just pop it off the end.
            # (2, harder) The file is in the middle of the list of files in [right_pointer].
            # If so, we'll need to split it up, to get the free space in the right place.

            if right_pointer.files[-1][0] != next_file_to_move:
                # Case 2. Split [right_pointer] up into two chunks.
                i = [i for (i, f) in enumerate(right_pointer.files) if f[0] == next_file_to_move][0]

                files1 = right_pointer.files[:i+1]
                files2 = right_pointer.files[i+1:]

                new_block = Block(files=files2, free_space=right_pointer.free_space, prev_block=right_pointer, next_block=right_pointer.next_block)
                right_pointer.files = files1
                right_pointer.free_space = 0
                right_pointer.next_block.prev_block = new_block
                right_pointer.next_block = new_block

            # Now either way, we have the file we want to move on the right-hand-side of this block
            assert right_pointer.files[-1][0] == next_file_to_move

            # Move the file.
            right_pointer.files.pop()
            block.files.append((next_file_to_move, file_size))
            right_pointer.free_space += file_size
            block.free_space -= file_size

            moved = True

            # An optimisation: If this made [block] full, merge it with the next one. This avoids us walking over multiple
            # full blocks.
            if block.free_space == 0:
                if block.next_block is not None:
                    old_next_block = block.next_block

                    block.files.extend(old_next_block.files)
                    block.free_space = old_next_block.free_space
                    block.next_block = old_next_block.next_block
                    if block.next_block is not None:
                        block.next_block.prev_block = block

                    if old_next_block is right_pointer:
                        right_pointer = block
        else:
            block = block.next_block

    next_file_to_move -= 1

assert next_file_to_move < 0

# Reconstruct the disk
disk = []
block = first_block
while block is not None:
    for (file_index, file_length) in block.files:
        disk.extend([file_index] * file_length)
    disk.extend([BLANK] * block.free_space)
    block = block.next_block
assert len(disk) == sum(lengths)

checksum = 0
for disk_index, file_index in enumerate(disk):
    if file_index == BLANK: continue
    checksum += (disk_index * file_index)
print(checksum)
