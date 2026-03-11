

import random

charsize = 6
statelength = 16

characters="abcdefghijklmnopqrstuvwxyz .,!?;"
operators = [("~", 1), ("+", 2), ("-", 2), ("|", 2), ("&", 2), ("^", 2), (">>", 3), ("<<", 3)]

desiredText = "welcome to the library of babel!"
findText = "to be, or not to be, that is the question whether tis nobler in the mind to suffer. the slings and arrows of outrageous fortune, or to take arms against a sea of troubles and by opposing end them. to die to sleep, no more and by a sleep to say we end the heart ache and the thousand natural shocks that flesh is heir to tis a consummation devoutly to be wishd."

def verify(text:str, generation:list[int], mapping = None):
    generation = generation[:len(text)]
    if mapping is None:
        mapping = {}
    count = 0
    mapped = len(set(mapping.values())) 
    for c, i in zip(text, generation):
        if i in mapping:
            if mapping[i] != c:
                return (False, mapping, count)
        # elif c in mapping.values():
        #     return (False, mapping, count)
        elif (len(characters) - mapped) <= ((1 << charsize) - len(mapping)):
            mapping[i] = c
            if c not in mapping.values():
                mapped += 1
        else:
            return (False, mapping, count)
        count += 1
    
    return (True, mapping, count)

def compute(initState:int, function):
    initState = initState & ((1<<statelength) - 1)
    state = initState
    output = []
    for i in range(256):
        state = function(state) & ((1<<statelength) - 1)
        output.append((state >> (statelength - charsize)) & ((1 << charsize) - 1))
    return output

def find_sequence(function, text, mapping, tests = 1000):
    for i in range(tests):
        init = random.randint(0, 2**statelength - 1)
        gen = compute(init, function)
        ok, new_mapping, count = verify(text, gen, mapping)
        if ok:
            return (True, init, new_mapping)
    return (False, None, mapping)

def randomness(function, iterations):
    counts = [0]*(1<<charsize)
    correlation = [[0]*(1<<charsize) for i in range((1<<charsize))]
    for i in range(iterations):
        init = random.randint(0, 2**statelength - 1)
        seq = compute(init, function)
        for s in seq:
            counts[s] += 1
        prev = seq[0]
        for s in seq[1:]:
            correlation[prev][s] += 1
            prev = s

    total = sum(counts)
    mean = total / len(counts)
    var_counts = sum((c - mean)**2 for c in counts) / len(counts)

    flat_corr = [v for row in correlation for v in row]
    total_corr = sum(flat_corr)
    mean_corr = total_corr / len(flat_corr)
    var_corr = sum((v - mean_corr)**2 for v in flat_corr) / len(flat_corr)
    return (var_counts, var_corr)
        


# ---------- expression generator ----------

def random_leaf():
    if random.random() < 0.5:
        return "state"
    else:
        return str(random.randint(0, 2**statelength - 1))

def random_expr(depth=3):
    if depth == 0:
        return random_leaf()

    op, arity = random.choice(operators)

    if arity == 1:
        return f"({op}{random_expr(depth-1)})"
    elif arity == 2:
        left = random_expr(depth-1)
        right = random_expr(depth-1)
        return f"({left} {op} {right})"
    else:
        left = random_expr(depth-1)
        right = random.randint(1, 15)
        return f"({left} {op} {right})"

# ---------- compile expression ----------

def make_function(expr):
    code = f"lambda state: {expr}"
    try:
        return eval(code), expr
    except:
        return None, expr

# ---------- search ----------

def search(iterations=100000):
    bad = []
    possibilities = []
    solutions = []
    for i in range(iterations):

        expr = random_expr(depth=4)
        func, expr = make_function(expr)

        if func is None:
            continue

        try:
            variance = randomness(func, 5)
            if variance[0] > 1000:
                continue
            
            bestCount = 0
            mapping = {}
            init = 0
            for j in range(10):
                test_init = random.randint(0, 2**statelength - 1)
                gen = compute(test_init, func)
                ok, test_mapping, count = verify(desiredText, gen)
                if ok:
                    init = test_init
                    mapping = test_mapping
                    break
                if count > bestCount:
                    init = test_init
                    mapping = test_mapping
            
            variance = randomness(func, 100)

            # print(init, expr, mapping)
            if ok:
                print("Tested", i)
                print("FOUND INIT MATCH")
                print("expr:", expr)
                print("init:", init)
                print("mapping:", mapping)
                print("randomness:", variance)
                possibilities.append((expr, init, mapping, variance , func, count))
                # return expr, init
            
            bad.append((expr, init, mapping, variance, func, count))
            bad.sort(key = lambda x:x[5], reverse = True)
            bad = bad[:10]

        except Exception as e:
            print(e)
            pass

        if i % 1000 == 0:
            print("tested", i, "max", bad[0][5])

    possibilities.sort(key=lambda x:x[3][1]+x[3][0])

    for p in possibilities:
        ok, key, newMapping = find_sequence(p[4], findText, p[2], 1000)
        if ok:
            print("FOUND SOLUTION")
            print("eq:", p[0])
            print("init:", p[1])
            print("randomness:", p[3])
            print("key:", key)

            code = []
            missingKeys = [c for c in characters if (c not in newMapping.values())]
            # print(missingKeys)
            for i in range(1<<charsize):
                if i in newMapping:
                    code.append(newMapping[i])
                elif len(missingKeys) > 0:
                    code.append(missingKeys.pop())
                else:
                    code.append(random.choice(characters))
            print(code)
            print("code:", "".join(code))
            return (p, code, key)

    # if len(possibilities) == 0:
    #     print(bad)
    # else:
    #     print(possibilities)

    return None


search(iterations=10000)

