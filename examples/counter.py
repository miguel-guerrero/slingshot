#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related

from chipo import *

def genCounter(name='counter', *, cntW=8):
    WIDTH = Parameter(cntW)
    clk, rst_n = Clock(), Reset()
    inc, clr = Input() ** 2
    max_val = Input(WIDTH)
    eq, cnt = Output(), Output(WIDTH)
    return Module(name) [
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
        ].autoGen()



if __name__=='__main__':
    #start generation
    cntr = genCounter()

    #print verilog code for it
    print(cntr.vlog(recursive=True))
