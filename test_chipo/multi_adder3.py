#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

def Adder(name='adder', W=8):
    WIDTH = Parameter(W)
    SWIDTH = Parameter(WIDTH+1)
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x, y = Input(WIDTH) ** 2
    sm, sm_r = Output(SWIDTH) ** 2
    sm_zero_r = Output()
    res = Var(SWIDTH)
    return Module(name=name) [
            Combo() [
                Declare(res),
                res @ (x + y + cin),
                sm <= res
            ],
            Clocked(clk, rst_n) [
                sm_r <= sm,
                sm_zero_r <= (sm == 0)
            ]
        ].autoGen()

def MultiAdder(name='multi_adder', numAdders=1):
    adder = Adder()
    SW = Parameter(9)
    cin_ = Signal()
    x_, y_ = Signal(8) ** 2
    clk_ = Clock()
    rst_n_ = Reset()

    m = Module(name=f"{name}_numAdders{numAdders}") 
    for i in range(numAdders):
        sumi_ = Signal(SW, name=f"sum{i}")
        m += Instance(adder, 
                ParamMap(SWIDTH=SW, WIDTH=8), 
                PortMap(cin=CInt(0, width=1), x=x_, y=y_, clk=clk_, rst_n=rst_n_,
                        sm=None, sm_r=sumi_, sm_zero_r=None)
             )
    return m.autoGen()

multiAdder = MultiAdder(numAdders=2)
print(multiAdder.vlog(recursive=True))

