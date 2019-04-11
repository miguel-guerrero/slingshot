#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------
import sys
sys.path.append('..')
import g2p as dut
import unittest

class Generator(unittest.TestCase):

    def testGenerateBasic(self):
        module = dut.generate('trip_adder', {'WIDTH':16}, renderType='trip')
        exp = "Module(name='trip_adder_WIDTH16', IOs=[Input('a', 16), Input('b', 16), Output('sum', 17)], paramDict={'HAS_CIN': 0, 'WIDTH': 16}, instanceList=[], userResult=Result(area=16))"
        self.assertEqual(f"{module}", exp)


if __name__ == '__main__':
    unittest.main()
    
