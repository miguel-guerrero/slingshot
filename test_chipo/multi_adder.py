#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

WIDTH = Param(8)
SWIDTH = Param(WIDTH+1)
clk = Clock()
rst_n = Reset()
cin = In()
x, y = In(WIDTH) ** 2
sm, sm_r = Out(SWIDTH), Out(SWIDTH)
sm_zero_r = Out()
res = Var(SWIDTH)

adder = Module().Params(WIDTH) [
    Combo(Block(name='my_com')).Name('combo_logic') [
        res.eq(x + y + cin),
        sm <= res
    ],
    Clocked(clk, rst_n).Name('registering') [
        sm_r <= sm,
        sm_zero_r <= (sm == 0)
    ]
].autoGen()

multi_adder = Module()

cin_ = Signal()
x_, y_ = Signal(8) ** 2
clk_ = Clock()
rst_n_ = Reset()

multi_adder += Instance(
    adder, {'WIDTH':WIDTH, 'SWIDTH':SWIDTH}, 
    {'cin': cin_, 'x':x_, 'clk':clk_, 'rst_n':rst_n_}
)

multi_adder.autoGen()

print(adder.vlog())
print(multi_adder.vlog())
