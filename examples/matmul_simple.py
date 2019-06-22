#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related

from chipo import *
from hlc import Fsm, Wait

# Example of algorithmically defined state machine through Fsm construct

MEM_AW = Parameter(16)
MEM_DW = Parameter(32)
DIM_BITS = Parameter(16)
PREC = Parameter(16)

clk = Clock()
rst_n = Reset()
ret = Output()
go = Input()

# memory interface
mem_write, mem_req = Output() ** 2
mem_addr = Output(MEM_AW)
mem_wdata = Output(MEM_DW)
mem_rdata_vld = Input()
mem_rdata = Input(MEM_DW)

#mattrix parameters
aBASE, bBASE, cBASE = Input(MEM_AW) ** 3
aSTRIDE, bSTRIDE, cSTRIDE = Input(DIM_BITS) ** 3
aROWS, aCOLS, bCOLS = Input(DIM_BITS) ** 3

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
    Fsm('matmul_fsm', clk, rst_n) [
        ret <= 0,
        ...,
        Wait(go),
        a_i0 <= aBASE,
        c_i0 <= cBASE,
        i <= 0,
        ...,
        While (~(i == aROWS)) [
            b_0j <= bBASE,
            c_ij <= c_i0,
            j <= 0,
            ...,
            While (~(j == bCOLS)) [
                a_ik <= a_i0,
                b_kj <= b_0j,
                acc <= 0,
                k <= 0,
                ..., MEM_read(a_ik), incr(a_ik),
                ..., MEM_read(b_kj), incr(b_kj, bSTRIDE),
                While (~(k == aCOLS)) [
                    ..., incr(k),
                    ..., MEM_read(a_ik), incr(a_ik),          a <= mem_rdata[PREC-1:0],
                    ..., MEM_read(b_kj), incr(b_kj,bSTRIDE),  incr(acc, a[PREC-1:0]*mem_rdata[PREC-1:0]),
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
    ].expand()
].autoGen()

print(matmul.vlog())

