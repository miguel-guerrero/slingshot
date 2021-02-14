#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
import helper as h

#in this example IOs is defined as an IoList, but is passed to FA
#one by one using . notation

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

class TwoAdder(Module):
    def __init__(self, name='two_adder'):
        super().__init__(name=name)
        cin, a0, b0, a1, b1 = In()**5
        c0 = Signal()
        s0, s1, cout = Out()**3
        fa = FullAdder()
        self.body = [
            fa(cin=cin, a=a0, b=b0, s=s0, cout=c0),
            fa(cin=c0,  a=a1, b=b1, s=s1, cout=cout),
        ]
        self.autoGen()

two_adder = TwoAdder()
print(two_adder.vlog(recursive=True))

