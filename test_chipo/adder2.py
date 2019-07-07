#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

if __name__=='__main__':
    clk = Clock()
    rst_n = Reset()
    cin = In()
    x = In(8)
    y = In(8)
    sm = Out(9)
    sm_r = Out(9)
    sm_zero_r = Out()
    res = Var(9)

    adder=\
    Module(cin, x, y, sm, sm_r, sm_zero_r, clk, rst_n).Body(
        Combo(Block(name='combo_logic'), name='combo_logic').Body(
            res.eq(x + y + cin),
            sm <= res
        ),
        Clocked(clk, rst_n, name='registering').Body(
            sm_r <= sm,
            sm_zero_r <= (sm == 0)
        ).addResetLogic()
    )

    print(adder.vlog())
