#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
from hlc import Pipeline

# example of auto-pipelining

def Abs(x):
    return IfCond(x < 0, -x, x)
    
# IO object definition
clk = Clock()
rst_n = Reset()
W = Param(8)
x0, y0, x1, y1 = In(W) ** 4
dx, dy = Signal(W+1).Signed() ** 2
adx, ady = Signal(W+1) ** 2
res = Signal(W+2)

# flow control for pipeline from external world
vld_up, rdy_dn = In() ** 2

# pipeline result
sad_res = Out(W+2)

# flow control results for the pipeline
sad_vld, sad_rdy = Out() ** 2


# Module definition
pipe = Module(sad_res, sad_vld, sad_rdy)

# pipe stage boundaries set by ..., vld/rdy flow control (optional)
sad = Pipeline(clk, rst_n, keep=[res], vld=vld_up, rdy=rdy_dn) [
    dx <= x1 - x0,
    dy <= y1 - y0,
    ...,
    While(dx < 0) [
        adx <= Abs(dx),
        ...,
        ady <= Abs(dy),
    ],
    ...,
    res <= adx + ady
]

pipe += sad.expand()

print(pipe.autoGen().vlog())
