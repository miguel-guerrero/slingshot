#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

if __name__=='__main__':
    NUM_INP = Param(8)
    DW = Param(32)
    clk = Clock()
    rst_n = Reset()
    a = In(5)
    tbl = Out(20)

    ArgT = Array(BitVec(DW), NUM_INP)

    ins = Signal(ArgT)

    adder = Module()

    com = Combo(name='combo_logic')
    com += tbl <= ins[a]
    adder += com

    adder.autoGen()

    print(adder.vlog())
