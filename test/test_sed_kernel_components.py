#!/usr/bin/env python2

import sys
import os

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

import unittest
from sed_kernel_components import *

class TestSEDKernelComponents(unittest.TestCase):
    def setUp(self):
        self.r_1 = { "localization": { "beginFrame": 20, "endFrame": 30 } }
        
        self.s_1 = { "localization": { "beginFrame": 20, "endFrame": 30 } }
        self.s_2 = { "localization": { "beginFrame": 10, "endFrame": 22 } }
        self.s_3 = { "localization": { "beginFrame": 0, "endFrame": 0 } }

class TestTimeOverlapFilter(TestSEDKernelComponents):
    def setUp(self):
        super(TestTimeOverlapFilter, self).setUp()

        self.filter_dt10 = build_sed_time_overlap_filter(10)
        self.filter_dt0 = build_sed_time_overlap_filter(0)
        self.filter_dt30 = build_sed_time_overlap_filter(30)

    def test_filter_dt10(self):
        self.assertEqual(self.filter_dt10(self.r_1, self.s_1), True)
        self.assertEqual(self.filter_dt10(self.r_1, self.s_2), True)
        self.assertEqual(self.filter_dt10(self.r_1, self.s_3), False)

    def test_filter_dt0(self):
        self.assertEqual(self.filter_dt0(self.r_1, self.s_1), True)
        self.assertEqual(self.filter_dt0(self.r_1, self.s_2), False)
        self.assertEqual(self.filter_dt0(self.r_1, self.s_3), False)

    def test_filter_dt30(self):
        self.assertEqual(self.filter_dt30(self.r_1, self.s_1), True)
        self.assertEqual(self.filter_dt30(self.r_1, self.s_2), True)
        self.assertEqual(self.filter_dt30(self.r_1, self.s_3), True)

class TestTimeCongruence(TestSEDKernelComponents):
    def setUp(self):
        super(TestTimeCongruence, self).setUp()

        self.r_0 = { "localization": { "beginFrame": 20, "endFrame": 20 } }

    def test_time_congruence(self):
        self.assertAlmostEqual(sed_time_congruence(self.r_1, self.s_1), 1.0)
        self.assertAlmostEqual(sed_time_congruence(self.r_1, self.s_2), 0.2)

        self.assertAlmostEqual(sed_time_congruence(self.r_0, self.s_1), 0.0)
        self.assertAlmostEqual(sed_time_congruence(self.r_0, self.s_2), 0.0)

class TestDecscoreCongruence(TestSEDKernelComponents):
    def setUp(self):
        super(TestDecscoreCongruence, self).setUp()

        self.sys_1 = [ { "decisionScore": 0.4 },
                       { "decisionScore": 0.5 },
                       { "decisionScore": 0.8 },
                       { "decisionScore": 0.85 },
                       { "decisionScore": 0.95 } ]
        self.congruence_func_sys_1 = build_sed_decscore_congruence(self.sys_1)

        self.sys_2 = [ { "decisionScore": 0.4 } ]
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
