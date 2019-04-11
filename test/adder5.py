#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
from chipo import *

if __name__=='__main__':

    WIDTH = Parameter(8)
    SWIDTH = Parameter(9)
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x, y = Input(WIDTH) ** 2
    sm, sm_r  = Output(SWIDTH) ** 2
    sm_zero_r = Output()
    res = Variable(SWIDTH)

    adder = Module(IOs=[sm]).Params(WIDTH,SWIDTH) [
        Combo() [
            res @ (x + y + cin),
            If (res == 2) [
                sm <= 1
            ].Else [
                sm <= res
            ]
        ],
        Clocked(clk, rst_n) [
            sm_r <= sm,
            sm_zero_r <= (sm == 0)
        ].addResetLogic()
    ].autoGen()

    print(adder.vlog())
