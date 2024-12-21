import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from z3 import *

# Needs to run in a venv with z3-solver installed.

TEST = False
if TEST:
    text = Path("17_test.txt").read_text().strip()
else:
    text = Path("17.txt").read_text().strip()

register_a = int(re.findall("Register A: (.*)$", text, flags=re.MULTILINE)[0])
register_b = int(re.findall("Register B: (.*)$", text, flags=re.MULTILINE)[0])
register_c = int(re.findall("Register C: (.*)$", text, flags=re.MULTILINE)[0])
program = re.findall("Program: (.*)$", text, flags=re.MULTILINE)[0]
program = [int(x) for x in program.split(",")]

ADV = 0
BXL = 1
BST = 2
JNZ = 3
BXC = 4
OUT = 5
BDV = 6
CDV = 7

class Computer:
    def combo_operand(self, x: int) -> int:
        if x >= 0 and x <= 3:
            return x

        if x == 4:
            return self.register_a

        if x == 5:
            return self.register_b

        if x == 6:
            return self.register_c
        
        raise Exception(f"Invalid combo operand: {x}")

    def __init__(self, register_a, register_b, register_c, program):
        self.pc = 0
        self.register_a = register_a
        self.register_b = register_b
        self.register_c = register_c
        self.program = program

    def step(self) -> tuple[bool, Optional[int]]:
        if self.pc + 1 >= len(self.program) or self.pc < 0:
            return (False, None)

        instruction = self.program[self.pc]
        operand = self.program[self.pc + 1]
        output_value = None

        if instruction in (ADV, BDV, CDV):
            value = self.register_a // (2 ** self.combo_operand(operand))

            if instruction == ADV:
                self.register_a = value
            elif instruction == BDV:
                self.register_b = value
            elif instruction == CDV:
                self.register_c = value
            else:
                assert False
        elif instruction == BXL:
            value = self.register_b ^ operand
            self.register_b = value
        elif instruction == BST:
            value = self.combo_operand(operand) & 0b111
            self.register_b = value
        elif instruction == JNZ:
            if self.register_a != 0:
                self.pc = operand
        elif instruction == BXC:
            self.register_b ^= self.register_c
        elif instruction == OUT:
            output_value = self.combo_operand(operand) & 0b111
        else: 
            raise Exception("Invalid instruction")

        if instruction != JNZ or self.register_a == 0:
            self.pc += 2
        return (True, output_value)

    def print_state(self):
        print(f"{self.pc=}")
        print(f"A:{self.register_a}, B:{self.register_b}, C:{self.register_c}")
        print(f"Current instruction: {self.program[self.pc] if self.pc < len(self.program) else 'OOB'}")
        print(f"Current operand: {self.program[self.pc + 1] if self.pc + 1 < len(self.program) else 'OOB'}")

    def run(self) -> list[int]:
        result = []
        self.print_state()
        while True:
            (still_running, value) = self.step()
            self.print_state()

            if value is not None: 
                result.append(value)

            if not still_running:
                break
        return result

c = Computer(register_a, register_b, register_c, program)
results = c.run()
print(",".join(str(x) for x in results))

# Part 2 is completely different. Inspecting my program, here's roughly what it corresponds to:
# Program: 2,4,1,7,7,5,0,3,1,7,4,1,5,5,3,0
# (2, 4) B = A mod 8
# (1, 7) B = B XOR 7
# (7, 5) C = A / (2**B) (and we may as well MOD by 8 here, makes no difference to below)
# (0, 3) A = A / 8
# (1, 7) B = B XOR 7
# (4, 1) B = B XOR C
# (5, 5) OUTPUT (B & 8)
# (3, 0) JUMP IF NOT 0
# 
# So each pass gives us a relationship between:
# - The bottom 3 bits of A
# - Some other 3 bits further up

s = Solver()

target = program

length = 3 * len(target)

a = BitVec("a", length)
chunks = []
for i in range(len(program)):
    chunks.append(BitVec(f"a-{i}", length))

# Add basic constraints: Each of the a-{i} is supposed to be a chunk of 3 bits of a.
for i, a_chunk in enumerate(chunks):
    s.add((a >> (3*i)) & 0b111 == a_chunk)
    s.add(a_chunk <= 8)

# Add the constraints that the program gives us.
for i, a_chunk in enumerate(chunks):
    b = BitVec(f"b-{i}", length)
    s.add(b == a_chunk ^ 7)

    c = BitVec(f"c-{i}", length)
    s.add(c == ((a >> (3*i)) >> b) & 0b111)

    b2 = BitVec(f"b2-{i}", length)
    # b2 is (b ^ 7) ^ c = a_chunk ^ c
    s.add(b2 == a_chunk ^ c)

    s.add(b2 == target[i])

print(s.check())
print(s.model())

register_a = s.model()[a].as_long()
print(register_a)
while True:
    s.add(a < register_a)
    try:
        s.check()
        register_a = s.model()[a].as_long()
        print(register_a)
    except Z3Exception:
        break

c = Computer(register_a, register_b, register_c, program)
results = c.run()
print(results)
print(target)
print(register_a)
