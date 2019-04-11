#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# (c) 2018 Miguel A. Guerrero all rights reserved
#-------------------------------------------------------------------------------

import sys
sys.path.append('..')
import g2p as g
import unittest

class Generator(unittest.TestCase):

    def testGenerateBasic(self):
        module = g.generate('adder', {'WIDTH':16})
        self.assertEqual(module.name, 'adder_WIDTH16')

    def testGenerateHier2(self):
        module = g.generate('multi_adder2', {'WIDTH':8, 'CNT':10})
        self.assertEqual(module.name, "multi_adder2_CNT10_WIDTH8")

    def testGenerateHier3(self):
        module = g.generate('multi_adder3', {'WIDTH':8, 'CNT':10})
        self.assertEqual(module.name, "multi_adder3_CNT10_WIDTH8")
        for i, ins in enumerate(module.getInstances()):
            self.assertEqual(f'{ins.insName}', f'adder_{i}')
            self.assertEqual(ins.module.targetPath, 'build/adder_WIDTH16.v')
            self.assertEqual(ins.module.paramDict['WIDTH'], 16)
            self.assertEqual(ins.module.paramDict['HAS_CIN'], 0)
            self.assertEqual(len(ins.module.IOs), 3)

if __name__ == '__main__':
    unittest.main()
    
