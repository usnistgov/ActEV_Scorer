#!/usr/bin/env python2

import sys
import os

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

import unittest
from actev_kernel_components import *
from actev_kernel_components import _temporal_intersection, _temporal_union

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


class TestTemporalIntersection(TestActEVKernelComponents):
    def test_empty(self):
        self.assertEqual(_temporal_intersection(self.ae, self.ae), 0)

    def test_singlefile(self):
        self.assertEqual(_temporal_intersection(self.a1, self.a1), 10)
        self.assertEqual(_temporal_intersection(self.a1, self.a2), 5)
        self.assertEqual(_temporal_intersection(self.a2, self.a1), 5)
        self.assertEqual(_temporal_intersection(self.a1, self.a3), 0)

    def test_multifile(self):
        self.assertEqual(_temporal_intersection(self.a5, self.a6), 5)
        self.assertEqual(_temporal_intersection(self.a5, self.a7), 8)

        self.assertEqual(_temporal_intersection(self.a3, self.a4), 0)

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

class TestTemporalUnion(TestActEVKernelComponents):
    def test_singlefile(self):
        self.assertEqual(_temporal_union(self.a1, self.a1), 10)
        self.assertEqual(_temporal_union(self.a1, self.a2), 15)
        self.assertEqual(_temporal_union(self.a2, self.a1), 15)
        self.assertEqual(_temporal_union(self.a1, self.a3), 15)

    def test_multifile(self):
        self.assertEqual(_temporal_union(self.a5, self.a6), 45)
        self.assertEqual(_temporal_union(self.a5, self.a7), 25)

        self.assertEqual(_temporal_union(self.a3, self.a4), 15)

class TestTemporalIntersectionOverUnion(TestActEVKernelComponents):
    def test_empty(self):
        self.assertEqual(temporal_iou(self.ae, self.ae), 0.0)

    def test_singlefile(self):
        self.assertEqual(temporal_iou(self.a1, self.a1), float(10) / 10)
        self.assertEqual(temporal_iou(self.a1, self.a2), float(5) / 15)
        self.assertEqual(temporal_iou(self.a2, self.a1), float(5) / 15)
        self.assertEqual(temporal_iou(self.a1, self.a3), float(0) / 15)

    def test_multifile(self):
        self.assertEqual(temporal_iou(self.a5, self.a6), float(5) / 45)
        self.assertEqual(temporal_iou(self.a5, self.a7), float(8) / 25)

        self.assertEqual(temporal_iou(self.a3, self.a4), float(0) / 15)
        
if __name__ == '__main__':
    unittest.main()
