#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
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
print(
    Module('motor_fsm', IOs=[motor_up_q, motor_dn_q]) [
        Fsm('control', clk, rst_n) [
            Wait(activate),
            If (up_limit) [
                motor_dn_q <= 1,
                ...,  
                Wait(dn_limit),
                motor_dn_q <= 0,
            ].Else [
                motor_up_q <= 1,
                ...,  
                Wait(up_limit),
                motor_up_q <= 0,
            ]
        ].expand(),
    ].autoGen().vlog()
)
