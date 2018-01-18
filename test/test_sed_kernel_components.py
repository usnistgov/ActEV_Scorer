#!/usr/bin/env python2

import sys
import os

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

import unittest
from sed_kernel_components import *

# ActivityInstance stub class
class A():
    def __init__(self, decScore):
        self.decisionScore = decScore

class TestSEDKernelComponents(unittest.TestCase):
    def setUp(self):
        self.sys_1 = [ A(0.4),
                       A(0.5),
                       A(0.8),
                       A(0.85),
                       A(0.95) ]
        self.congruence_func_sys_1 = build_sed_decscore_congruence(self.sys_1)

        self.sys_2 = [ A(0.4) ]
        self.congruence_func_sys_2 = build_sed_decscore_congruence(self.sys_2)

        self.sys_empty = [ ]

    def test_decscore_congruence(self):
        self.assertAlmostEqual(self.congruence_func_sys_1(None, self.sys_1[0]), 0.0)
        self.assertAlmostEqual(self.congruence_func_sys_1(None, self.sys_1[1]), 0.1 / 0.55)
        self.assertAlmostEqual(self.congruence_func_sys_1(None, self.sys_1[2]), 0.4 / 0.55)
        self.assertAlmostEqual(self.congruence_func_sys_1(None, self.sys_1[3]), 0.45 / 0.55)
        self.assertAlmostEqual(self.congruence_func_sys_1(None, self.sys_1[4]), 1.0)

    def test_decscore_congruence_single_instance(self):
        self.assertAlmostEqual(self.congruence_func_sys_2(None, self.sys_2[0]), 1.0)

    def test_decscore_congruence_empty(self):
        # This shouldn't raise an exception, if it does, our test case
        # fails
        build_sed_decscore_congruence(self.sys_empty)
        
if __name__ == '__main__':
    unittest.main()
