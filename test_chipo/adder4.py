#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

if __name__=='__main__':
    WIDTH = Param(8)
    SWIDTH = Param(WIDTH+1)
    #SWIDTH = WIDTH+1
    clk = Clock()
    rst_n = Reset()
    cin = In()
    x = In(WIDTH)
    y = In(WIDTH)
    sm = Out(SWIDTH)
    sm_r = Out(SWIDTH)
    sm_zero_r = Out()
    res = Var(SWIDTH)

    adder=(
        Module()
            .Params(WIDTH, SWIDTH)
            .Ios(cin, x, y, sm, sm_r, sm_zero_r, clk, rst_n)
            .Body(
                Combo(Block(name='my_com')).Name('combo_logic').Body(
                    res.eq(x + y + cin),
                    sm <= res
                ),
                Clocked(clk, rst_n).Name('registering').Body(
                    sm_r <= sm,
                    sm_zero_r <= (sm == 0)
                ).addResetLogic()
            )
    )

    print(adder.vlog())
