#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append('..')
import g2p as dut
import unittest

class MakoBasicTests(unittest.TestCase):

    def testRenderBasic(self):
        s = dut.MakoRenderer.renderStr('hello ${name}', {'name':'miguel'})[0].strip()
        self.assertEqual(s, "hello miguel")

    def _estRenderResult(self):
        class OutStruct:
            x=1
            y=2
        s = dut.MakoRenderer.renderStr('hello ${name}<% result.x=999 %>', 
                {'name':'miguel'}, result=OutStruct)[0].strip()
        self.assertEqual(s, "hello miguel")
        self.assertEqual(OutStruct.x, 999)

    def testRenderBasicFromFileDefaults(self):
        s = dut.MakoRenderer.renderFile('mako/mk.test0.v', {})[0].strip()
        with open('mako/mk.test0.v.exp') as f:
            self.assertEqual(s, f.read().strip())

    def testRenderBasicFromFile(self):
        s = dut.MakoRenderer.renderFile('mako/mk.test1.v', {'N':16})[0].strip()
        with open('mako/mk.test1.v.exp') as f:
            self.assertEqual(s, f.read().strip())

class GenerateBasicTests(unittest.TestCase):

    def testGetDefaultName(self):
        self.assertEqual('adder',
            dut.getDefaultName('adder', {}, {'N':10, 'M':20}))

    def testGetDefaultNameWithOverrides(self):
        self.assertEqual('adder_A1_N25',
            dut.getDefaultName('adder', {'N':25, 'A':1}, {'N':10, 'M':20, 'A':2}))

    def testGetDefaultNameWithDummyOverride(self):
        self.assertEqual('adder',
            dut.getDefaultName('adder', {'N':10}, {'N':10, 'M':20}))

    def testGetDefaultNameWithNonDefault(self):
        self.assertEqual('adder_P10',
            dut.getDefaultName('adder', {'P':10}, {'N':10, 'M':20}))

    def estFinalParams(self):
        finalParams = dut.getFinalParams({'N':16}, {'N':10, 'M':20})
        self.assertEqual({'N':16, 'M':20}, finalParams)
        

class FileNewer(unittest.TestCase):

    def testIsFileNewer(self):
        self.assertTrue(dut.isFileNewer('newer', 'older'))
        self.assertFalse(dut.isFileNewer('older', 'newer'))
        self.assertFalse(dut.isFileNewer('older', 'older'))


class InOut(unittest.TestCase):

    def testInput(self):
        self.assertEqual(f"{dut.Input('a')}", 'input a')
        self.assertEqual(f"{dut.Input(name='a')}", 'input a')
        self.assertEqual(f"{dut.Input('a',10)}", 'input [9:0] a')
        self.assertEqual(f"{dut.Input(10,'a')}", 'input [9:0] a')
        self.assertEqual(f"{dut.Input(10,name='a')}", 'input [9:0] a')

    def testOutput(self):
        self.assertEqual(f"{dut.Output('b')}", 'output b')
        self.assertEqual(f"{dut.Output(name='b')}", 'output b')
        self.assertEqual(f"{dut.Output('b',10)}", 'output [9:0] b')
        self.assertEqual(f"{dut.Output(10,'b')}", 'output [9:0] b')
        self.assertEqual(f"{dut.Output(10,name='b')}", 'output [9:0] b')


class DictObjConv(unittest.TestCase):
    
    def testObjToDict(self):
        class P:
            x=1
            y=2
        d = dut.objToDict(P)
        self.assertEqual(d['x'], P.x)
        self.assertEqual(d['y'], P.y)
        self.assertEqual(len(d), 2)

    def testDictToObj(self):
        d = {'x':1, 'y':2}
        P = dut.dictToObj(d)
        self.assertEqual(d['x'], P.x)
        self.assertEqual(d['y'], P.y)
        self.assertEqual(len(d), 2)


if __name__ == '__main__':
    unittest.main()
    
