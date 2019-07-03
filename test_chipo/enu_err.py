#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related

from chipo import *
import vlog

States = Enu('IDLE', 'GO', ('DONE',2))
clk = Clock()
rst_n = Reset()
ctl, done = Output() ** 2
state = Signal(States, default='IDLE')
state_nxt = Signal(States)
#state_nxt = Signal(States).Signed()

fsm = Module()

fsm += Combo() [
    Switch(state).
        Case(States.IDLE) [
            state_nxt <= States.GO,
            ctl <= 0
        ].
        Case(States.GO) [
            #state_nxt <= States.DONE,
            state_nxt <= States.DON,
            ctl <= 1
        ].
        Case(States.DONE) [
            state_nxt <= States.IDLE
        ].
        Default(
            state_nxt <= 'IDLE', #can also do this, but no checking here
            ctl <= 0
        )
]

fsm += done <= (state==States.DONE)

fsm += Clocked(clk, rst_n) [
    state <= state_nxt
]

fsm.autoGen()

print(fsm.vlog())
