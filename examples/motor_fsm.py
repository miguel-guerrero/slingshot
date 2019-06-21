#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related

from chipo import *
from hlc import Fsm, Wait

# Example of algorithmically defined state machine through Fsm construct

clk = Clock()
rst_n = Reset()
activate, up_limit, dn_limit = Input() ** 3
motor_up_q, motor_dn_q = Output() ** 2
motor_up = Variable()
motor_dn = Variable()
print(
    Module('motor_fsm', IOs=[motor_up_q, motor_dn_q]) [
        Fsm('control', clk, rst_n) [
            Wait(activate),
            If (up_limit) [
                motor_dn != 1,
                ...,  
                Wait(dn_limit),
                motor_dn != 0,
            ].Else [
                motor_up != 1,
                ...,  
                Wait(up_limit),
                motor_up != 0,
            ]
        ].expand(),
    ].autoGen().vlog()
)
