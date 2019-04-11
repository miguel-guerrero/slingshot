#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
from chipo import *

if __name__=='__main__':
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x = Input(10)
    y = Input(10)
    sm = Output(11)
    sm_r = Output(11)
    sm_zero_r = Output()

    a = Variable()
    b = Variable(3)
    c = Variable(3)

    adder =  Module().Ios(cin, x, y, sm, clk, rst_n)

    com = Combo(Block(name='my_com')).Name('combo_logic')
    com += sm <= x + y + cin
    adder += com

    if True:
        p = Clocked(clk, rst_n).Name('registering')
        p += sm_r <= sm
        p += sm_zero_r <= (sm == 0)
        p.body = p.genResetLogic()
        adder += p

    print('-------------- verilog --------------')
    setIndent('.   ')
    print(adder.vlog())
    print('-------------- repr --------------')
    print(repr(adder))

