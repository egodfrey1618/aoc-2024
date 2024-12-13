from pathlib import Path

TEST = False
if TEST:
    text = Path("12_test.txt").read_text().strip()
else:
    text = Path("12.txt").read_text().strip()

grid = [[x for x in line] for line in text.split("\n")]

def get_value(grid, position):
    (x, y) = position
    if y >= len(grid) or y < 0: return None
    if x >= len(grid[y]) or x < 0: return None
    return grid[y][x]

def get_neighbours(p):
    # goes in clockwise order, which is important for Part 2!
    yield (p[0] + 1, p[1])
    yield (p[0], p[1] + 1)
    yield (p[0] - 1, p[1])
    yield (p[0], p[1] - 1)

positions = [(x, y) for x in range(len(grid[0])) for y in range(len(grid))]

# First step: Flood fill to get the regions
region_id_to_region = {}
position_to_region_id = {}

for position in positions:
    if position not in position_to_region_id:
        new_region_id = len(region_id_to_region)
        new_region = set()
        character = get_value(grid, position)

        # Flood fill to find the region
        boundary = set([position])
        while boundary:
            x = boundary.pop()
            if x not in new_region:
                new_region.add(x)
                for n in get_neighbours(x):
                    if get_value(grid, n) == character and n not in new_region:
                        boundary.add(n)

        region_id_to_region[new_region_id] = new_region
        for p in new_region: 
            position_to_region_id[p] = new_region_id

# Part 1
def simple_perimeter(region):
    count = 4 * len(region)

    for p in region:
        for n in get_neighbours(p):
            if n in region:
                # Subtract off one for the fence between these that we've overcounted.
                # We'll do this twice (both ways around).
                count -= 1

    return count

print(sum(len(region) * simple_perimeter(region) for region in region_id_to_region.values()))

# Part 2. This is trickier - now we just want to count how many straight lines contain the region.
# Or equivalently, the number of "corners" that the fence has.
#
# I think this is equivalent to counting the number of times I either have:
# - a square which is IN, and two next-door neighbours which are OUT. (Because then the fence has to wrap around
# this square).
# - a square which is IN, with two next-door neighbours which are IN, and the other square diagonally opposite
# OUT. (Because then the fence has to go around them - it's the dual of case 1, i.e. the region next door has this
# shape.)

def complicated_perimeter(region):
    count = 0

    for p in region:
        neighbours = list(get_neighbours(p))

        for i in range(4):
            # These are "next-door" neighbours, not opposite, because [neighbours] returns the neighbours
            # in clockwise order
            neighbour1 = neighbours[i] 
            neighbour2 = neighbours[(i+1)%4]

            if neighbour1 not in region and neighbour2 not in region:
                # This is case 1
                count += 1

            if neighbour1 in region and neighbour2 in region:
                x = neighbour1[0] + neighbour2[0] - p[0]
                y = neighbour1[1] + neighbour2[1] - p[1]
                diagonally_across = (x, y)
                if diagonally_across not in region:
                    # This is case 2
                    count += 1
    return count

print(sum(len(region) * complicated_perimeter(region) for region in region_id_to_region.values()))

