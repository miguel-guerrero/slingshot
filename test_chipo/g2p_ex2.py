#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

#integrating chipo into a g2p flow

def genAdder(name, params):
    WIDTH = Parameter(params.WIDTH)
    SWIDTH = Parameter(WIDTH+1)
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x, y = Input(WIDTH) ** 2
    sm, sm_r = Output(SWIDTH) ** 2
    sm_zero_r = Output()
    res = Variable(SWIDTH)

    mod = (
        Module(name)
            .Params(WIDTH, SWIDTH)
            .Ios(cin, x, y, sm, sm_r, sm_zero_r, clk, rst_n) [
                Combo() [
                    res.eq(x + y + cin),
                    sm <= res
                ],
                Clocked(clk, rst_n) [
                    sm_r <= sm,
                    sm_zero_r <= (sm == 0)
                ]
            ]
    ).elab()

    mod.userResult.area = 0 #generate g2p compatible results
    return mod

adder = generateG2p('adder', {'WIDTH':32}, {'WIDTH':8}, genAdder)
print(adder)

x0, y0 = Signal() ** 2

#default mapping
ioMap = {k.name:k for k in adder.IOs}
#overrides
ioMap['x']=x0
ioMap['y']=y0

#instantiate a g2p module in chipo
i = InstanceG2p(adder, {'A':1}, ioMap, 'adder_0')
print(vlog.dump(i, 0))

