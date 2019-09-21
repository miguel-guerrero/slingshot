#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
from hlc import Fsm

#Generate behavioral verilog if the name ends with _behav.py so we can create 
#a sym-link to the same file and easily compare RTL and behavioral outputs
behav = sys.argv[0].endswith('_behav.py')

#Simple Video test pattern generator

# Example of algorithmically defined state machine through Fsm construct
clk   = Clock()
rst_n = Reset()
PW, H_BITS, V_BITS     = Param(8), Param(12), Param(12)

#syncs and output/valid 
hs, vs, rgb_vld, rgb   = Out(), Out(), Out(), Out(3*PW)

#Horizontal timing config inputs
tHS_START, tHS_END     = In(H_BITS)**2   #h sync timing (in pixels)
tHACT_START, tHACT_END = In(H_BITS)**2   #h active video timings (in pixels)
tH_END                 = In(H_BITS)      #line length (in pixels)

#Vertical timing config inputs
tVS_START, tVS_END     = In(V_BITS)**2   #v sync timings (in lines)
tVACT_START, tVACT_END = In(V_BITS)**2   #v active video (in lines)
tV_END                 = In(V_BITS)      #frame height (in lines)

y_active = Signal()
cnt = Signal(PW)
x = Signal(H_BITS) 
y = Signal(V_BITS) 

vtpg = \
    Module(clk, rst_n) [
        Fsm(name='control', behav=behav) [
            Do() [
                Do() [
                    Comm('create h sync'),
                    If (x == tHS_START) [ 
                        hs <= 1,
                    ].Elif (x == tHS_END) [ 
                        hs <= 0,
                    ],
                    Comm('rgb_vld setting'),
                    If (x == tHACT_START) [
                        rgb_vld <= y_active
                    ].Elif (x == tHACT_END) [
                        rgb_vld <= 0,
                    ],
                    Comm('pixel cnt increment'),
                    If (rgb_vld) [
                        cnt <= cnt + 1,
                    ],
                    x <= x + 1,
                    ...,
                ].While (x != tH_END),

                If (y == tVS_START)   [ vs <= 1 ].       Elif (y == tVS_END)   [ vs <= 0 ],
                If (y == tVACT_START) [ y_active <= 1 ]. Elif (y == tVACT_END) [ y_active <= 0 ],
                y <= y + 1,
                x <= 0,
                ...,
            ].While (y != tVACT_END),
        ],
        rgb <= [cnt, cnt, cnt]
    ].autoGen()

print(vtpg.vlog())
