#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related

from chipo import *
from iolist import IoList

#in this example IOs is defined as an IoList, so they can be passsed
#as a group and accessed using . notation


class FullAdder(Module):
    def __init__(self, name='FA'):
        super().__init__(name=name)
        self.IOs = IoList(In(1, "cin"), In(1, "a"), In(1, "b"), Out(1,"s"), Out(1, "cout"))
        self.body += [self.logic()]

    @staticmethod
    def FA(cin, a, b, s, cout):
        return (
            s <= a ^ b ^ cin,
            cout <= a & b | a & cin | b & cin,
        )

    def logic(self):
        io = self.IOs
        return Combo(FullAdder.FA(io.cin, io.a, io.b, io.s, io.cout))


fa = FullAdder()

cin = Signal()
a0, b0, s0, c0   = Signal()**4
a1, b1, s1, cout = Signal()**4

two_adder = Module() [
    fa(cin=cin, a=a0, b=b0, s=s0, cout=c0),
    fa(cin=c0,  a=a1, b=b1, s=s1, cout=cout),
].autoGen()

print(two_adder.vlog(recursive=True))

