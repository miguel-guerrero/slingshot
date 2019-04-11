#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append('..')
import g2p as dut
import unittest

class Generator(unittest.TestCase):

    def exp(self, name):
        ios="Input('a', 16), Input('b', 16), Output('sum', 17)"
        return  "Module(name='" + name + "', IOs=[Input('a0', 8), Input('b0', 8), Output('sum0', 9), Input('a1', 8), Input('b1', 8), Output('sum1', 9), Input('a2', 8), Input('b2', 8), Output('sum2', 9), Input('a3', 8), Input('b3', 8), Output('sum3', 9), Input('a4', 8), Input('b4', 8), Output('sum4', 9), Input('a5', 8), Input('b5', 8), Output('sum5', 9), Input('a6', 8), Input('b6', 8), Output('sum6', 9), Input('a7', 8), Input('b7', 8), Output('sum7', 9), Input('a8', 8), Input('b8', 8), Output('sum8', 9), Input('a9', 8), Input('b9', 8), Output('sum9', 9)], paramDict={'CNT': 10, 'HAS_CIN': 0, 'WIDTH': 8}, instanceList=[Instance(module=Module(name='adder_WIDTH16', IOs=["+ios+"], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16)), insName='adder_0'), Instance(module=Module(name='adder_WIDTH16', IOs=["+ios+"], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16)), insName='adder_1'), Instance(module=Module(name='adder_WIDTH16', IOs=["+ios+"], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16)), insName='adder_2'), Instance(module=Module(name='adder_WIDTH16', IOs=["+ios+"], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16)), insName='adder_3'), Instance(module=Module(name='adder_WIDTH16', IOs=["+ios+"], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16)), insName='adder_4'), Instance(module=Module(name='adder_WIDTH16', IOs=["+ios+"], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16)), insName='adder_5'), Instance(module=Module(name='adder_WIDTH16', IOs=["+ios+"], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16)), insName='adder_6'), Instance(module=Module(name='adder_WIDTH16', IOs=["+ios+"], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16)), insName='adder_7'), Instance(module=Module(name='adder_WIDTH16', IOs=["+ios+"], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16)), insName='adder_8'), Instance(module=Module(name='adder_WIDTH16', IOs=["+ios+"], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16)), insName='adder_9')])"


    def testGenerateBasic(self):
        module = dut.generate('adder', {'WIDTH':16})
        exp = "Module(name='adder_WIDTH16', IOs=[Input('a', 16), Input('b', 16), Output('sum', 17)], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16))"
        self.assertEqual(f"{module}", exp)

    def testGenerateBasic2(self):
        module = dut.generate('adder2', {'WIDTH':16})
        exp = "Module(name='adder2_WIDTH16', IOs=[Input('a', 16), Input('b', 16), Output('sum', 17)], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[])"
        self.assertEqual(f"{module}", exp)

    def testGenerateHier(self):
        self.maxDiff = None
        module = dut.generate('multi_adder', {'WIDTH':8, 'CNT':10})
        self.assertEqual(f"{module}", self.exp("multi_adder_CNT10_WIDTH8"))
        
    def testGenerateHier2(self):
        self.maxDiff = None
        module = dut.generate('multi_adder2', {'WIDTH':8, 'CNT':10})
        self.assertEqual(f"{module}", self.exp("multi_adder2_CNT10_WIDTH8"))

    def testGenerateHier3(self):
        self.maxDiff = None
        module = dut.generate('multi_adder3', {'WIDTH':8, 'CNT':10})
        self.assertEqual(f"{module}", self.exp("multi_adder3_CNT10_WIDTH8"))

if __name__ == '__main__':
    unittest.main()
    
