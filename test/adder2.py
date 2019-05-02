#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
from chipo import *

if __name__=='__main__':
    vlog.setIndent('\t')
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x = Input(8)
    y = Input(8)
    sm = Output(9)
    sm_r = Output(9)
    sm_zero_r = Output()
    res = Variable(9)

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
