#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

#testing nested structures

if __name__=='__main__':
    W = Param(8)
    #W = 8

    Sums = Rec() [
        Field(BitVec(W), "x"),
        Field(BitVec(W), "y"),
        Field(BitVec(W), "z"),
        Field(BitVec(W), "w")
    ]

    Args = Rec() [
        Field(Sums , "s"),
        Field(BitVec(), "cin")
    ]

    clk = Clock()
    rst_n = Reset()
    ins = In(Args)
    sm = Out(W+2)
    sm_r = Out(W+2)
    sm_zero_r = Out()

    adder = Module()

    com = Combo(name='combo_logic')
    com += sm <= ins.s.x + ins.s.y + ins.s.z + ins.s.w + ins.cin
    adder += com

    p = Clocked(clk, rst_n, name='registering') [
        sm_r <= sm,
        sm_zero_r <= (sm == 0),
    ]
    adder += p
    adder.autoGen()

    print(adder.vlog())
