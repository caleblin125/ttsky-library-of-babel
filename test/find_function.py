import random
import multiprocessing as mp
import argparse
import json
import os
import time

# -------------------------
# parameters
# -------------------------

charsize = 5
statelength = 16

STATE_MASK = (1 << statelength) - 1
CHAR_MASK = (1 << charsize) - 1

PROGRAM_LEN = 4

characters = "abcdefghijklmnopqrstuvwxyz .,!?;"

desiredText = (
"to be, or not to be, that is the question whether tis nobler in the mind "
"to suffer the slings and arrows"
)

RESULT_FILE = "best_results.jsonl"

OPS = ["xor_lshift","xor_rshift","add","mul","xor_const"]

# -------------------------
# program generation
# -------------------------

def random_instruction():

    op = random.choice(OPS)

    if op in ("xor_lshift","xor_rshift"):
        return (op, random.randint(1,7))

    if op == "add":
        return (op, random.randint(1,65535))

    if op == "mul":
        return (op, random.randint(3,65535) | 1)

    if op == "xor_const":
        return (op, random.randint(1,65535))


def random_program():
    return [random_instruction() for _ in range(PROGRAM_LEN)]


# -------------------------
# RNG execution
# -------------------------

def run_program(state, program):

    for op,val in program:

        if op == "xor_lshift":
            state ^= (state << val)

        elif op == "xor_rshift":
            state ^= (state >> val)

        elif op == "add":
            state += val

        elif op == "mul":
            state *= val

        elif op == "xor_const":
            state ^= val

        state &= STATE_MASK

    return state


def output_char(state):
    return (state >> (statelength - charsize)) & CHAR_MASK


# -------------------------
# prefix verification
# -------------------------

def verify_prefix(program, init):

    mapping = {}
    used = set()

    state = init
    count = 0

    for c in desiredText:

        state = run_program(state, program)
        out = output_char(state)

        if out in mapping:

            if mapping[out] != c:
                return count

        else:

            if c in used:
                return count

            mapping[out] = c
            used.add(c)

        count += 1

    return count


# -------------------------
# persistence
# -------------------------

def save_result(program, seed, prefix):

    data = {
        "program": program,
        "seed": seed,
        "prefix": prefix
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
# build encoding
# -------------------------

def build_encoding(program, seed):

    mapping = {}
    used = set()

    state = seed

    for c in desiredText:

        state = run_program(state, program)
        out = output_char(state)

        if (out not in mapping) and (c not in used):
            mapping[out] = c
            used.add(c)

    code = []

    remaining = [c for c in characters if c not in used]

    for i in range(1<<charsize):

        if i in mapping:
            code.append(mapping[i])

        elif remaining:
            code.append(remaining.pop())

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

        if op == "xor_lshift":
            lines.append(f"        s = s ^ (s << {val});")

        elif op == "xor_rshift":
            lines.append(f"        s = s ^ (s >> {val});")

        elif op == "add":
            lines.append(f"        s = s + 16'd{val};")

        elif op == "mul":
            lines.append(f"        s = s * 16'd{val};")

        elif op == "xor_const":
            lines.append(f"        s = s ^ 16'd{val};")

    lines.append("        rng_step = s;")
    lines.append("    end")
    lines.append("endfunction")

    return "\n".join(lines)


# -------------------------
# worker search
# -------------------------

def worker(proc_id):

    random.seed(proc_id + int(time.time()))

    best_data = load_best()
    best_prefix = best_data["prefix"] if best_data else 0

    print(f"[proc {proc_id}] starting best =", best_prefix)

    while True:

        program = random_program()

        for seed in range(65536):

            prefix = verify_prefix(program, seed)

            if prefix > best_prefix:

                best_prefix = prefix

                print(
                    f"[proc {proc_id}] new best:",
                    prefix,
                    program,
                    seed
                )

                save_result(program, seed, prefix)


# -------------------------
# search mode
# -------------------------

def search():

    cpu = mp.cpu_count()

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
    seed = best["seed"]
    prefix = best["prefix"]

    print("Best prefix:",prefix)
    print("Seed:",seed)
    print("Program:",program)

    print("\nEncoding table:\n")

    encoding = build_encoding(program, seed)
    print(encoding)

    print("\nVerilog RNG:\n")

    print(program_to_verilog(program))


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