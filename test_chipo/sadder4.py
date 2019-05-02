#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

if __name__=='__main__':
    vlog.setIndent('\t')
    WIDTH = Parameter(8)
    SWIDTH = Parameter(WIDTH)
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x = Input(WIDTH).Signed()
    y = Input(WIDTH).Signed()
    sm = Output(SWIDTH).Signed()
    sm_r = Output(SWIDTH).Signed()
    sm_zero_r = Output()
    res = Variable(SWIDTH).Signed()

    m=(
        Module('adder')
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

    print(m.vlog())
