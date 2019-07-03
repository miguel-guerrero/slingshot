#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related

from chipo import *

def Counter(cntW=8):
    WIDTH = Param(cntW)
    clk, rst_n = Clock(), Reset()
    inc, clr = In() ** 2
    max_val = In(WIDTH)
    eq, cnt = Out(), Out(WIDTH)
    return Module(clk, rst_n) [
            Combo() [
                eq <= (cnt == max_val),
            ],
            Comment('clear and increment logic', 'goes here'),
            Clocked() [
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
    counter = Counter()

    #print verilog code for it
    print(counter.vlog(recursive=True))
