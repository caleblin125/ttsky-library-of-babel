import random
import multiprocessing as mp
import argparse
import json
import os
import time
import numpy as np
from numba import njit, prange, int64

# -------------------------
# parameters
# -------------------------

charsize = 5
statelength = 16

STATE_MASK = (1 << statelength) - 1
CHAR_MASK = (1 << charsize) - 1

PROGRAM_LEN = 4

characters = "abcdefghijklmnopqrstuvwxyz .,!?;"

# desiredText = (
# "to be, or not to be, that is the question whether tis nobler in the mind "
# "to suffer the slings and arrows"
# )

desiredText = "welcome to babel"

desiredIdx = np.array([characters.index(c) for c in desiredText], dtype=np.int32)
# print(desiredIdx)

RESULT_FILE = "best_results.jsonl"

OPS = ["xor_lshift","xor_rshift","add","mul","xor_const"]

# opcode encoding
OP_XOR_LSHIFT = 0
OP_XOR_RSHIFT = 1
OP_ADD = 2
OP_MUL = 3
OP_XOR_CONST = 4


# -------------------------
# program generation
# -------------------------

def random_instruction():

    op = random.choice(OPS)

    if op == "xor_lshift":
        return (OP_XOR_LSHIFT, random.randint(1,7))

    if op == "xor_rshift":
        return (OP_XOR_RSHIFT, random.randint(1,7))

    if op == "add":
        return (OP_ADD, random.randint(1,65535))

    if op == "mul":
        return (OP_MUL, random.randint(3,65535) | 1)

    if op == "xor_const":
        return (OP_XOR_CONST, random.randint(1,65535))


def random_program():
    return [random_instruction() for _ in range(PROGRAM_LEN)]


def program_to_arrays(program):

    ops = np.zeros(PROGRAM_LEN, dtype=np.int32)
    vals = np.zeros(PROGRAM_LEN, dtype=np.int32)
    
    for i,(op,val) in enumerate(program):
        ops[i] = op
        vals[i] = val

    return ops, vals


# -------------------------
# numba RNG step
# -------------------------

@njit
def step(state, ops, vals):

    for i in range(len(ops)):

        op = ops[i]
        v = vals[i]

        if op == OP_XOR_LSHIFT:
            state ^= (state << v)

        elif op == OP_XOR_RSHIFT:
            state ^= (state >> v)

        elif op == OP_ADD:
            state += v

        elif op == OP_MUL:
            state *= v

        elif op == OP_XOR_CONST:
            state ^= v

        state &= STATE_MASK

    return state


# -------------------------
# prefix verification
# -------------------------

@njit
def verify_prefix_seed(seed:int, ops, vals, desired:np.ndarray[int]) -> int:

    mapping = np.full(32, -1, np.int32)
    used = np.zeros(32, np.uint8)

    state = int64(seed)

    for i in range(len(desired)):

        state = step(state, ops, vals)

        out = state >> (statelength - charsize)
        c = desired[i]

        m = mapping[out]

        if m != -1:
            if m != c:
                return i
        else:
            if used[c] == 1:
                return i
            mapping[out] = c
            used[c] = 1

    return len(desired)


# -------------------------
# scan all seeds (parallel)
# -------------------------

@njit(parallel=True)
def scan_seeds(ops, vals, desired):
    prefixes = np.zeros(65536, dtype=np.int32)
    
    for seed in prange(65536):
        prefixes[seed] = verify_prefix_seed(seed, ops, vals, desired)
    
    best_idx = np.argmax(prefixes)
    return prefixes[best_idx], best_idx


# -------------------------
# persistence
# -------------------------

def save_result(program, seed, prefix):

    data = {
        "program": [[OPS[p[0]], p[1]] for p in program],
        "seed": int(seed),
        "prefix": int(prefix)
    }

    with open(RESULT_FILE,"a") as f:
        f.write(json.dumps(data) + "\n")


def load_best():

    if not os.path.exists(RESULT_FILE):
        return None

    best = None

    with open(RESULT_FILE) as f:

        for line in f:
            data = json.loads(line)

            if best is None or data["prefix"] > best["prefix"]:
                best = data

    return best


# -------------------------
# encoding generation
# -------------------------

def build_encoding(program:list[(str,int)], seed):
    ops,vals = program_to_arrays(program)

    mapping = [-1]*32
    used = [False]*32

    state = seed

    for c in desiredIdx:

        state = step(state, ops, vals)
        out = state >> (statelength - charsize)

        if mapping[out] == -1 and not used[c]:

            mapping[out] = c
            used[c] = True

    remaining = [i for i in range(len(characters)) if not used[i]]

    code = []

    for i in range(32):

        if mapping[i] != -1:
            code.append(characters[mapping[i]])

        elif remaining:
            code.append(characters[remaining.pop()])

        else:
            code.append("?")

    return "".join(code)


# -------------------------
# Verilog generation
# -------------------------

def program_to_verilog(program):

    lines = []

    lines.append("function [15:0] rng_step;")
    lines.append("    input [15:0] state;")
    lines.append("    reg [15:0] s;")
    lines.append("    begin")
    lines.append("        s = state;")

    for op,val in program:
        if op == OP_XOR_LSHIFT:
            lines.append(f"        s = s ^ (s << {val});")

        elif op == OP_XOR_RSHIFT:
            lines.append(f"        s = s ^ (s >> {val});")

        elif op == OP_ADD:
            lines.append(f"        s = s + 16'd{val};")

        elif op == OP_MUL:
            lines.append(f"        s = s * 16'd{val};")

        elif op == OP_XOR_CONST:
            lines.append(f"        s = s ^ 16'd{val};")

    lines.append("        rng_step = s;")
    lines.append("    end")
    lines.append("endfunction")

    return "\n".join(lines)


# -------------------------
# worker
# -------------------------

def worker(proc_id):

    random.seed(proc_id + int(time.time()))

    best_data = load_best()
    best_prefix = best_data["prefix"] if best_data else 0

    print(f"[proc {proc_id}] starting best =", best_prefix)
    
    count = 0
    startTime = time.time()
    while True:

        program = random_program()
        ops,vals = program_to_arrays(program)

        prefix,seed = scan_seeds(ops, vals, desiredIdx)

        if prefix > best_prefix:

            best_prefix = prefix

            print(
                f"[proc {proc_id}] new best:",
                prefix,
                program,
                seed
            )

            save_result(program, seed, prefix)
        
        count += 1
        # if count % 10 == 0:
        #     print(f"{count / (time.time() - startTime)} functions per second")
        #     print(f"{count * (1<<16) / (time.time() - startTime)} searches per second")


# -------------------------
# search
# -------------------------

def search():

    cpu = int(os.environ.get("SLURM_CPUS_PER_TASK", mp.cpu_count()))

    print("Starting search on", cpu, "cores")

    procs = []

    for i in range(cpu):

        p = mp.Process(target=worker,args=(i,))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()


# -------------------------
# print mode
# -------------------------

def print_best():

    best = load_best()

    if best is None:
        print("No results yet.")
        return

    program = best["program"]
    pEncoded = [(OPS.index(p[0]), p[1]) for p in program]
    seed = best["seed"]
    prefix = best["prefix"]

    print("Best prefix:",prefix)
    print("Seed:",seed)
    print("Program:",program)

    print("\nEncoding table:\n")

    encoding = build_encoding(pEncoded, seed)
    print(encoding)

    print("\nVerilog RNG:\n")

    print(program_to_verilog(pEncoded))


# -------------------------
# main
# -------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "mode",
        choices=["search","print"],
        help="search for RNG or print best Verilog"
    )

    args = parser.parse_args()

    if args.mode == "search":
        search()

    if args.mode == "print":
        print_best()


if __name__ == "__main__":
    main()