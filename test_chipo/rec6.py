#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

#testing nested structures

if __name__=='__main__':
    #W = Parameter(8)
    W = 8


    Args = Rec() [
        Field(
            Rec() [
                Field(BitVec(W), "x"),
                Field(BitVec(W), "y"),
                Field(BitVec(W), "z"),
                Field(BitVec(W), "w")
            ], "s1"
        ),
        Field(BitVec(), "cin"),
    ]

    clk = Clock()
    rst_n = Reset()
    ins = In(Args)
    sm = Output(W+2)
    sm_r = Output(W+2)
    sm_zero_r = Output()

    adder = Module()

    com = Combo(Block(name='my_com')).Name('combo_logic')
    x = Var(W)
    com += sm <= ins.s1.x + ins.s1.y[3:2] + ins.s1.z + ins.s1.w + ins.cin
    adder += com

    p = Clocked(clk, rst_n).Name('registering') [
        sm_r <= sm,
        sm_zero_r <= (sm == 0),
    ]
    adder += p
    adder.autoGen()

    print(adder.vlog())
