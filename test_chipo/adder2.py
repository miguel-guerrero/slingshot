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
    cin = Input()
    x = Input(8)
    y = Input(8)
    sm = Output(9)
    sm_r = Output(9)
    sm_zero_r = Output()
    res = Var(9)

    adder=\
    Module(IOs=(cin, x, y, sm, sm_r, sm_zero_r, clk, rst_n)).Body(
        Combo(Block(name='my_com')).Name('combo_logic').Body(
            res.eq(x + y + cin),
            sm <= res
        ),
        Clocked(clk, rst_n).Name('registering').Body(
            sm_r <= sm,
            sm_zero_r <= (sm == 0)
        ).addResetLogic()
    )

    print(adder.vlog())
