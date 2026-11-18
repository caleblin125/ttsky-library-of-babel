![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# Library of Babel — a Tiny Tapeout chip

A tiny ASIC that "writes" pages of the
[Library of Babel](https://en.wikipedia.org/wiki/The_Library_of_Babel): every
possible page of text, generated on demand from a seed instead of stored.
Designed in SystemVerilog for [Tiny Tapeout](https://tinytapeout.com) on the
SkyWater 130 nm process (one 167 × 108 µm tile).

It is also an infinite-monkey experiment: the pseudorandom generator was
**searched** so that one particular seed makes the chip type out the opening of
Hamlet's soliloquy.

## How it works

* The chip holds a **16-bit state** and steps it every clock with a small
  hash-like function (multiply, add, xor-shift). The top 5 bits of the state
  select one of 32 characters: `a`–`z` plus ` .,!?;`.
* **Seeding:** while `ui[5]` (enable input) is high, the 5-bit character on
  `ui[4:0]` is mixed into the state each cycle, so any short string acts as a
  "book address".
* **Writing:** after seeding, the chip emits one character per clock on
  `uo[4:0]` with `uo[5]` (output valid) high, for a fixed-length page of 255
  characters, then stops.

### Searching for Shakespeare

[`test/find_function.py`](test/find_function.py) searches the space of
four-instruction RNG programs (xor-left-shift, xor-right-shift, add, multiply,
xor-constant). For each candidate program it checks **all 65,536 seeds** in
parallel with Numba (`@njit(parallel=True)`) and scores how many leading
characters match the target text. It ran as a 64-core batch job on the PSC
Bridges-2 supercomputer ([`test/slurm_find.bat`](test/slurm_find.bat)).

The best program found so far reproduces the first **15 characters**
(`to be, or not t`) from a single seed. Results are logged to
[`test/best_results.jsonl`](test/best_results.jsonl), and
`python find_function.py print` emits the winning function as Verilog.

```bash
cd test
pip install numba numpy
python find_function.py search     # run the search (uses all cores)
python find_function.py print      # print the best RNG as Verilog
```

## Pinout

| Pin | Direction | Function |
|---|---|---|
| `ui[4:0]` | in | seed character index |
| `ui[5]` | in | enable seed input |
| `uo[4:0]` | out | output character index |
| `uo[5]` | out | output valid (page still being written) |

## Testing

The cocotb testbench in [`test/`](test/) seeds the design with several strings
and reads back the generated pages:

```bash
cd test
pip install -r requirements.txt
make        # runs the RTL simulation with Icarus Verilog
```

GitHub Actions also run the test suite, build the GDS layout with LibreLane,
and generate the datasheet ([`docs/info.md`](docs/info.md)).

## About Tiny Tapeout

Tiny Tapeout is an educational project that makes it cheap and easy to get
digital designs manufactured on a real chip. Learn more at
https://tinytapeout.com.
