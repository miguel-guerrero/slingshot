#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

if __name__=='__main__':
    WIDTH = Param(8)
    SWIDTH = Param(WIDTH)
    clk = Clock()
    rst_n = Reset()
    cin = In()
    x = In(WIDTH).Signed()
    y = In(WIDTH).Signed()
    sm = Out(SWIDTH).Signed()
    sm_r = Out(SWIDTH).Signed()
    sm_zero_r = Out()
    res = Var(SWIDTH).Signed()

    adder=(
        Module()
            .Params(WIDTH, SWIDTH)
            .Ios(cin, x, y, sm, sm_r, sm_zero_r, clk, rst_n)
            .Body(
                Combo(Block(name='my_com')).Name('combo_logic').Body(
                    res != x + y + cin,
                    sm <= res
                ),
                Clocked(clk, rst_n).Name('registering').Body(
                    sm_r <= sm,
                    sm_zero_r <= (sm == 0)
                ).addResetLogic()
            )
    )

    print(adder.vlog())
