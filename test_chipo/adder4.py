#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
from chipo import *

if __name__=='__main__':
    vlog.setIndent('\t')
    WIDTH = Parameter(8)
    SWIDTH = Parameter(WIDTH+1)
    #SWIDTH = WIDTH+1
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x = Input(WIDTH)
    y = Input(WIDTH)
    sm = Output(SWIDTH)
    sm_r = Output(SWIDTH)
    sm_zero_r = Output()
    res = Variable(SWIDTH)

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