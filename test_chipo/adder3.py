#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

if __name__=='__main__':
    WIDTH = Param(8)
    SWIDTH = Param(9)
    clk = Clock()
    rst_n = Reset()
    cin = In()
    x = In(WIDTH)
    y = In(WIDTH)
    sm = Out(SWIDTH)
    sm_r = Out(SWIDTH)
    sm_zero_r = Out()
    res = Var(SWIDTH)

    adder = \
    Module(cin, x, y, sm, sm_r, sm_zero_r, clk, rst_n, params=[WIDTH,SWIDTH]) [
        Combo(name='combo_logic') [
            res @ (x + y + cin),
            sm <= res
        ],
        Clocked(clk, rst_n, name='registering') [
            sm_r <= sm,
            sm_zero_r <= (sm == 0)
        ].addResetLogic()
    ]

    print(adder.vlog())
