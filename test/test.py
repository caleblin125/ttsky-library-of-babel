# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge

characters=";t?!,le.zyxbwoavusrq pnmkjcihgfd"
testStrings = ["", "a", "cat", "dog", "caleb lin", "page one", "page two"]
loopLimit = 1000

async def reset(dut):
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 10)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 0

async def inputKey(dut, key:str):
    for c in key:
        if c not in characters:
            raise ValueError(f"{c} not a valid character in {key}")
        index = characters.index(c)
        dut.ui_in.value = index | (1 << 5) # Set 5th bit to 1 to enable inputs
        await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0

async def readKey(dut):
    s = ""
    for i in range(loopLimit):
        await ClockCycles(dut.clk, 1)
        outChar = dut.uo_out.value.to_unsigned()
        if outChar & (1 << 5): # 5th bit confirms writing
            s += characters[outChar & 0b11111]
        else:
            break
    return s

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    res = {}
    for s in testStrings:
        await reset(dut) # Reset

        dut._log.info(f"Testing input: [{s}]")
        await inputKey(dut,s)
        page = await readKey(dut) # get page of text
        dut._log.info(f"Output: {page}")
        res[s] = page

        assert len(page) == 255 #check size of page is correct

    for s in testStrings:
        await reset(dut) # Reset

        dut._log.info(f"Retesting input: [{s}]")
        await inputKey(dut,s)
        page = await readKey(dut) # get page of text
        assert res[s] == page
    
    counts = [0]*32  #Check randomness
    for s in testStrings:
        for i in range(32):
            counts[i] += res[s].count(characters[i])
    dut._log.info(f"Character counts: {counts}")
    avg = sum(counts)/32
    dut._log.info(f"Character count mean: {avg}")
    dut._log.info(f"Character count variance: {(sum([(c-avg)**2 for c in counts])/32)**0.5}")