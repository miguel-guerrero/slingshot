#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
from chipo import *

class Counter(Module):

    def __init__(self, name='counter', *, cntW=8):
        super().__init__(name)
        WIDTH = Parameter(cntW)
        clk, rst_n = Clock(), Reset()
        en, clr = Input() ** 2
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
                ].Elif (en) [
                    cnt <= cnt + 1
                ]
            ]
        ]
        self.autoGen()



if __name__=='__main__':

    #start generation
    cntr = Counter()

    #print verilog code for it
    print(cntr.vlog(recursive=True))
