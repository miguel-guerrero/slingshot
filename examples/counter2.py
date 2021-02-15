#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
# -------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related

from chipo import *


# another style, see counter.py
class Counter2(Module):
    def __init__(self, name='counter2', *, cntW=8):
        super().__init__(name=name)
        WIDTH = Param(cntW)
        clk, rst_n = Clock(), Reset()
        inc, clr = In() ** 2
        max_val = In(WIDTH)
        eq, cnt = Out(), Out(WIDTH)

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


if __name__ == '__main__':
    # start generation
    cntr2 = Counter2()

    # dump verilog code for it
    with open(cntr2.name+'.v', "w") as f:
        f.write(cntr2.vlog())
