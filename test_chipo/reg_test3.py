#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from regs import *
from chipo import *

z = Signal(16)
regA = Reg(
            RW(4, 'x'),
            RO(3, 'y'),
            RW(z),
            name='regA'
       )
regB = Reg(Const(4, 'x'), Rsrv(3, 'rsv1'), RW(30, 'thirty', reset=0xFFFFFFF), name='regB')
regC = Reg(RW(1, 'flag'), RW(64, 'large', reset=0xAB), name='regC')
rb = RegBlock(regA, regB, regC, name='csrs')
rb.breakUp()
print(toGenCsrsXML(rb))
