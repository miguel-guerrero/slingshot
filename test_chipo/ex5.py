#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
from vlog import dump

c=Signal(8)
x=Signal()
stm=(x <= 1)

w=Do() [ stm ].While(c)
print(w)
print(dump(w, 0))
print(dump(w, 1))

