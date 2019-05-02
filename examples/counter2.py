#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.insert(0, "..")

from chipo import *

#another style, see counter.py
class Counter2(Module):

    def __init__(self, name='counter2', *, cntW=8):
        super().__init__(name)
        WIDTH = Parameter(cntW)
        clk, rst_n = Clock(), Reset()
        inc, clr = Input() ** 2
        max_val = Input(WIDTH)
        eq, cnt = Output(), Output(WIDTH)

        self.body = [
            Combo() [
                eq <= (cnt == max_val),
            ],
            Comment('clear and increment logic', 'goes here'),
            Clocked(clk, rst_n) [
                If (clr) [
                    Comment('clear has priority'),
                    cnt <= 0
                ].Elif (inc) [
                    cnt <= cnt + 1
                ]
            ]
        ]
        self.autoGen()



if __name__=='__main__':
    #start generation
    cntr2 = Counter2()

    #dump verilog code for it
    with open(cntr2.name+'.v', "w") as f:
        f.write(cntr2.vlog())

