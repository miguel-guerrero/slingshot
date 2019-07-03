#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
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
    res = Var(SWIDTH)

    adder = Module(sm).Params(WIDTH,SWIDTH) [
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
