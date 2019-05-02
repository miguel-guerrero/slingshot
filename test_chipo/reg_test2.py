#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
from regs import *

z = Signal(16)
regA = Reg( 
            RW(4, 'x'), 
            RO(3, 'y'),
            RW(z),
            name='regA'
       )
regB = Reg(Const(4, 'x'), Rsrv(3, 'rsv1'), name='regB')
rb = RegBlock(regA, regB, name='csrs')
print(toGenCsrsXML(rb))
