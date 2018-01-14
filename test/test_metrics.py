#!/usr/bin/env python2

import sys
import os

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

import unittest
from metrics import *
from sparse_signal import SparseSignal as S

# ActivityInstance stub class
class A():
    def __init__(self, dictionary):
        self.localization = dictionary

class TestMetrics(unittest.TestCase):
    def setUp(self):
        super(TestMetrics, self).setUp()

class TestPMiss(TestMetrics):
    def setUp(self):
        super(TestPMiss, self).setUp()

        self.c1 = [1, 2, 3, 4]
        self.m1 = [10, 11]

        self.m2 = []

    def testNoPredicate(self):
        self.assertEqual(p_miss(len(self.c1), len(self.m1), 0), float(2) / 6)
        self.assertEqual(p_miss(0, 0, 0), None)
        self.assertEqual(p_miss(len(self.c1), len(self.m2), 0), float(0) / 6)

class TestRFA(TestMetrics):
    def setUp(self):
        super(TestRFA, self).setUp()

    def testRFA(self):
        self.assertEqual(r_fa(0, 0, 0, 60), float(0) / 60)
        self.assertEqual(r_fa(0, 0, 2, 60), float(2) / 60)
        self.assertEqual(r_fa(0, 0, 5, 10), float(5) / 10)

class TestPMissAtRFA(TestMetrics):
    def setUp(self):
        super(TestPMissAtRFA, self).setUp()

        self.c1 = [1.0, 0.9, 0.6, 0.3, 0.2]
        self.m1 = [None, None]
        self.f1 = [0.8, 0.7, 0.5, 0.4]

        self.key_func_2 = lambda x: x["decisionScore"]
        self.c2 = [{ "decisionScore": 1.0 },
                   { "decisionScore": 0.9 },
                   { "decisionScore": 0.6 },
                   { "decisionScore": 0.3 },
                   { "decisionScore": 0.2 }]
        self.m2 = [None, None]
        self.f2 = [{ "decisionScore": 0.8 },
                   { "decisionScore": 0.7 },
                   { "decisionScore": 0.5 },
                   { "decisionScore": 0.4 }]

    def testRMissAtRFA(self):
        self.assertEqual(p_miss_at_r_fa(self.c1, self.m1, self.f1, 10, float(0) / 10), float(5) / 7)
        self.assertEqual(p_miss_at_r_fa(self.c1, self.m1, self.f1, 10, float(1) / 10), float(5) / 7)
        self.assertEqual(p_miss_at_r_fa(self.c1, self.m1, self.f1, 10, float(2) / 10), float(4) / 7)
        self.assertEqual(p_miss_at_r_fa(self.c1, self.m1, self.f1, 10, float(3) / 10), float(4) / 7)
        self.assertEqual(p_miss_at_r_fa(self.c1, self.m1, self.f1, 10, float(4) / 10), float(2) / 7)
        self.assertEqual(p_miss_at_r_fa(self.c1, self.m1, self.f1, 10, float(5) / 10), float(2) / 7)

    def testRMissAtRFAwKeyFun(self):
        self.assertEqual(p_miss_at_r_fa(self.c2, self.m2, self.f2, 10, float(0) / 10, self.key_func_2), float(5) / 7)
        self.assertEqual(p_miss_at_r_fa(self.c2, self.m2, self.f2, 10, float(1) / 10, self.key_func_2), float(5) / 7)
        self.assertEqual(p_miss_at_r_fa(self.c2, self.m2, self.f2, 10, float(2) / 10, self.key_func_2), float(4) / 7)
        self.assertEqual(p_miss_at_r_fa(self.c2, self.m2, self.f2, 10, float(3) / 10, self.key_func_2), float(4) / 7)
        self.assertEqual(p_miss_at_r_fa(self.c2, self.m2, self.f2, 10, float(4) / 10, self.key_func_2), float(2) / 7)
        self.assertEqual(p_miss_at_r_fa(self.c2, self.m2, self.f2, 10, float(5) / 10, self.key_func_2), float(2) / 7)

class TestMIDE(TestMetrics):
    def setUp(self):
        super(TestMIDE, self).setUp()

        self.cost_fn = lambda x: 1 * x
        
        self.r1 = S({5: 1, 15: 0})
        self.s1 = S({5: 1, 15: 0})
        
        self.s2 = S({2: 1, 10: 0})

        self.r3 = S({5: 1, 15: 0, 30: 1, 35: 0})
        self.s3 = S({10: 1, 15: 0, 40: 1, 50: 0})

    def testMIDE(self):
        self.assertEqual(mide(self.r1, self.s1, 2, self.cost_fn, self.cost_fn), 0)
        self.assertEqual(mide(self.r1, self.s2, 2, self.cost_fn, self.cost_fn), (3 + 1))
        self.assertEqual(mide(self.r1, self.s2, 5, self.cost_fn, self.cost_fn), 0)
        self.assertEqual(mide(self.r1, self.s2, 0, self.cost_fn, self.cost_fn), (5 + 3))

    def testMIDEMulti(self):
        self.assertEqual(mide(self.r3, self.s2, 0, self.cost_fn, self.cost_fn), (10 + 3))
        self.assertEqual(mide(self.r3, self.s2, 2, self.cost_fn, self.cost_fn), (4 + 1))

        self.assertEqual(mide(self.r3, self.s3, 2, self.cost_fn, self.cost_fn), (4 + 10))
        
class TestNMIDE(TestMIDE):
    def setUp(self):
        super(TestNMIDE, self).setUp()

        self.c1 = [(A({ "f1": self.r1 }), A({ "f1": self.s1 })),
                   (A({ "f1": self.r3 }), A({ "f1": self.s3 }))]

        self.cd = [(A({ "f1": self.r1, "f2": self.r1 }), A({ "f1": self.s1, "f2": self.s1 })),
                   (A({ "f1": self.r3, "f2": self.r3 }), A({ "f1": self.s3, "f2": self.s3 }))]

        self.c3 = [(A({ "f1": self.r1 }), A({ "f2": self.s1 })),
                   (A({ "f1": self.r3 }), A({ "f2": self.s3 }))]

        self.cost_0 = lambda x: 0 * x
        
    def testNMIDE(self):
        self.assertEqual(n_mide(self.c1, 2, self.cost_fn, self.cost_fn), float(0 + (4 + 10)) / len(self.c1))
        self.assertEqual(n_mide(self.c1, 0, self.cost_fn, self.cost_fn), float(0 + (10 + 10)) / len(self.c1))
        self.assertEqual(n_mide(self.c1, 2, self.cost_0, self.cost_fn), float(0 + (0 + 10)) / len(self.c1))
        self.assertEqual(n_mide(self.c1, 2, self.cost_fn, self.cost_0), float(0 + (4 + 0)) / len(self.c1))
        self.assertEqual(n_mide(self.c1, 2, self.cost_0, self.cost_0), 0.0)

        self.assertEqual(n_mide(self.cd, 2, self.cost_fn, self.cost_fn), float(0 + (8 + 20)) / len(self.cd))

        self.assertEqual(n_mide(self.c3, 2, self.cost_fn, self.cost_fn), float((6 + 10) + (7 + 15)) / len(self.c3))

class TestSignalMetrics(unittest.TestCase):
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

class TestTemporalIntersection(TestSignalMetrics):
    def test_empty(self):
        self.assertEqual(temporal_intersection(self.ae, self.ae), 0)

    def test_singlefile(self):
        self.assertEqual(temporal_intersection(self.a1, self.a1), 10)
        self.assertEqual(temporal_intersection(self.a1, self.a2), 5)
        self.assertEqual(temporal_intersection(self.a2, self.a1), 5)
        self.assertEqual(temporal_intersection(self.a1, self.a3), 0)

    def test_multifile(self):
        self.assertEqual(temporal_intersection(self.a5, self.a6), 5)
        self.assertEqual(temporal_intersection(self.a5, self.a7), 8)

        self.assertEqual(temporal_intersection(self.a3, self.a4), 0)

class TestTemporalUnion(TestSignalMetrics):
    def test_singlefile(self):
        self.assertEqual(temporal_union(self.a1, self.a1), 10)
        self.assertEqual(temporal_union(self.a1, self.a2), 15)
        self.assertEqual(temporal_union(self.a2, self.a1), 15)
        self.assertEqual(temporal_union(self.a1, self.a3), 15)

    def test_multifile(self):
        self.assertEqual(temporal_union(self.a5, self.a6), 45)
        self.assertEqual(temporal_union(self.a5, self.a7), 25)

        self.assertEqual(temporal_union(self.a3, self.a4), 15)

class TestTemporalIntersectionOverUnion(TestSignalMetrics):
    def test_empty(self):
        self.assertEqual(temporal_intersection_over_union(self.ae, self.ae), 0.0)

    def test_singlefile(self):
        self.assertEqual(temporal_intersection_over_union(self.a1, self.a1), float(10) / 10)
        self.assertEqual(temporal_intersection_over_union(self.a1, self.a2), float(5) / 15)
        self.assertEqual(temporal_intersection_over_union(self.a2, self.a1), float(5) / 15)
        self.assertEqual(temporal_intersection_over_union(self.a1, self.a3), float(0) / 15)

    def test_multifile(self):
        self.assertEqual(temporal_intersection_over_union(self.a5, self.a6), float(5) / 45)
        self.assertEqual(temporal_intersection_over_union(self.a5, self.a7), float(8) / 25)

        self.assertEqual(temporal_intersection_over_union(self.a3, self.a4), float(0) / 15)
        
if __name__ == '__main__':
    unittest.main()
