#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
import vlog

if __name__=='__main__':
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x = Input(10)
    y = Input(10)
    sm = Output(11)
    sm_r = Output(11)
    sm_zero_r = Output()

    a = Var()
    b = Var(3)
    c = Var(3)

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
    vlog.setStyle(indent='.   ')
    print(adder.vlog())
    print('-------------- repr --------------')
    print(repr(adder))

