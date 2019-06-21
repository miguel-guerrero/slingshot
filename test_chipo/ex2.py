#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
import vlog

if __name__=='__main__':
    clk = Clock()
    rst_n = Reset()
    cin = Input()
    x = Input(10)
    y = Input(10)
    sm = Output(11)

    a = Signal()
    b = Signal(3)
    c = Signal(3)
    d = Signal(3)

    adder =  Module(IOs=(cin, x, y, sm, clk, rst_n))

    if True:
        p = Clocked(clk, rst_n).Name('my_process_p') [
             If(a == 1).Then(
                 If(2 == b) [
                    c<=4,
                    b<=5
                 ].Else [
                    a<=3,
                    b<=6
                 ]
             ).Else(
               a <= b,
               a <= 1 + b*(3 + 5*a),
               b <= b*3 - CInt(5, width=3).Signed().Hex()*d,
               a <= b & a | ~(c & a),
               a <= 1 & (a > 1)
             ),
             If (a < 22) [
                a <= a + 1
             ]
        ]
        p += (c <= c + 1)
        p += While (a < 5) [
                a <= a + 1,
                c <= c - 1
             ]
        adder += p

    vlog.setIndent('    ')
    if True:
        q = Clocked(clk, rst_n).Name('my_process_q')
        q += (c <= c + 3)
        q += (a <= a + 33)
        h = q.genResetLogic()
        q.body = h.Name('q_with_reset')
        adder += q
        print(vlog.dump(h))

    com = Combo(Block(name='my_com'))
    com += a <= b + 1

    adder += com

    if True:
        adder += Declare(Signal(name='a0'))
        adder += Declare(Signal(name='b0'))
        adder += Declare(Signal(name='clk'))
        # for existing verilog modules
        textParamMap={"W":1, "A":2}
        textIoMap={"a":"a0", "b":"b0", "clk":"clk"}
        i0 = InstanceLegacy('submod', textParamMap, textIoMap, insName="submod_0")
        adder += i0
        ib = InstanceLegacy('submod', {}, textIoMap, insName="submod_1")
        adder += ib

        res = Output(32)
        op = Input(10)
        a = Input(32)
        b2 = Input(32)
        alu = Module().Ios(res, op, a, b2).Body(
            Combo().Body(
                res <= a + b2
            )
        )

        # for chipo modules
        a0 = Signal(32)
        b0 = Signal(32)
        res0 = Signal(32)
        op0 = Signal(10, default=0)
        i2 = Instance(alu, {}, {a:a0, b2:b0, op:op0, res:res0}, 'alu_0')
        adder += i2


    print('-------------- verilog --------------')
    print(vlog.dump(adder))
    print('-------------- repr --------------')
    print(repr(adder))
    print('-------------- m.getInstances() --------------')
    print(repr(adder.getInstances()))

