#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

def genAdder(name='adder'):
    WIDTH = Parameter(8)
    SWIDTH = Parameter(WIDTH+1)
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x, y = Input(WIDTH) ** 2
    sm, sm_r = Output(SWIDTH) ** 2
    sm_zero_r = Output()
    res = Variable(SWIDTH)
    m = Module(name) [
            Combo() [
                Declare(res),
                res.eq(x + y + cin),
                sm <= res
            ],
            Clocked(clk, rst_n) [
                sm_r <= sm,
                sm_zero_r <= (sm == 0)
            ]
        ].autoGen()

    print(m.vlog())
    return m

def genMultiAdder(name='multi_adder', numAdders=1):

    adder = genAdder()

    WIDTH = Parameter(8)
    SWIDTH = Parameter(WIDTH+1)

    cin_ = Signal()
    x_, y_ = Signal(8) ** 2
    clk_ = Clock()
    rst_n_ = Reset()

    m = Module(f"{name}_numAdders{numAdders}") 

    for i in range(numAdders):
        sumi_ = Signal(SWIDTH, name=f"sum{i}")
        m += Instance(adder, 
                ParamMap(WIDTH=WIDTH, SWIDTH=SWIDTH), 
                PortMap(cin=cin_, x=x_, clk=clk_, rst_n=rst_n_, 
                        sm_r=sumi_, sm_zero_r=None),
                insName=f"{adder.name}_{i}"
             )
    m.autoGen()

    print(m.vlog())
    return m

multiAdder = genMultiAdder(numAdders=2)

