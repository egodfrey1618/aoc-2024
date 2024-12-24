from pathlib import Path
from z3 import *

# Needs to run in a venv with z3-solver installed.

TEST = False
if TEST:
    text = Path("24_test.txt").read_text().strip()
else:
    text = Path("24.txt").read_text().strip()

fixed_values = {}
combinations = {}

for line in text.split("\n"):
    if line == "":
        continue
    elif " -> " in line:
        tokens = line.split()
        assert tokens[3] == "->"
        assert tokens[1] in ("AND", "OR", "XOR")
        (input1, op, input2, _, result) = tokens
        combinations[result] = (result, op, input1, input2)
    else:
        tokens = line.split()
        (variable, number) = tokens
        number = int(number)
        assert variable.endswith(":")
        variable = variable[:-1]
        fixed_values[variable] = number


# Add fixed value constraints
# Part 1: Lazy, just Z3 this.
def solve1(fixed_values, combinations):
    all_vars = {k: Bool(k) for k in list(fixed_values.keys()) + list(combinations.keys())}
    
    s = Solver()
    for k, v in fixed_values.items():
        s.add(all_vars[k] == bool(v))
    for k, v in combinations.items():
        (result, op, input1, input2) = v
        
        if op == "AND":
            s.add(all_vars[result] == all_vars[input1] & all_vars[input2])
        elif op == "OR":
            s.add(all_vars[result] == all_vars[input1] | all_vars[input2])
        elif op == "XOR":
            s.add(all_vars[result] == all_vars[input1] ^ all_vars[input2])
        else: 
            assert False
    
    z_keys = [s for s in all_vars.keys() if s.startswith("z")]
    z_keys.sort(key=lambda s: int(s[1:]))
    
    s.check()
    model = s.model()
    
    n = 0
    for key in reversed(z_keys):
        n *= 2
        v = bool(model[all_vars[key]])
        n += v
    
    print(n)
solve1(fixed_values, combinations)

# Part 2: The input has a pretty predictable structure (I just determined this by inspection),
# and my solution very heavily relies on this. Most of this is me manually inspecting it - I
# didn't come up with a smart algorithm.
# 
# Reverse engineering how the adder works: We have two types of gate:
# X AND Y. This is used to determine whether there's a carry bit that should be applied.
# X XOR Y. This is used to determine what the LSB should be.
#
# For example z00 = x00 XOR y00 is what's used to determine the LSB of the output.
#
# In pseudocode, the adder then looks like this:
# carry_bit := 0
# for x_bit, y_bit in input:
#   output = carry_bit ^ x_bit ^ y_bit
#   temp = carry_bit & (x_bit ^ y_bit)
#   carry_bit = temp | (x_bit & y_bit)
#
# For an example of above:
# ('z02', 'XOR', 'pgc', 'xor02')
# ('qrm', 'AND', 'pgc', 'xor02')
# ('wdm', 'OR', 'qrm', 'and02')
#
# Those last two lines, in English, say that the carry bit should be passed through if either:
# - both inputs bits at this position are 1.
# - exactly one input bit at this position is 1, and the carry bit was set.
# which makes sense.

def solve2(combinations):
    all_vars = list(fixed_values.keys()) + list(combinations.keys())
    
    def letter_keys(char):
        keys = [s for s in all_vars if s.startswith(char)]
        keys.sort(key=lambda s: int(s[1:]))
        return keys
    
    x_keys = letter_keys("x")
    y_keys = letter_keys("y")
    z_keys = letter_keys("z")
    assert len(x_keys) == len(y_keys) == len(z_keys) - 1
    
    x_keys_set = set(x_keys)
    y_keys_set = set(y_keys)
    
    # Let's relabel the gates matching that structure above, and see from visual inspection
    # what looks off. This is just relabelling the names - we're not doing any swapping yet.
    relabelling = {}
    reverse_relabelling = {}

    def add_label(x, y):
        if x in relabelling:
            print(f"Warning, {x} already labelled - skipping")
            return

        if y in reverse_relabelling:
            print(f"Warning, {y} already labelled - skipping")
            return
        relabelling[x] = y
        reverse_relabelling[y] = x

    def remove_label(y):
        assert y in reverse_relabelling
        x = reverse_relabelling[y]
        relabelling.pop(x)
        reverse_relabelling.pop(y)

    def swap_label(y1, y2):
        assert y1 in reverse_relabelling
        assert y2 in reverse_relabelling
        x1 = reverse_relabelling[y1]
        x2 = reverse_relabelling[y2]
        remove_label(y1)
        remove_label(y2)
        add_label(x1, y2)
        add_label(x2, y1)
    
    # Relabelling step 1: Relabel things that look like (x_i | y_i) or (x_i & y_i)
    for v in combinations.values():
        (result, op, input1, input2) = v
        if result.startswith("z"): continue

        if input1.startswith("y"):
            input1, input2 = input2, input1
    
        if input1 in x_keys_set and input2 in y_keys_set:
            number = input1[1:]
            assert number == input2[1:]
    
            if op == "AND":
                add_label(result, f"and-{number}")
            elif op == "XOR":
                add_label(result, f"xor-{number}")
            else:
                assert False
    
    combinations_after_relabel1 = {}
    for k, v in combinations.items():
        k = relabelling.get(k, k)
        v = tuple(relabelling.get(i, i) for i in v)
        combinations_after_relabel1[k] = v

    # Relabelling step2: Relabel the carry bit stages. Hacky-ish heuristic
    # for relabelling, and it doesn't always work.
    for v in combinations_after_relabel1.values():
        (result, op, input1, input2) = v
        if result.startswith("z"): continue

        if op == "AND" and "xor" in input1 or "xor" in input2:
            # Looks like the intermediate carry bit stage.
            if "xor" in input1:
                number = input1[4:]
            else:
                number = input2[4:]

            add_label(result, f"intermediate-carry-{number}")

        elif op == "OR" and "and" in input1 or "and" in input2:
            # Looks like the carry bit stage.
            if "and" in input1:
                number = input1[4:]
            else:
                number = input2[4:]

            add_label(result, f"carry-{number}")

    # Relabelling step3: Manual relabelling. I did this by looking at which
    # z labels didn't look like they were correct (an XOR with a carry and
    # an xor-), and looking at the variables with matching numbers.
    #
    # This is still only relabelling, not fixing up the gates.
    add_label("mfm", "and-31") # I think this has been swapped with z31.
    remove_label("intermediate-carry-06") # This got incorrectly labelled above
    add_label("ghf", "intermediate-carry-06") 
    add_label("fkp", "carry-06") # I think this has been swapped with z06
    add_label("brs", "carry-31") # Not sure why this didn't get picked up?

    # I think the intermediate-carry-38 and carry-38 labels are the wrong way aroudn.
    # Relabel them.
    swap_label("carry-38", "intermediate-carry-38")
    # At this point, it looks like the definitions of and-38 and xor-38 are wrong to
    # make those carry labels work.
    # If I swap those, the definitions of z38 and carry-38 and so on line up.

    add_label("ngr", "intermediate-carry-11") # I think this has been swapped with z11

    combinations_after_relabel2 = {}
    for k, v in combinations.items():
        k = relabelling.get(k, k)
        v = tuple(relabelling.get(i, i) for i in v)
        combinations_after_relabel2[k] = v

    for v in combinations_after_relabel2.values():
        print(v)

    # OK, so I think now my claim is that post-relabelling, these things got swapped:
    # (z31, and-31)
    # (carry-06, z06)
    # (and-38, xor-38)
    # (z11, intermediate-carry-11)

    l = ["z31", "and-31", "carry-06", "z06", "and-38", "xor-38", "z11", "intermediate-carry-11"]
    m = [reverse_relabelling.get(x, x) for x in l]
    m.sort()
    print(",".join(m))

solve2(combinations)
