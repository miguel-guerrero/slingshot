#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
# -------------------------------------------------------------------------------
import sys
sys.path.append("..")  # add path to chipo and related

from chipo import *
from hlc import Fsm, Wait

# Example of algorithmically defined state machine through Fsm construct

MEM_AW = Param(16)
MEM_DW = Param(32)
DIM_BITS = Param(16)
PREC = Param(16)

clk = Clock()
rst_n = Reset()
ret = Out()
go = In()

# memory interface
mem_write, mem_req = Out() ** 2
mem_addr = Out(MEM_AW)
mem_wdata = Out(MEM_DW)
mem_rdata_vld = In()
mem_rdata = In(MEM_DW)

# mattrix parameters
aBASE, bBASE, cBASE = In(MEM_AW) ** 3
aSTRIDE, bSTRIDE, cSTRIDE = In(DIM_BITS) ** 3
aROWS, aCOLS, bCOLS = In(DIM_BITS) ** 3


def MEM_write(addr, wdata):
    return Block(
        mem_wdata <= wdata,
        mem_addr  <= addr,
        mem_write <= 1,
        mem_req   <= 1)


def MEM_read(addr):
    return Block(
        mem_addr  <= addr,
        mem_write <= 0,
        mem_req   <= 1)


def MEM_done():
    return mem_req <= 0


def incr(x, inc=1):
    return x <= x + inc


i, j, k = Signal(DIM_BITS) ** 3
a_i0, a_ik, b_0j, b_kj, c_i0, c_ij = Signal(MEM_AW) ** 6
acc = Signal(MEM_DW)
a = Signal(PREC)


matmul = Module() [
    Fsm(clk, rst_n, name='matmul_fsm') [
        ret <= 0,
        ...,
        Wait(go),
        a_i0 <= aBASE,
        c_i0 <= cBASE,
        i <= 0,
        ...,
        While (i != aROWS) [
            b_0j <= bBASE,
            c_ij <= c_i0,
            j <= 0,
            ...,
            While (j != bCOLS) [
                a_ik <= a_i0,
                b_kj <= b_0j,
                acc <= 0,
                k <= 0,
                ..., MEM_read(a_ik), incr(a_ik),
                ..., MEM_read(b_kj), incr(b_kj, bSTRIDE),
                While (k != aCOLS) [
                    ..., incr(k),
                    ..., MEM_read(a_ik), incr(a_ik),           a <= mem_rdata[PREC-1:0],
                    ..., MEM_read(b_kj), incr(b_kj, bSTRIDE),  incr(acc, a[PREC-1:0]*mem_rdata[PREC-1:0]),
                ],
                MEM_done(),
                ..., MEM_write(c_ij, acc), incr(b_0j), incr(c_ij), incr(j),
                ..., MEM_done(),
            ],
            incr(a_i0, aSTRIDE),
            incr(c_i0, cSTRIDE),
            incr(i),
            ...,
        ],
        ret <= 1,
        ...,
    ]
].autoGen()

print(matmul.vlog())
