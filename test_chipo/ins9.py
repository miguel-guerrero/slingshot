#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *

#in this example IOs is defined as an IoList, but is passed to FA
#one by one using . notation

class FullAdder(Module):
    def __init__(self, name='FA'):
        super().__init__(name=name)
        with self.IOs:
            a, b, cin = In()**3
            s, cout = Out()**2
        self.body = [Combo(FullAdder.FA(self.IOs))]

    @staticmethod
    def FA(io):
        return (io.s    <= io.a ^ io.b ^ io.cin,
                io.cout <= io.a & io.b | io.a & io.cin | io.b & io.cin)

class MultiAdder(Module):
    def __init__(self, N=1, name='multi_adder'):
        super().__init__(name=name)
        cin, a, b, cout, s = In(), In(N), In(N), Out(), Out(N)
        c = Signal(N)
        fa = FullAdder()
        cy = cin
        for i in range(N):
            self += fa(cin=cy, a=a[i], b=b[i], s=s[i], cout=c[i])
            cy = c[i]
        self += cout <= c[N-1]
        self.autoGen()

multi_adder = MultiAdder(8)
print(multi_adder.vlog(recursive=True))

