#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

#testing nested structures

if __name__=='__main__':
    #W = Parameter(8)
    W = 8

    Sums = Rec() [
        Field(BitVec(W), "x"),
        Field(BitVec(W), "y"),
        Field(BitVec(W), "z"),
        Field(BitVec(W), "w")
    ]

    Args = Rec() [
        Field(Sums , "s1"),
        Field(BitVec(), "cin"),
        Field(Sums , "s2"),
    ]

    clk = Clock()
    rst_n = Reset()
    ins = In(Args)
    sm = Output(W+2)
    sm_r = Output(W+2)
    sm_zero_r = Output()

    adder = Module()

    com = Combo(Block(name='my_com')).Name('combo_logic')
    com += sm <= ins.s1.x + ins.s1.y + ins.s1.z + ins.s1.w + \
                 ins.s2.x + ins.s2.y + ins.s2.z + ins.s2.w + ins.cin
    adder += com

    p = Clocked(clk, rst_n).Name('registering') [
        sm_r <= sm,
        sm_zero_r <= (sm == 0),
    ]
    adder += p
    adder.autoGen()

    print(adder.vlog())
