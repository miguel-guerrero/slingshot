#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
# -------------------------------------------------------------------------------
import sys
sys.path.append("..")  # add path to chipo and related
from chipo import *


def Adder(W=8):
    WIDTH = Param(W)
    SWIDTH = Param(WIDTH)
    clk = Clock()
    rst_n = Reset()
    cin = In()
    x, y = In(WIDTH).Signed() ** 2
    sm, sm_r = Out(SWIDTH).Signed() ** 2
    sm_zero_r = Out()
    res = Var(SWIDTH).Signed()

    return Module(clk, rst_n).Params(WIDTH, SWIDTH) [
               Combo() [
                   res != x + y + cin,
                   sm <= res
               ],
               Clocked() [
                   sm_r <= sm,
                   sm_zero_r <= (sm == 0)
               ]
           ].autoGen()


if __name__ == '__main__':
    adder = Adder()
    print(adder.vlog())
