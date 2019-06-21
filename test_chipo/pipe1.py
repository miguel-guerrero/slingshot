#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
from hlc import Pipeline

clk = Clock()
rst_n = Reset()
W = Parameter(8)
x, y = Input(W) ** 2
s = Signal(W+1)
s2 = Signal(2*W+2)
x2 = Signal(2*W)
out = Output(2*W)

m = Module('pipe')
pipe = Pipeline('arith', clk, rst_n, keep=[s2, x2]) [
    s <= x+y,
    ...,
    s2 <= s*s,
    ...,
    x2 <= x*x   # note that x is transfered through 2nd pipe stage
]

m += pipe.expand()
m += Comment(', '.join([f"{x}:{v.name}" for x,v in pipe.outs.getDict().items()]))
m += Assign(out, pipe.outs.x2 - 1)

m.autoGen()

print(m.vlog())
