#!/usr/bin/env python3

import sys
import os
from functools import reduce

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

import unittest
from operator import add, sub
from sparse_signal import SparseSignal as S

class TestSparseSignal(unittest.TestCase):
    def setUp(self):
        super(TestSparseSignal, self).setUp()

        self.se = S()
        self.s1 = S({30: 1, 60: 0})
        self.s2 = S({0: 1, 10: 0})
        self.s3 = S({30: 1, 40: 0})
        self.s4 = S({60: 1, 80: 0})
        self.s5 = S({0: 1, 30: 0})
        self.s6 = S({60: 1, 100: 0})
        self.s7 = S({0: 1, 100: 0})

        self.sb1 = S({0: 1, 30: 2, 60: 1, 100: 0})
        self.sb2 = S({30: 2, 40: 1, 60: 0})
        self.sb3 = S({30: 1, 60: 2, 100: 1, 130: 0})

        self.ss1 = S({0: 1, 30: 0, 60: 1, 100: 0})

        self.si1 = S({45: 1, 100: 0})

        self.sd1 = S({10: 1, 20: 0})
        self.sd2 = S({10.45: 1, 20: 0})
        self.sd3 = S({10.00: 1, 20.85: 0})
        self.sd4 = S({10.90: 1, 20.35: 0})
        self.sd5 = S({0.12: 1, 30.32: 0, 30.7: 1, 100.2: 0})
        self.sd6 = S({0.12: 1, 30.32: 2, 60.7: 1, 100.2: 0})

        self.sn1 = S({0: 1, 10: 1, 20: 0})

        self.sc1 = S({5: 1, 10: 0})
        self.sc2 = S({5: 1, 7:1, 10: 0})
        self.sc3 = S({0: 1, 10: 0})

        self.s2d_1 = S({10: S({10: 1, 20: 0}), 15: S(), 30: S({15: 1, 35: 0}), 40: S()})
        self.s2d_2 = S({10: S({15: 1, 25: 0}), 35: S()})

        self.s3d_1 = S({1: S({10: S({10: 1, 20: 0}), 20: S()}), 2: S({10: S({10: 1, 30: 0}), 30: S()}), 4: S()})
        self.s3d_2 = S({1: S({10: S({10: 1, 20: 0}), 20: S()}), 4: S()})

        self.s_iter1 = S({3: 1, 5: 2, 10: 0})

        self.s_iter2 = S({3: 1, 5: 0, 7: 1, 10: 0})

    def testSignalEquivalence(self):
        self.assertEqual(self.se, self.se)
        self.assertEqual(self.s1, self.s1)
        self.assertEqual(S({30: 1, 60: 0}), self.s1)

    def testSignalAdditionEmpty(self):
        self.assertEqual(self.se + self.se, self.se)
        self.assertEqual(self.s1 + self.se, self.s1)
        self.assertEqual(self.se + self.s1, self.s1)

    def testSignalAdditionPass2(self):
        self.assertEqual(self.s1 + self.s2, S({0: 1, 10: 0, 30: 1, 60: 0}))
        self.assertEqual(self.s1 + self.s3, S({30: 2, 40: 1, 60: 0}))
        self.assertEqual(self.s1 + self.s4, S({30: 1, 80: 0}))

    def testSignalAdditionPass3(self):
        self.assertEqual(self.s1 + self.s5, S({0: 1, 60: 0}))
        self.assertEqual(self.s1 + self.s1, S({30: 2, 60: 0}))
        self.assertEqual(self.s1 + self.s6, S({30: 1, 100: 0}))
        self.assertEqual(self.s1 + self.s7, S({0: 1, 30: 2, 60: 1, 100: 0}))

    def testSignalMultiAdd(self):
        self.assertEqual(reduce(add, [self.s1, self.s1, self.s1]), S({30: 3, 60: 0}))
        self.assertEqual(reduce(add, [self.s1, self.s2, self.s3]), S({0: 1, 10: 0, 30: 2, 40: 1, 60: 0}))

    def testIntersection(self):
        self.assertEqual(self.s1 & self.se, self.se)
        self.assertEqual(self.s1 & self.s1, self.s1)
        self.assertEqual(self.s1 & self.s2, self.se)
        self.assertEqual(self.s1 & self.s3, self.s3)
        self.assertEqual(self.s3 & self.s1, self.s3)
        self.assertEqual(self.s1 & self.sb1, self.s1)
        self.assertEqual(self.s1 & self.si1, S({45: 1, 60: 0}))

    def testSubtraction(self):
        self.assertEqual(self.s1 - self.se, self.s1)
        self.assertEqual(self.se - self.s1, self.se)
        self.assertEqual(self.s1 - self.si1, S({30: 1, 45: 0}))
        self.assertEqual(self.si1 - self.s1, S({60: 1, 100: 0}))
        self.assertEqual(self.sb1 - self.s1, S({0: 1, 100: 0}))
        self.assertEqual(self.sb1 - self.sb3, S({0: 1, 60: 0}))
        self.assertEqual(self.sb3 - self.sb1, S({60: 1, 130: 0}))
        self.assertEqual(self.sb1 - self.se, self.sb1)

    def testArea(self):
        self.assertEqual(self.se.area(), 0)
        self.assertEqual(self.s1.area(), 30)
        self.assertEqual(self.s2.area(), 10)
        self.assertEqual(self.sb1.area(), 130)

    def testNormalize(self):
        self.assertEqual(self.sn1.normalize(), S({0: 1, 20: 0}))

    def testGenerateCollar(self):
        self.assertEqual(self.sc1.generate_collar(2), S({3: 1, 7: 0, 8: 1, 12: 0}))

        # Input signal should be normalized in the generate_collar
        # function
        self.assertEqual(self.sc2.generate_collar(2), S({3: 1, 7: 0, 8: 1, 12: 0}))

        self.assertEqual(self.sc3.generate_collar(2), S({-2: 1, 2: 0, 8: 1, 12: 0}))

        # Output signal should be normalized
        self.assertEqual(self.sc1.generate_collar(5), S({0: 1, 15: 0}))

    def test2D(self):
        self.assertEqual(self.s2d_1.area(), 250)
        self.assertEqual(self.s2d_2.area(), 250)

        self.assertEqual(self.s2d_1.join(self.s2d_1.join(self.s2d_1, lambda a, b: a.join(b, min, 0), S()), lambda a, b: a.join(b, sub, 0), S()), S())

        self.assertEqual(self.s2d_1.join(self.s2d_2, lambda a, b: a.join(b, min, 0), S()), S({10: S({15: 1, 20: 0}), 15: S(), 30: S({15: 1, 25: 0}), 35: S()}))
        self.assertEqual(self.s2d_1.join_nd(self.s2d_2, 2, min), S({10: S({15: 1, 20: 0}), 15: S(), 30: S({15: 1, 25: 0}), 35: S()}))

        self.assertEqual(self.s2d_1.join_nd(S(), 2, max), self.s2d_1)

        self.assertEqual(self.s2d_1.join_nd(self.s2d_2, 2, lambda a, b: a - min(a, b)), S({10: S({10: 1, 15: 0}), 15: S(), 30: S({25: 1, 35: 0}), 35: S({15: 1, 35: 0}), 40: S()}))
        self.assertEqual(self.s2d_1.join_nd(self.s2d_2, 2, lambda a, b: a - min(a, b)).area(), 175)

        self.assertEqual(self.s2d_1.join_nd(self.s2d_2, 2, max), S({10: S({10: 1, 25: 0}), 15: S({15: 1, 25: 0}), 30: S({15: 1, 35: 0}), 40: S()}))
        self.assertEqual(self.s2d_1.join_nd(self.s2d_2, 2, max).area(), 425)

    def test3D(self):
        self.assertEqual(self.s3d_1.area(), 900)
        self.assertEqual(self.s3d_2.area(), 300)

        self.assertEqual(self.s3d_1.join_nd(self.s3d_1, 3, lambda a, b: a - min(a, b)).area(), 0)
        self.assertEqual(self.s3d_2.join_nd(self.s3d_1, 3, lambda a, b: a - min(a, b)).area(), 0)

        self.assertEqual(self.s3d_1.join_nd(self.s3d_2, 3, lambda a, b: a - min(a, b)).area(), 600)
        self.assertEqual(self.s3d_1.join_nd(self.s3d_2, 3, max).area(), 900)

    def testIterateByFrame(self):
        self.assertEqual([ x for x in self.s_iter1.iterate_by_frame(1, 1) ], [ (1, 0) ])
        self.assertEqual([ x for x in self.s_iter1.iterate_by_frame(1, 5) ], [ (1, 0), (2, 0), (3, 1), (4, 1), (5, 2) ])
        self.assertEqual([ x for x in self.s_iter1.iterate_by_frame(1, 11) ], [ (1, 0), (2, 0), (3, 1), (4, 1), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 0), (11, 0) ])
        self.assertEqual([ x for x in self.s_iter1.iterate_by_frame(1, 11, -1) ], [ (1, -1), (2, -1), (3, 1), (4, 1), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 0), (11, 0) ])

        with self.assertRaises(ValueError):
            [ x for x in self.s_iter1.iterate_by_frame(1, 0) ]

    def testOnSteps(self):
        self.assertEqual([ x for x in self.s_iter1.on_steps(lambda x: x == 1) ], [ (3, 1), (4, 1) ])
        self.assertEqual([ x for x in self.s_iter1.on_steps(lambda x: x == 2) ], [ (5, 2), (6, 2), (7, 2), (8, 2), (9, 2) ])

        self.assertEqual([ x for x in self.s_iter2.on_steps(lambda x: x == 1) ], [ (3, 1), (4, 1), (7, 1), (8, 1), (9, 1) ])

if __name__ == '__main__':
    unittest.main()
