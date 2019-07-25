#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
from hlc import Fsm

behav = sys.argv[0].endswith('vtpg_behav.py')

# Example of algorithmically defined state machine through Fsm construct
clk   = Clock()
rst_n = Reset()
PW, H_BITS, V_BITS     = Param(8), Param(12), Param(12)
hs, vs, vld, rgb       = Out(), Out(), Out(), Out(3*PW)
tHS_START, tHS_END     = In(H_BITS)**2
tHACT_START, tHACT_END = In(H_BITS)**2
tVS_START, tVS_END     = In(V_BITS)**2
tVACT_START, tVACT_END = In(V_BITS)**2
tH_END                 = In(H_BITS)
tV_END                 = In(V_BITS)

y_active = Signal()
cnt = Signal(PW)
x = Signal(H_BITS) 
y = Signal(V_BITS) 

"""
    y = 0;
    do begin

        // Per line loop
        x = 0;
        do begin

            if (x == tHS_START)
                hs = 1;
            else if (x == tHS_END)
                hs = 0;

            if (x == tHACT_START)
                vld = y_active;
            else if (x == tHACT_END)
                vld = 1'b0;

            if (vld)
                cnt = cnt + 1;

            x = x + 1'b1;
            `tick;
        end while (x != tH_END);

        // generate vertical sync as a function of line#
        if (y == tVS_START)
            vs = 1;
        else if (y == tVS_END)
            vs = 0;

        if (y == tVACT_START)
            y_active = 1'b1;
        else if (y == tVACT_END) 
            y_active = 1'b0;

        y = y + 1'b1;
        `tick;
    end while (y != tV_END);
"""
vtpg = \
    Module(clk, rst_n) [
        Fsm(name='control', behav=behav) [
            Do() [
                Do() [
                    Comm('hs setting'),
                    If (x == tHS_START) [ 
                        hs <= 1,
                    ].Elif (x == tHS_END) [ 
                        hs <= 0,
                    ],
                    Comm('vld setting'),
                    If (x == tHACT_START) [
                        vld <= y_active
                    ].Elif (x == tHACT_END) [
                        vld <= 0,
                    ],
                    Comm('cnt increment'),
                    If (vld) [
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
        Combo() [
            rgb <= [cnt, cnt, cnt]
        ]
    ].autoGen()

print(vtpg.vlog())
