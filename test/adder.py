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

    adder = Module().Ios(cin, x, y, sm, sm_r, sm_zero_r, clk, rst_n)

    com = Combo(Block(name='my_com')).Name('combo_logic')
    com += sm <= x + y + cin
    adder += com

    p = Clocked(clk, rst_n).Name('registering')
    p += sm_r <= sm
    p += sm_zero_r <= (sm == 0)
    p.body = p.genResetLogic()
    adder += p

    print(adder.vlog())
