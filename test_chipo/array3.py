#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

if __name__=='__main__':
    W = Param(8)
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    sm = Out(W+2)
    sm_r = Out(W+2)
    sm_zero_r = Out()

    ArgT = Array(BitVec(20), 10, 5, 2)
    Arr2 = Array(ArgT, 2, 2)

    ins = Signal(Arr2)

    adder = Module()

    com = Combo(name='combo_logic')
    com += sm <= ins[1,1][9,4,1]
    adder += com

    adder.autoGen()

    print(adder.vlog())
