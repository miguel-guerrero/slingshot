#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

WIDTH = Parameter(8)
clk = Clock()
rst_n = Reset()
x = Input(WIDTH)
y = Input(WIDTH)
cat = Output(4)
a = Input()
b = Input()

cater = \
Module().Params(WIDTH).Ios(x, y, cat, clk, rst_n, a, b).Body(
    Combo(Block(name='my_com')).Name('combo_logic').Body(
        cat <= [x[3:2], y[2]],
        cat <= ((a ^ b) & cat) ^ a
    )
)

print(cater.vlog())
