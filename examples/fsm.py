#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related

from chipo import *
import vlog

States = Enu('IDLE', 'GO', 'DONE')
clk = Clock()
rst_n = Reset()
ctl = Output()
done = Output()
state, state_nxt = Signal(States) ** 2

fsm = Module()

fsm += Combo() [
    Switch(state).
        Case(States.IDLE) [
            state_nxt <= States.GO,
            ctl <= 0
        ].
        Case(States.GO) [
            state_nxt <= States.DONE,
            ctl <= 1
        ].
        Case(States.DONE) [
            state_nxt <= States.IDLE
        ].
        Default(
            state_nxt <= 'IDLE',
            ctl <= 0
        )
]

fsm += Assign(done, state==States.DONE)

fsm += Clocked(clk, rst_n) [
    state <= state_nxt
]

fsm.autoGen()

print(fsm.vlog())
