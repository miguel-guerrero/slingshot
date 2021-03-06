#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
import g2p as g
import vlog

#integrating chipo into a g2p flow

def Adder(modBaseName='adder', passedParamDict={}):
    name, paramDict, params = g.processParams(
                                modBaseName, passedParamDict, {'WIDTH':8})

    # create the module with chipo
    WIDTH = Param(params.WIDTH)
    SWIDTH = Param(WIDTH+1)
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x = Input(WIDTH)
    y = Input(WIDTH)
    sm = Output(SWIDTH)
    sm_r = Output(SWIDTH)
    sm_zero_r = Output()
    res = Var(SWIDTH)

    mod = (
        Module(name=name)
            .Params(WIDTH, SWIDTH)
            .Ios(cin, x, y, sm, sm_r, sm_zero_r, clk, rst_n)
            .Body(
                Combo(Block(name='my_com')).Name('combo_logic').Body(
                    res.eq(x + y + cin),
                    sm <= res
                ),
                Clocked(clk, rst_n).Name('registering').Body(
                    sm_r <= sm,
                    sm_zero_r <= (sm == 0)
                ).addResetLogic()
            )
    )

    #generate g2p compatible results
    mod.userResult.area = 0
    mod.paramDict = paramDict

    vlogToFile(mod)
    return mod


adder = Adder('adder', {'WIDTH':32})
print(adder)

x0 = Signal()
y0 = Signal()

ioMap = {k.name:k for k in adder.IOs}
ioMap['x']=x0
ioMap['y']=y0

#instantiate a g2p module in chipo
i = InstanceG2p(adder, g.toDict(A=1), ioMap, 'adder_0')

print(vlog.dump(i, 0))

