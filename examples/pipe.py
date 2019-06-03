#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

# example of auto-pipelining

def Abs(x):
    return IfCond(x < 0, -x, x)
    
# IO object definition
clk = Clock()
rst_n = Reset()
W = Parameter(8)
x0, y0, x1, y1 = Input(W) ** 4
dx, dy = Signal(W+1).Signed() ** 2
adx, ady = Signal(W+1) ** 2
res = Signal(W+2)

# flow control for pipeline from external world
vld_up, rdy_dn = Input() ** 2

# pipeline result
sad_res = Output(W+2)

# flow control results for the pipeline
sad_vld, sad_rdy = Output() ** 2


# Module definition
m = Module('pipe', IOs=(sad_res, sad_vld, sad_rdy))

# pipe stage boundaries set by ..., vld/rdy flow control (optional)
sad = Pipeline('sad', clk, rst_n, keep=[res], vld=vld_up, rdy=rdy_dn) [
    dx <= x1 - x0,
    dy <= y1 - y0,
    ...,
    adx <= Abs(dx),
    ady <= Abs(dy),
    ...,
    res <= adx + ady
]

m += sad.expand()

print(m.autoGen().vlog())
