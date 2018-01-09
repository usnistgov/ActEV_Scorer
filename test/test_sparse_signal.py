#!/usr/bin/env python2

import sys
import os

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

import unittest
from operator import add
from sparse_signal import SparseSignal as S

class TestSparseSignal(unittest.TestCase):
    def setUp(self):
        super(TestSparseSignal, self).setUp()

        self.se = S({})
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
        
if __name__ == '__main__':
    unittest.main()
