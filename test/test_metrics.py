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
        self.assertAlmostEqual(p_miss(len(self.c1), len(self.m1), 0), float(2) / 6, places=10)
        self.assertAlmostEqual(p_miss(0, 0, 0), None, places=10)
        self.assertAlmostEqual(p_miss(len(self.c1), len(self.m2), 0), float(0) / 6, places=10)

class TestRFA(TestMetrics):
    def setUp(self):
        super(TestRFA, self).setUp()

    def testRFA(self):
        self.assertAlmostEqual(r_fa(0, 0, 0, 60), float(0) / 60, places=10)
        self.assertAlmostEqual(r_fa(0, 0, 2, 60), float(2) / 60, places=10)
        self.assertAlmostEqual(r_fa(0, 0, 5, 10), float(5) / 10, places=10)

class TestPMissAtRFA(TestMetrics):
    def setUp(self):
        super(TestPMissAtRFA, self).setUp()

        self.points_empty = []

        self.points_1 = [(1.0, 0.0, float(6) / 7),
                         (0.9, 0.0, float(5) / 7),
                         (0.8, 1.0, float(5) / 7),
                         (0.7, 2.0, float(5) / 7),
                         (0.6, 2.0, float(4) / 7),
                         (0.5, 3.0, float(4) / 7),
                         (0.3, 4.0, float(3) / 7),
                         (0.3, 4.0, float(3) / 7),
                         (0.2, 4.0, float(2) / 7)]

        self.points_2 = [(1.0, 1.0, float(6) / 6),
                         (0.9, 1.0, float(5) / 6),
                         (0.6, 2.0, float(5) / 6),
                         (0.5, 2.0, float(4) / 6),
                         (0.4, 3.0, float(4) / 6),
                         (0.3, 3.0, float(3) / 6)]

        self.points_3 = [(1.0, 0.0, float(5) / 6),
                         (0.9, 0.0, float(4) / 6),
                         (0.6, 1.0, float(4) / 6),
                         (0.5, 3.0, float(3) / 6),
                         (0.5, 3.0, float(3) / 6),
                         (0.5, 3.0, float(3) / 6)]

        self.points_4 = [(1.0, 0.0, float(5) / 6),
                         (0.9, 0.0, float(4) / 6)]


    def testRMissAtRFA(self):
        self.assertEqual(p_miss_at_r_fa(self.points_empty, 1), None)
        self.assertEqual(p_miss_at_r_fa(self.points_empty, 0), None)

        self.assertAlmostEqual(p_miss_at_r_fa(self.points_1, 0), float(5) / 7, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_1, 1), float(5) / 7, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_1, 1.5), float(5) / 7, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_1, 2), float(4) / 7, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_1, 2.5), float(4) / 7, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_1, 3), float(4) / 7, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_1, 3.5), float(3.5) / 7, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_1, 4), float(2) / 7, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_1, 5), float(2) / 7, places=10)

        self.assertAlmostEqual(p_miss_at_r_fa(self.points_2, 0), float(6) / 6, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_2, 2), float(4) / 6, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_2, 2.5), float(4) / 6, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_2, 3), float(3) / 6, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_2, 4), float(3) / 6, places=10)

        self.assertAlmostEqual(p_miss_at_r_fa(self.points_3, 0), float(4) / 6, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_3, 2), float(3.5) / 6, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_3, 2.5), float(3.25) / 6, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_3, 3), float(3) / 6, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_3, 4), float(3) / 6, places=10)

        self.assertAlmostEqual(p_miss_at_r_fa(self.points_4, 1), float(4) / 6, places=10)
        self.assertAlmostEqual(p_miss_at_r_fa(self.points_4, 2), float(4) / 6, places=10)

class TestNMIDE(TestMetrics):
    def setUp(self):
        super(TestNMIDE, self).setUp()

        self.cost_fn = lambda x: 1 * x

        self.r1 = S({5: 1, 15: 0})
        self.s1 = S({5: 1, 15: 0})

        self.s2 = S({2: 1, 10: 0})

        self.r3 = S({5: 1, 15: 0, 30: 1, 35: 0})
        self.s3 = S({10: 1, 15: 0, 40: 1, 50: 0})

        self.r4 = S({30: 1, 35: 0})

        self.c1 = [(A({ "f1": self.r1 }), A({ "f1": self.s1 })),
                   (A({ "f1": self.r3 }), A({ "f1": self.s3 }))]

        self.cd = [(A({ "f1": self.r1, "f2": self.r1 }), A({ "f1": self.s1, "f2": self.s1 })),
                   (A({ "f1": self.r3, "f2": self.r3 }), A({ "f1": self.s3, "f2": self.s3 }))]

        self.c3 = [(A({ "f1": self.r1 }), A({ "f2": self.s1 })),
                   (A({ "f1": self.r3 }), A({ "f2": self.s3 }))]

        self.c4 = [(A({ "f1": self.r1 }), A({ "f1": self.s2 })),
                   (A({ "f1": self.r4 }), A({ "f1": self.s3 }))]

        self.filedur_1 = { "f1": 80, "f2": 100 }

        # Testing 0 FA denominator
        self.filedur_2 = { "f1": 15 }

        self.cost_0 = lambda x: 0 * x

    def testNMIDE(self):
        self.assertAlmostEqual(n_mide(self.c1, self.filedur_1, 2, self.cost_fn, self.cost_fn), float(0 + (4 / float(7) + 10 / float(57))) / len(self.c1), places=10)
        self.assertAlmostEqual(n_mide(self.c1, self.filedur_1, 0, self.cost_fn, self.cost_fn), float(0 + (10 / float(15) + 10 / float(65))) / len(self.c1), places=10)
        self.assertAlmostEqual(n_mide(self.c1, self.filedur_1, 2, self.cost_0, self.cost_fn), float(0 + (0 + 10 / float(57))) / len(self.c1), places=10)
        self.assertAlmostEqual(n_mide(self.c1, self.filedur_1, 2, self.cost_fn, self.cost_0), float(0 + (4 / float(7) + 0)) / len(self.c1), places=10)
        self.assertAlmostEqual(n_mide(self.c1, self.filedur_1, 2, self.cost_0, self.cost_0), 0.0, places=10)

        # n_mide should ignore pair with 0 false-alarm denominator
        self.assertAlmostEqual(n_mide(self.c1, self.filedur_2, 0, self.cost_fn, self.cost_fn), float(0), places=10)

        self.assertAlmostEqual(n_mide(self.cd, self.filedur_1, 2, self.cost_fn, self.cost_fn), float(0 + (8 / float(14) + 20 / float(57 + 77))) / len(self.cd), places=10)

        self.assertAlmostEqual(n_mide(self.c3, self.filedur_1, 2, self.cost_fn, self.cost_fn), float((6 / float(6) + 10 / float(100 + 66)) + (7 / float(7) + 15 / float(100 + 57))) / len(self.c3), places=10)

        self.assertAlmostEqual(n_mide(self.c4, self.filedur_1, 3, self.cost_fn, self.cost_fn), float((2 / float(4)) + 0) / 1, places=10)

        self.assertEqual(n_mide(self.c3, self.filedur_1, 10, self.cost_fn, self.cost_fn), None)

    def testNMIDE_count_rejected(self):
        self.assertEqual(n_mide_count_rejected(self.c3, self.filedur_1, 2), 0)
        self.assertEqual(n_mide_count_rejected(self.cd, self.filedur_1, 2), 0)
        self.assertEqual(n_mide_count_rejected(self.c3, self.filedur_1, 10), 2)
        self.assertEqual(n_mide_count_rejected(self.cd, self.filedur_1, 10), 2)
        self.assertEqual(n_mide_count_rejected(self.c4, self.filedur_1, 0), 0)
        self.assertEqual(n_mide_count_rejected(self.c4, self.filedur_1, 3), 1)
        self.assertEqual(n_mide_count_rejected(self.c4, self.filedur_1, 10), 2)

        # n_mide should ignore pair with 0 false-alarm denominator
        self.assertEqual(n_mide_count_rejected(self.c1, self.filedur_2, 0), 1)

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
        self.assertAlmostEqual(temporal_intersection_over_union(self.a1, self.a1), float(10) / 10, places=10)
        self.assertAlmostEqual(temporal_intersection_over_union(self.a1, self.a2), float(5) / 15, places=10)
        self.assertAlmostEqual(temporal_intersection_over_union(self.a2, self.a1), float(5) / 15, places=10)
        self.assertAlmostEqual(temporal_intersection_over_union(self.a1, self.a3), float(0) / 15, places=10)

    def test_multifile(self):
        self.assertAlmostEqual(temporal_intersection_over_union(self.a5, self.a6), float(5) / 45, places=10)
        self.assertAlmostEqual(temporal_intersection_over_union(self.a5, self.a7), float(8) / 25, places=10)

        self.assertAlmostEqual(temporal_intersection_over_union(self.a3, self.a4), float(0) / 15, places=10)

class TestTemporalMiss(TestSignalMetrics):
    def test_empty(self):
        self.assertEqual(temporal_miss(self.ae, self.ae), 0)

    def test_singlefile(self):
        self.assertEqual(temporal_miss(self.a1, self.a1), 0)
        self.assertEqual(temporal_miss(self.a1, self.a2), 5)
        self.assertEqual(temporal_miss(self.a2, self.a1), 5)
        self.assertEqual(temporal_miss(self.a1, self.a3), 10)

    def test_multifile(self):
        self.assertEqual(temporal_miss(self.a5, self.a6), (5 + 10))
        self.assertEqual(temporal_miss(self.a5, self.a7), (5 + 7))

        self.assertEqual(temporal_miss(self.a3, self.a4), 5)

class TestTemporalFA(TestSignalMetrics):
    def test_empty(self):
        self.assertEqual(temporal_fa(self.ae, self.ae), 0)

    def test_singlefile(self):
        self.assertEqual(temporal_fa(self.a1, self.a1), 0)
        self.assertEqual(temporal_fa(self.a1, self.a2), 5)
        self.assertEqual(temporal_fa(self.a2, self.a1), 5)
        self.assertEqual(temporal_fa(self.a1, self.a3), 5)

    def test_multifile(self):
        self.assertEqual(temporal_fa(self.a5, self.a6), (5 + 20))
        self.assertEqual(temporal_fa(self.a5, self.a7), (5 + 0))

        self.assertEqual(temporal_fa(self.a3, self.a4), 10)

class TestMeanExcludeNone(TestMetrics):
    def test(self):
        self.assertAlmostEqual(mean_exclude_none([1, 2, 3]), 2.0, places=10)
        self.assertAlmostEqual(mean_exclude_none([1, 2, 3, None]), 2.0, places=10)
        self.assertAlmostEqual(mean_exclude_none([1, 2, 3, None, None]), 2.0, places=10)

# ObjectLocalizationFrame stub class
class O():
    def __init__(self, signal):
        self.spatial_signal = signal

class TestSpatialSignalMetrics(unittest.TestCase):
    def setUp(self):
        self.ae = A({})

        self.a1 = A({ "f1": O(S({ 10: S({10: 1, 20: 0}), 15: S()})) })
        self.a2 = A({ "f1": O(S({ 10: S({15: 1, 25: 0}), 35: S()})) })
        self.a3 = A({ "f1": O(S({ 30: S({15: 1, 35: 0}), 40: S()})) })

        self.a4 = A({ "f1": O(S({ 10: S({10: 1, 20: 0}), 15: S()})),
                      "f2": O(S({ 30: S({15: 1, 35: 0}), 40: S()}))})
        self.a5 = A({ "f1": O(S({ 10: S({15: 1, 25: 0}), 35: S()})),
                      "f2": O(S({ 10: S({15: 1, 25: 0}), 35: S()}))})

class TestSpatialIntersection(TestSpatialSignalMetrics):
    def test_empty(self):
        self.assertEqual(spatial_intersection(self.ae, self.ae), 0)

    def test_singlefile(self):
        self.assertEqual(spatial_intersection(self.a1, self.a1), 50)
        self.assertEqual(spatial_intersection(self.a1, self.a2), 25)
        self.assertEqual(spatial_intersection(self.a2, self.a1), 25)
        self.assertEqual(spatial_intersection(self.a1, self.a3), 0)

    def test_multifile(self):
        self.assertEqual(spatial_intersection(self.a4, self.a5), 75)
        self.assertEqual(spatial_intersection(self.a5, self.a4), 75)

        self.assertEqual(spatial_intersection(self.a2, self.a4), 25)
        self.assertEqual(spatial_intersection(self.a3, self.a4), 0)

class TestSpatialUnion(TestSpatialSignalMetrics):
    def test_empty(self):
        self.assertEqual(spatial_union(self.ae, self.ae), 0)

    def test_singlefile(self):
        self.assertEqual(spatial_union(self.a1, self.a1), 50)
        self.assertEqual(spatial_union(self.a1, self.a2), 275)
        self.assertEqual(spatial_union(self.a2, self.a1), 275)
        self.assertEqual(spatial_union(self.a1, self.a3), 250)

    def test_multifile(self):
        self.assertEqual(spatial_union(self.a4, self.a5), 275 + 400)
        self.assertEqual(spatial_union(self.a5, self.a4), 275 + 400)

        self.assertEqual(spatial_union(self.a2, self.a4), 275 + 200)
        self.assertEqual(spatial_union(self.a3, self.a4), 250 + 200)

class TestSpatialIntersectionOverUnion(TestSpatialSignalMetrics):
    def test_empty(self):
        self.assertEqual(spatial_intersection_over_union(self.ae, self.ae), 0.0)

    def test_singlefile(self):
        self.assertEqual(spatial_intersection_over_union(self.a1, self.a1), 1.0)
        self.assertEqual(spatial_intersection_over_union(self.a1, self.a2), float(25) / 275)
        self.assertEqual(spatial_intersection_over_union(self.a2, self.a1), float(25) / 275)
        self.assertEqual(spatial_intersection_over_union(self.a1, self.a3), float(0) / 250)

    def test_multifile(self):
        self.assertEqual(spatial_intersection_over_union(self.a4, self.a5), float(75) / (275 + 400))
        self.assertEqual(spatial_intersection_over_union(self.a5, self.a4), float(75) / (275 + 400))

        self.assertEqual(spatial_intersection_over_union(self.a2, self.a4), float(25) / (275 + 200))
        self.assertEqual(spatial_intersection_over_union(self.a3, self.a4), float(0) / (250 + 200))

class TestMODE(TestMetrics):
    def setUp(self):
        super(TestMODE, self).setUp()

        self.c_1 = 6
        self.c_2 = 0

        self.f_1 = 28
        self.f_2 = 18

        self.m_1 = 26
        self.m_2 = 32

        self.wf_1 = lambda x: x * 1
        self.wf_2 = lambda x: x * 2

    def test_mode(self):
        self.assertAlmostEqual(mode(self.c_1, self.m_1, self.f_1, self.wf_1, self.wf_1), float(54) / 32, places = 10)
        self.assertAlmostEqual(mode(self.c_1, self.m_1, self.f_2, self.wf_1, self.wf_1), float(44) / 32, places = 10)
        self.assertAlmostEqual(mode(self.c_2, self.m_2, self.f_2, self.wf_1, self.wf_1), float(50) / 32, places = 10)

        self.assertAlmostEqual(mode(self.c_1, self.m_1, self.f_1, self.wf_1, self.wf_2), float(26 + 2 * 28) / 32, places = 10)
        self.assertAlmostEqual(mode(self.c_1, self.m_1, self.f_1, self.wf_2, self.wf_2), float(2 * 26 + 2 * 28) / 32, places = 10)

if __name__ == '__main__':
    unittest.main()
