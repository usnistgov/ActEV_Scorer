#!/usr/bin/env python3

import sys
import os

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

from munkres import Munkres, DISALLOWED

import unittest
from alignment import *

class TestAlignment(unittest.TestCase):
    pass

class TestBuildLinearCombinationKernel(TestAlignment):
    def setUp(self):
        super(TestBuildLinearCombinationKernel, self).setUp()

        def _filter_1(r_i, s_i):
            return (r_i > s_i, {})

        def _filter_2(r_i, s_i):
            return (r_i < 5, {})

        def _comp_1_func(r_i, s_i, cache):
            return { "summation": r_i + s_i }

        def _comp_2_func(r_i, s_i, cache):
            return { "multiplication": r_i * s_i }

        self.kernel_blank_1 = build_linear_combination_kernel([], [], {})
        self.kernel_blank_2 = build_linear_combination_kernel([], [], {}, 3)

        self.kernel_1 = build_linear_combination_kernel([_filter_1], [], {})
        self.kernel_2 = build_linear_combination_kernel([_filter_1, _filter_2], [], {})

        self.kernel_3 = build_linear_combination_kernel([], [_comp_1_func], { "summation": 3 })
        self.kernel_4 = build_linear_combination_kernel([], [_comp_1_func, _comp_2_func], { "summation": 3, "multiplication": 2 })

        self.kernel_5 = build_linear_combination_kernel([_filter_1, _filter_2], [_comp_1_func, _comp_2_func], { "summation": 3, "multiplication": 2 }, 3)

        def _caching_filter_1(r_i, s_i):
            total = r_i + s_i
            return (total, { "sum": total })

        def _caching_comp_1(r_i, s_i, cache):
            return { "summation": cache["sum"] }

        self.cache_kernel_1 = build_linear_combination_kernel([_caching_filter_1], [_caching_comp_1], { "summation": 1 }, 1)

    def test_blank_kernel(self):
        self.assertEqual(self.kernel_blank_1(3, 4), (1, {}))
        self.assertEqual(self.kernel_blank_1(0, 0), (1, {}))
        self.assertEqual(self.kernel_blank_2(3, 4), (3, {}))
        self.assertEqual(self.kernel_blank_2(0, 0), (3, {}))

    def test_filtering_kernels(self):
        self.assertEqual(self.kernel_1(3, 4), (DISALLOWED, {}))
        self.assertEqual(self.kernel_1(4, 3), (1, {}))

        self.assertEqual(self.kernel_2(4, 3), (1, {}))
        self.assertEqual(self.kernel_2(5, 3), (DISALLOWED, {}))

    def test_computing_kernels(self):
        self.assertEqual(self.kernel_3(0, 0), (1, { "summation": 0 }))
        self.assertEqual(self.kernel_3(3, 4), (22, { "summation": 7 }))
        self.assertEqual(self.kernel_3(2, 2), (13, { "summation": 4 }))

        self.assertEqual(self.kernel_4(0, 0), (1, { "summation": 0, "multiplication": 0 }))
        self.assertEqual(self.kernel_4(3, 4), (46, { "summation": 7, "multiplication": 12 }))
        self.assertEqual(self.kernel_4(2, 2), (21, { "summation": 4, "multiplication": 4 }))

    def test_combined_kernels(self):
        self.assertEqual(self.kernel_5(5, 3), (DISALLOWED, {}))

        self.assertEqual(self.kernel_5(4, 3), (48, { "summation": 7, "multiplication": 12 }))

    def test_caching_kernels(self):
        self.assertEqual(self.cache_kernel_1(3, 4), (8, { "summation": 7 }))
        self.assertEqual(self.cache_kernel_1(0, 2), (3, { "summation": 2 }))

class TestPerformAlignment(TestAlignment):
    def setUp(self):
        super(TestPerformAlignment, self).setUp()

        def _filter_1(r_i, s_i):
            return (r_i != 3, {})

        def _comp_1_func(r_i, s_i, cache):
            return { "multi": r_i * s_i }

        self.ref_instances_1 = [1, 2, 3, 4]
        self.sys_instances_1 = [2, 4, 8, 16]

        self.kernel_multi = build_linear_combination_kernel([_filter_1], [_comp_1_func], { "multi": 1 })

        # self.sim_matrix_1 = [[3, 5, D, 9],
        #                      [5, 9, D, 17],
        #                      [9, 17, D, 33],
        #                      [17, 33, D, 65]]

        self.corr_1 = [(1, 4, 5, { "multi": 4 }, None, None, None),
                       (2, 8, 17, { "multi": 16 }, None, None, None),
                       (4, 16, 65, { "multi": 64 }, None, None, None)]
        self.miss_1 = [(3, None, None, None, None,None, None)]
        self.fa_1 = [(None, 2, None, None,None, None, None)]

        def _filter_d(r_i, s_i):
            return (False, {})

        self.kernel_d = build_linear_combination_kernel([_filter_d], [_comp_1_func], { "multi": 1 })

        self.corr_d = []
        self.miss_d = [(1, None, None, None, None, None, None),
                       (2, None, None, None, None, None, None),
                       (3, None, None, None, None, None, None),
                       (4, None, None, None, None, None, None)]
        self.fa_d = [(None, 2, None, None, None, None, None),
                     (None, 4, None, None, None, None, None),
                     (None, 8, None, None, None, None, None),
                     (None, 16, None, None, None, None, None)]

        def _filter_2(r_i, s_i):
            return (not (r_i == 3 and s_i == 8), {})

        self.kernel_2 = build_linear_combination_kernel([_filter_2], [_comp_1_func], { "multi": 1 })

        # self.sim_matrix_2 = [[3, 5, 7, 9],
        #                      [5, 9, 13, 17],
        #                      [9, 17, D, 33],
        #                      [17, 33, 49, 65]]

        self.corr_2 = [(1, 2, 3, { "multi": 2 }, None, None, None),
                       (3, 4, 13, { "multi": 12 }, None, None, None),
                       (2, 8, 17, { "multi": 16 }, None, None, None),
                       (4, 16, 65, { "multi": 64 }, None, None, None)]
        self.miss_2 = []
        self.fa_2 = []

        self.sys_instances_empty = []
        self.ref_instances_empty = []

        def _filter_u(r_i, s_i):
            return (not ((r_i == 3 and s_i == 1) or (s_i > 1 and r_i < 3)), {})

        def _comp_u_func(r_i, s_i, cache):
            return { "add": r_i + s_i }

        self.ref_instances_u = [1, 2, 3]
        self.sys_instances_u = [1, 2, 3]

        self.kernel_u = build_linear_combination_kernel([_filter_u], [_comp_u_func], { "add": 1 })

        # self.sim_matrix_unsolvable = [[3, 4, D],
        #                               [D, D, 6],
        #                               [D, D, 7]]

        #self.corr_u = [(3, 3, 7, { "add": 6 }, None, None, None),
        #               (2, 1, 4, { "add": 3 },None, None, None)]
        self.corr_u = [(2, 1, 4, { "add": 3 }, None, None, None),
                       (3, 3, 7, { "add": 6 },None, None, None)]
        self.miss_u = [(1, None, None, None,None, None, None)]
        self.fa_u = [(None, 2, None, None,None, None, None)]

    def assertAlignment(self, observed, expected):
        obs_corr, obs_miss, obs_fa = observed
        exp_corr, exp_miss, exp_fa = expected
        self.assertEqual(obs_corr, exp_corr)
        self.assertEqual(obs_miss, exp_miss)
        self.assertEqual(obs_fa, exp_fa)

    def test_alignment(self):
        self.assertAlignment(perform_alignment(self.ref_instances_1, self.sys_instances_1, self.kernel_multi), (self.corr_1, self.miss_1, self.fa_1))

        self.assertAlignment(perform_alignment(self.ref_instances_1, self.sys_instances_1, self.kernel_2), (self.corr_2, self.miss_2, self.fa_2))

    def test_alignment_empty(self):
        self.assertAlignment(perform_alignment(self.ref_instances_1, self.sys_instances_1, self.kernel_d), (self.corr_d, self.miss_d, self.fa_d))

        self.assertAlignment(perform_alignment(self.ref_instances_1, self.sys_instances_empty, self.kernel_multi), (self.corr_d, self.miss_d, []))

        self.assertAlignment(perform_alignment(self.ref_instances_empty, self.sys_instances_1, self.kernel_multi), (self.corr_d, [], self.fa_d))

    def test_munkres_unsolvable(self):
        # If using DISALLOWED alone, the "munkres" library can't solve
        # a matrix with possible assignments less than max(M, N).  The
        # alignment function should cover this case
        observed = perform_alignment(self.ref_instances_u, self.sys_instances_u, self.kernel_u)
        expected = (self.corr_u, self.miss_u, self.fa_u)
        # print(str(observed[0][0]))
        # print(str(expected[0][0]))
        self.assertAlignment(observed, expected)

if __name__ == '__main__':
    unittest.main()
