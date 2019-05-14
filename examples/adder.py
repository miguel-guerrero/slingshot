#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

def genAdder(name='adder', *, W=8):
    WIDTH = Parameter(W)
    SWIDTH = Parameter(WIDTH)
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x, y = Input(WIDTH).Signed() **2
    sm, sm_r = Output(SWIDTH).Signed() **2
    sm_zero_r = Output()
    res = Variable(SWIDTH).Signed()

    return  Module('adder').Params(WIDTH, SWIDTH) [
                Combo() [
                    res != x + y + cin,
                    sm <= res
                ],
                Clocked(clk, rst_n) [
                    sm_r <= sm,
                    sm_zero_r <= (sm == 0)
                ]
            ].autoGen()

if __name__=='__main__':
    adder = genAdder()
    print(adder.vlog())

