#!/usr/bin/env python2

import sys
import os

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

import unittest
from actev_kernel_components import *

# ActivityInstance stub class
class A():
    def __init__(self, dictionary):
        self.localization = dictionary

class TestActEVKernelComponents(unittest.TestCase):
    def setUp(self):
        self.ae = A({})
        
        self.a1 = A({ "f1": { 10: 1, 20: 0 } })
        self.a2 = A({ "f1": { 15: 1, 25: 0 } })
        self.a3 = A({ "f1": { 25: 1, 30: 0 } })
        
        self.a4 = A({ "f2": { 30: 1, 40: 0 } })

        self.a5 = A({ "f1": { 10: 1, 20: 0 },
                      "f2": { 30: 1, 40: 0 } })
        self.a6 = A({ "f1": { 15: 1, 25: 0 },
                      "f2": { 50: 1, 70: 0 } })
        self.a7 = A({ "f1": { 15: 1, 25: 0 },
                      "f2": { 32: 1, 35: 0 } })

class TestTemporalIntersectionFilter(TestActEVKernelComponents):
    def test_empty(self):
        self.assertEqual(temporal_intersection_filter(self.ae, self.ae), False)

    def test_singlefile(self):
        self.assertEqual(temporal_intersection_filter(self.a1, self.a1), True)
        self.assertEqual(temporal_intersection_filter(self.a1, self.a2), True)
        self.assertEqual(temporal_intersection_filter(self.a2, self.a1), True)
        self.assertEqual(temporal_intersection_filter(self.a1, self.a3), False)

    def test_multifile(self):
        self.assertEqual(temporal_intersection_filter(self.a5, self.a6), True)
        self.assertEqual(temporal_intersection_filter(self.a5, self.a7), True)

        self.assertEqual(temporal_intersection_filter(self.a3, self.a4), False)
        
if __name__ == '__main__':
    unittest.main()
