#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
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
