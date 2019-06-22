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
motor_up, motor_dn = Output() ** 2
print(
    Module('motor_fsm') [
        Fsm('control', clk, rst_n) [
            Wait(activate),
            If (up_limit) [
                motor_dn <= 1,
                ...,  
                Wait(dn_limit),
                motor_dn <= 0,
            ].Else [
                motor_up <= 1,
                ...,  
                Wait(up_limit),
                motor_up <= 0,
            ]
        ].expand(),
    ].autoGen().vlog()
)
