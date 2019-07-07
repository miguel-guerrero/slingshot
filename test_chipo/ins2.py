#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related

from chipo import *
import vlog

#in this example arguments to FA are pased by name expanding IOs in the call

def NameMapDict(lst):
    return {x.name:x for x in lst}

class FullAdder(Module):

    def __init__(self, name='FA'):
        super().__init__(name=name)
        self.IOs = [In(1, "a"), In(1, "b"), In(1, "cin"), Out(1,"s"), Out(1, "cout")]
        self.a, self.b, self.cin, self.s, self.cout = self.IOs
        log = self.logic()
        self.body += [log]

    @staticmethod
    def FA(cin, a, b, cout, s):
        return (
            cout <= a & b | a & cin | b & cin,
            s <= a ^ b ^ cin 
        )

    def logic(self):
        #log = FullAdder.FA(**{x.name:x for x in self.IOs})
        log = FullAdder.FA(**NameMapDict(self.IOs))
        return Combo(log)


fa = FullAdder()

cin = Signal()
a0, b0, s0, c0   = Signal()**4
a1, b1, s1, cout = Signal()**4

two_adder = Module() [
    fa(cin=cin, a=a0, b=b0, s=s0, cout=c0),
    fa(cin=c0,  a=a1, b=b1, s=s1, cout=cout),
].autoGen()

two_adder.vlogToFiles()

