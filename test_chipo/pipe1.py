#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
from hlc import Pipeline
import vlog

clk = Clock()
rst_n = Reset()
W = Parameter(8)
x, y = Input(W) ** 2
add = Signal(W+1)
add_sqr = Signal(2*W+2)
x_sqr = Signal(2*W)
out = Output(2*W)

pipe = Module()
arith = Pipeline(clk, rst_n, keep=[add_sqr, x_sqr]) [
    add <= x+y,
    ...,
    add_sqr <= add*add,
    ...,
    x_sqr <= x*x   # note that x is transfered through 2nd pipe stage
]

pipe += arith
pipe += Comment(', '.join([f"{x}:{v.name}" for x,v in arith.outs.getDict().items()]))
pipe += out <= arith.outs.x_sqr - 1


pipe.autoGen()

vlog.setStyle(useLogic=True)
print(pipe.vlog())
