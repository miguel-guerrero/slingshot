#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

class FullAdder(Module):
    def __init__(self, name='FA'):
        super().__init__(name=name)
        self.IOs = h.IoList(In(1, "cin"), In(1, "a"), In(1, "b"), Out(1,"s"), Out(1, "cout"))
        self.body = [Combo(FullAdder.FA(self.IOs))]

    @staticmethod
    def FA(io):
        return (
            io.s <= io.a ^ io.b ^ io.cin,
            io.cout <= io.a & io.b | io.a & io.cin | io.b & io.cin,
        )


fa = FullAdder()

cin = Signal()
a0, b0, s0, c0   = Signal()**4
a1, b1, s1, cout = Signal()**4

two_adder = Module() [
    fa(cin=cin, a=a0, b=b0, s=s0, cout=c0),
    fa(cin=c0,  a=a1, b=b1, s=s1, cout=cout),
].autoGen()

print(two_adder.vlog(recursive=True))

