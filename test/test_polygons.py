#!/usr/bin/env python3

import os
import sys
import unittest

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

from polygons import *


class TestPolygons(unittest.TestCase):
    pass


class TestCentroid(TestPolygons):
    def testCentroid(self):
        self.assertEqual(centroid({'x': 0, 'y': 0, 'w': 30, 'h': 30}), (15, 15))
        self.assertEqual(centroid({'x': 0, 'y': 0, 'w': 31, 'h': 31}), (15.5, 15.5))
        self.assertEqual(centroid({'x': 30, 'y': 30, 'w': 31, 'h': 31}), (45.5, 45.5))


class TestSegment(TestPolygons):
    def setUp(self):
        self.p = (0, 0)
        self.q = (0, 20)
        self.r = (20, 20)
        self.s = (20, 0)
        self.a = (10, 10)
        self.b = (0, 10)
        self.c = (10, 0)

    def testSegmentTrue(self):
        self.assertTrue(segment(self.p, self.a, self.r))
        self.assertTrue(segment(self.p, self.b, self.q))
        self.assertTrue(segment(self.p, self.c, self.s))
        self.assertTrue(segment(self.r, self.a, self.p))

    def testSegmentFalse(self):
        self.assertFalse(segment(self.p, self.r, self.a))
        self.assertFalse(segment(self.a, self.p, self.r))
        self.assertFalse(segment(self.b, self.p, self.q))
        self.assertFalse(segment(self.p, self.q, self.b))
        self.assertFalse(segment(self.c, self.p, self.s))
        self.assertFalse(segment(self.p, self.s, self.c))
        self.assertFalse(segment(self.a, self.r, self.p))
        self.assertFalse(segment(self.r, self.p, self.a))


class TestOrientation(TestPolygons):
    def setUp(self):
        self.p = (10, 10)
        self.q = (20, 20)
        self.r = (30, 30)
        self.s = (10, 20)

    def testOrientation(self):
        self.assertEqual(0, orientation(self.p, self.q, self.r))
        self.assertEqual(1, orientation(self.p, self.s, self.q))
        self.assertEqual(2, orientation(self.p, self.q, self.s))


class TestIntersect(TestPolygons):
    def setUp(self):
        self.p1 = (10, 10)
        self.p2 = (20, 10)
        self.q1 = (20, 20)
        self.q2 = (10, 20)

    def testIntersect(self):
        self.assertTrue(intersect(self.p1, self.q1, self.p2, self.q2))
        self.assertFalse(intersect(self.p1, self.p2, self.q1, self.q2))
        self.assertTrue(intersect(self.p1, self.q1, self.p1, self.q1))


class TestInterList(TestPolygons):
    def setUp(self):
        self.a = a = [0, 10, 1500, 3000]
        self.b = ['1000', '1800', '2000']

    def testInterList(self):
        self.assertEqual(inter_list(self.a, self.b), ['1000', '1500', '1800', '2000'])


class TestDNA(TestPolygons):
    def setUp(self):
        self.obj0 = {
            "objectID": 1,
            "objectType": "person",
            "localization": {
                "test.avi": {
                    "0": {
                        "boundingBox": {
                            "x": 40,
                            "y": 40,
                            "h": 20,
                            "w": 20
                        }, "presenceConf": 1.0
                    }, "3000": {}
                }
            }
        }
        self.obj1 = {
            "objectID": 2,
            "objectType": "person",
            "localization": {
                "test.avi": {
                    "0": {
                        "boundingBox": {
                            "x": 50,
                            "y": 50,
                            "h": 20,
                            "w": 20
                        }, "presenceConf": 1.0
                    }, "1000": {
                        "boundingBox": {
                            "x": 15,
                            "y": 15,
                            "h": 20,
                            "w": 20
                        }, "presenceConf": 1.0
                    },  "1300": {
                        "boundingBox": {
                            "x": 50,
                            "y": 50,
                            "h": 20,
                            "w": 20
                        }, "presenceConf": 1.0
                    }, "3000": {}
                }
            }
        }
        self.dna0 = DNA('test.avi', (1000, 2000), ['act001'], [(20, 20), (20, 40), (40, 40), (40, 20)])
        self.dna1 = DNA('test.avi', (1000, 2000), ['act001'], [(20, 20), (20, 60), (60, 60), (60, 20)])
        self.dna2 = DNA('test.avi', (1000, 2000), ['act001'], [(20, 20), (20, 40), (40, 40), (40, 20)], thd="80p")
        self.dna3 = DNA('test.avi', (1000, 2000), ['act001'], [(20, 20), (20, 40), (40, 40), (40, 20)], thd="50p")
        self.dna4 = DNA('test.avi', (1000, 2000), ['act001'], [(20, 20), (20, 40), (40, 40), (40, 20)], thd="500f")
        self.dna5 = DNA('test.avi', (1000, 2000), ['act001'], [(20, 20), (20, 40), (40, 40), (40, 20)], thd="300")

    def testBasic(self):
        self.assertFalse(self.dna0.contains(self.obj0))
        self.assertTrue(self.dna1.contains(self.obj0))

    def testPercentageThreshold(self):
        self.assertFalse(self.dna2.contains(self.obj1))
        self.assertTrue(self.dna3.contains(self.obj1))

    def testFrameThreshold(self):
        self.assertFalse(self.dna4.contains(self.obj1))
        self.assertTrue(self.dna5.contains(self.obj1))
