#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

WIDTH = Parameter(8)
SWIDTH = Parameter(WIDTH+1)
clk = Clock()
rst_n = Reset()
cin = Input()
x, y = Input(WIDTH) ** 2
sm, sm_r = Output(SWIDTH), Output(SWIDTH)
sm_zero_r = Output()
res = Variable(SWIDTH)

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
