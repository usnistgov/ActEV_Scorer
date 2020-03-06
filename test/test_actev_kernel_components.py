#!/usr/bin/env python2

import sys
import os
import json

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

import unittest
from actev_kernel_components import *
from sed_kernel_components import *
from activity_instance import *
from alignment import *

# ActivityInstance stub class
class A():
    def __init__(self, dictionary):
        self.localization = dictionary

# ObjectInstance stub class
class O():
    def __init__(self, obj_type):
        self.objectType = obj_type

# ObjectLocalizationFrame stub class
class OLF():
    def __init__(self, signal):
        self.spatial_signal = signal

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

        self.temporal_delta = 0.2
        self.temporal_overlap_filter = build_temporal_overlap_filter(self.temporal_delta)

        self.s_ae = A({})

        self.s_a1 = A({ "f1": OLF(S({ 10: S({10: 1, 20: 0}), 15: S()})) })
        self.s_a2 = A({ "f1": OLF(S({ 10: S({15: 1, 25: 0}), 35: S()})) })
        self.s_a3 = A({ "f1": OLF(S({ 30: S({15: 1, 35: 0}), 40: S()})) })

        self.s_a4 = A({ "f1": OLF(S({ 10: S({10: 1, 20: 0}), 15: S()})),
                        "f2": OLF(S({ 30: S({15: 1, 35: 0}), 40: S()}))})
        self.s_a5 = A({ "f1": OLF(S({ 10: S({15: 1, 25: 0}), 35: S()})),
                        "f2": OLF(S({ 10: S({15: 1, 25: 0}), 35: S()}))})

        self.spatial_delta_1 = 0.5
        self.spatial_delta_2 = 0.1
        self.spatial_overlap_filter_1 = build_spatial_overlap_filter(self.spatial_delta_1)
        self.spatial_overlap_filter_2 = build_spatial_overlap_filter(self.spatial_delta_2)

        self.o_1 = O("person")
        self.o_2 = O("person")
        self.o_3 = O("vehicle")
        self.o_4 = O("Vehicle")

        self.o_5 = O("construction_vehicle")

        self.obj_classes_1 = { "person": "person",
                               "vehicle": "vehicle" }

        self.obj_classes_2 = { "person": "person",
                               "vehicle": "vehicle",
                               "construction_vehicle": "vehicle" }

        self.obj_classes_3 = { "person": "*object*",
                               "vehicle": "*object*",
                               "construction_vehicle": "*object*" }

        self.obj_ec_filter_1 = build_equiv_class_type_match_filter(self.obj_classes_1)
        self.obj_ec_filter_2 = build_equiv_class_type_match_filter(self.obj_classes_2)
        self.obj_ec_filter_3 = build_equiv_class_type_match_filter(self.obj_classes_3)

    def assert_filter(self, obs, exp):
        obs_b, obs_d = obs
        exp_b, exp_d = exp
        self.assertEqual(obs_b, exp_b)
        for k in obs_d.keys() | exp_d.keys():
            self.assertAlmostEqual(obs_d[k], exp_d[k], places=10)

class TestTemporalIntersectionFilter(TestActEVKernelComponents):
    def test_empty(self):
        self.assertEqual(temporal_intersection_filter(self.ae, self.ae), (False, { "temporal_intersection": 0 }))

    def test_singlefile(self):
        self.assertEqual(temporal_intersection_filter(self.a1, self.a1), (True, { "temporal_intersection": 10 }))
        self.assertEqual(temporal_intersection_filter(self.a1, self.a2), (True, { "temporal_intersection": 5 }))
        self.assertEqual(temporal_intersection_filter(self.a2, self.a1), (True, { "temporal_intersection": 5 }))
        self.assertEqual(temporal_intersection_filter(self.a1, self.a3), (False, { "temporal_intersection": 0 }))

    def test_multifile(self):
        self.assertEqual(temporal_intersection_filter(self.a5, self.a6), (True, { "temporal_intersection": 5 }))
        self.assertEqual(temporal_intersection_filter(self.a5, self.a7), (True, { "temporal_intersection": 8 }))

        self.assertEqual(temporal_intersection_filter(self.a3, self.a4), (False, { "temporal_intersection": 0 }))

class TestTemporalOverlapFilter(TestActEVKernelComponents):
    def test_empty(self):
        self.assert_filter(self.temporal_overlap_filter(self.ae, self.ae), (False, { "temporal_intersection-over-union": 0.0 }))

    def test_singlefile(self):
        self.assert_filter(self.temporal_overlap_filter(self.a1, self.a1), (True, { "temporal_intersection-over-union": float(10) / 10 }))
        self.assertEqual(self.temporal_overlap_filter(self.a1, self.a2), (True, { "temporal_intersection-over-union": float(5) / 15 }))
        self.assertEqual(self.temporal_overlap_filter(self.a2, self.a1), (True, { "temporal_intersection-over-union": float(5) / 15 }))
        self.assertEqual(self.temporal_overlap_filter(self.a1, self.a3), (False, { "temporal_intersection-over-union": float(0) / 15 }))

    def test_multifile(self):
        self.assert_filter(self.temporal_overlap_filter(self.a5, self.a6), (False, { "temporal_intersection-over-union": float(5) / 45 }))
        self.assert_filter(self.temporal_overlap_filter(self.a5, self.a7), (True, { "temporal_intersection-over-union": float(8) / 25 }))

        self.assert_filter(self.temporal_overlap_filter(self.a3, self.a4), (False, { "temporal_intersection-over-union": float(0) / 15 }))

class TestSpatialOverlapFilter(TestActEVKernelComponents):
    def test_empty(self):
        self.assert_filter(self.spatial_overlap_filter_1(self.s_ae, self.s_ae), (False, { "spatial_intersection-over-union": 0.0 }))

        self.assert_filter(self.spatial_overlap_filter_2(self.s_ae, self.s_ae), (False, { "spatial_intersection-over-union": 0.0 }))

    def test_singlefile(self):
        self.assert_filter(self.spatial_overlap_filter_1(self.s_a1, self.s_a1), (True, { "spatial_intersection-over-union": 1.0 }))
        self.assert_filter(self.spatial_overlap_filter_1(self.s_a1, self.s_a2), (False, { "spatial_intersection-over-union": float(25) / 275 }))
        self.assert_filter(self.spatial_overlap_filter_1(self.s_a2, self.s_a1), (False, { "spatial_intersection-over-union": float(25) / 275 }))
        self.assert_filter(self.spatial_overlap_filter_1(self.s_a1, self.s_a3), (False, { "spatial_intersection-over-union": float(0) / 275 }))

        self.assert_filter(self.spatial_overlap_filter_2(self.s_a1, self.s_a1), (True, { "spatial_intersection-over-union": 1.0 }))
        self.assert_filter(self.spatial_overlap_filter_2(self.s_a1, self.s_a2), (False, { "spatial_intersection-over-union": float(25) / 275 }))
        self.assert_filter(self.spatial_overlap_filter_2(self.s_a2, self.s_a1), (False, { "spatial_intersection-over-union": float(25) / 275 }))
        self.assert_filter(self.spatial_overlap_filter_2(self.s_a1, self.s_a3), (False, { "spatial_intersection-over-union": float(0) / 275 }))

    def test_multifile(self):
        self.assert_filter(self.spatial_overlap_filter_1(self.s_a4, self.s_a5), (False, { "spatial_intersection-over-union": float(75) / (275 + 400) }))
        self.assert_filter(self.spatial_overlap_filter_1(self.s_a5, self.s_a4), (False, { "spatial_intersection-over-union": float(75) / (275 + 400) }))

        self.assert_filter(self.spatial_overlap_filter_1(self.s_a2, self.s_a4), (False, { "spatial_intersection-over-union": float(25) / (275 + 200) }))
        self.assert_filter(self.spatial_overlap_filter_1(self.s_a3, self.s_a4), (False, { "spatial_intersection-over-union": float(0) / (250 + 200) }))

        self.assert_filter(self.spatial_overlap_filter_2(self.s_a4, self.s_a5), (True, { "spatial_intersection-over-union": float(75) / (275 + 400) }))
        self.assert_filter(self.spatial_overlap_filter_2(self.s_a5, self.s_a4), (True, { "spatial_intersection-over-union": float(75) / (275 + 400) }))

        self.assert_filter(self.spatial_overlap_filter_2(self.s_a2, self.s_a4), (False, { "spatial_intersection-over-union": float(25) / (275 + 200) }))
        self.assert_filter(self.spatial_overlap_filter_2(self.s_a3, self.s_a4), (False, { "spatial_intersection-over-union": float(0) / (250 + 200) }))

class TestObjectTypeFilter(TestActEVKernelComponents):
    def test_filter(self):
        self.assertEqual(object_type_match_filter(self.o_1, self.o_1), (True, {}))
        self.assertEqual(object_type_match_filter(self.o_1, self.o_2), (True, {}))
        self.assertEqual(object_type_match_filter(self.o_2, self.o_1), (True, {}))

        self.assertEqual(object_type_match_filter(self.o_1, self.o_3), (False, {}))
        self.assertEqual(object_type_match_filter(self.o_1, self.o_4), (False, {}))

        self.assertEqual(object_type_match_filter(self.o_3, self.o_4), (False, {}))
        self.assertEqual(object_type_match_filter(self.o_4, self.o_3), (False, {}))

class TestEquivClassObjectTypeFilter(TestActEVKernelComponents):
    def test_filter(self):
        self.assertEqual(self.obj_ec_filter_1(self.o_1, self.o_1), (True, {}))
        self.assertEqual(self.obj_ec_filter_1(self.o_1, self.o_2), (True, {}))
        self.assertEqual(self.obj_ec_filter_1(self.o_2, self.o_1), (True, {}))
        self.assertEqual(self.obj_ec_filter_1(self.o_1, self.o_3), (False, {}))
        self.assertEqual(self.obj_ec_filter_1(self.o_3, self.o_4), (False, {}))

        self.assertEqual(self.obj_ec_filter_2(self.o_3, self.o_5), (True, {}))
        self.assertEqual(self.obj_ec_filter_2(self.o_1, self.o_3), (False, {}))

        self.assertEqual(self.obj_ec_filter_3(self.o_3, self.o_5), (True, {}))
        self.assertEqual(self.obj_ec_filter_3(self.o_1, self.o_5), (True, {}))
        self.assertEqual(self.obj_ec_filter_3(self.o_1, self.o_3), (True, {}))

class TestObjectCongruence(TestActEVKernelComponents):
    def setUp(self):
        super(TestObjectCongruence, self).setUp()

        self.sai_1 = ActivityInstance(json.loads("""
        {
          "activity": "Closing",
          "activityID": 1,
          "presenceConf": 0.77,
          "localization": {
            "VIRAT_S_000000.mp4": {
              "3024": 1,
              "3040": 0,
              "3052": 1,
              "3070": 0
            }
          },
          "objects": [
            {
              "objectType": "person",
              "objectID": 1,
              "localization": {
                "VIRAT_S_000000.mp4": {
                  "3034": {
                    "presenceConf": 0.45,
                    "boundingBox": {
                      "x": 10,
                      "y": 30,
                      "w": 50,
                      "h": 20
                    }
                  },
                  "3052": {
                    "presenceConf": 0.67,
                    "boundingBox": {
                      "x": 80,
                      "y": 10,
                      "w": 50,
                      "h": 20
                    }
                  },
                  "3070": {
                  }
                }
              }
            },
            {
              "objectType": "vehicle",
              "objectID": 2,
              "localization": {
                "VIRAT_S_000000.mp4": {
                  "3030": {
                    "presenceConf": 0.20,
                    "boundingBox": {
                      "x": 10,
                      "y": 30,
                      "w": 50,
                      "h": 20
                    }
                  },
                  "3041": {
                  }
                }
              }
            }
          ]
        }"""), True)

        self.sai_2 = ActivityInstance(json.loads("""
        {
          "activity": "Closing",
          "activityID": 1,
          "presenceConf": 0.77,
          "localization": {
            "VIRAT_S_000000.mp4": {
              "3034": 1,
              "3062": 0
            }
          },
          "objects": [
            {
              "objectType": "person",
              "objectID": 1,
              "localization": {
                "VIRAT_S_000000.mp4": {
                  "3034": {
                    "presenceConf": 0.45,
                    "boundingBox": {
                      "x": 10,
                      "y": 30,
                      "w": 50,
                      "h": 20
                    }
                  },
                  "3052": {
                    "presenceConf": 0.67,
                    "boundingBox": {
                      "x": 80,
                      "y": 10,
                      "w": 50,
                      "h": 20
                    }
                  },
                  "3062": {
                  }
                }
              }
            }
          ]
        }"""), True)

        self.rai_1 = ActivityInstance(json.loads("""
        {
          "activity": "Closing",
          "activityID": 1,
          "localization": {
            "VIRAT_S_000000.mp4": {
              "3030": 1,
              "3062": 0
            }
          },
          "objects": [
            {
              "objectType": "person",
              "objectID": 1,
              "localization": {
                "VIRAT_S_000000.mp4": {
                  "3030": {
                    "boundingBox": {
                      "x": 10,
                      "y": 30,
                      "w": 50,
                      "h": 20
                    }
                  },
                  "3062": {
                  }
                }
              }
            }
          ]
        }"""), True)

        def _obj_kernel_builder(sys):
            return build_linear_combination_kernel([object_type_match_filter,
                                                    build_simple_spatial_overlap_filter(0.5)],
                                                   [simple_spatial_intersection_over_union_component,
                                                    build_sed_presenceconf_congruence(sys)],
                                                   {"spatial_intersection-over-union": 10e-8,
                                                    "presence-conf-congruence": 10e-6 })

        self.obj_kernel_builder = _obj_kernel_builder

    def assert_mode_scores(self, observed, expected):
        for o, e in zip(*map(sorted, [observed, expected])):
            o_conf, o_mode = o
            e_conf, e_mode = e
            self.assertEqual(o_conf, e_conf)
            self.assertAlmostEqual(o_mode, e_mode, places=10)

    def test_object_congruence_intersection(self):
        intersect_object_congruence_1 = build_object_congruence(self.obj_kernel_builder, intersection_filter, intersection_filter)(self.rai_1, self.sai_1, {})
        self.assertAlmostEqual(intersect_object_congruence_1["minMODE"], 1.2, places=10)
        self.assert_mode_scores(intersect_object_congruence_1["MODE_records"], [(0.2, 1.7), (0.45, 1.2), (0.67, 1.5)])
        self.assertAlmostEqual(intersect_object_congruence_1["object-p_miss@0.5rfa"], 0.7, places=10)
        self.assertAlmostEqual(intersect_object_congruence_1["object-p_miss@0.2rfa"], 1.0, places=10)
        self.assertAlmostEqual(intersect_object_congruence_1["object-p_miss@0.1rfa"], 1.0, places=10)
        self.assertAlmostEqual(intersect_object_congruence_1["object-p_miss@0.033rfa"], 1.0, places=10)

        intersect_object_congruence_2 = build_object_congruence(self.obj_kernel_builder, intersection_filter, intersection_filter)(self.rai_1, self.sai_2, {})
        self.assertAlmostEqual(intersect_object_congruence_2["minMODE"], float(20) / 28, places=10)
        self.assert_mode_scores(intersect_object_congruence_2["MODE_records"], [(0.45, float(20) / 28), (0.67, float(38) / 28)])
        self.assertAlmostEqual(intersect_object_congruence_2["object-p_miss@0.5rfa"], float(10) / 28, places=10)
        self.assertAlmostEqual(intersect_object_congruence_2["object-p_miss@0.2rfa"], 1.0, places=10)
        self.assertAlmostEqual(intersect_object_congruence_2["object-p_miss@0.1rfa"], 1.0, places=10)
        self.assertAlmostEqual(intersect_object_congruence_2["object-p_miss@0.033rfa"], 1.0, places=10)

    def test_object_congruence_intersection_wobjecttypes(self):
        intersect_object_congruence_1 = build_object_congruence(self.obj_kernel_builder, intersection_filter, intersection_filter, ["person"])(self.rai_1, self.sai_1, {})
        self.assertAlmostEqual(intersect_object_congruence_1["minMODE"], 1.2, places=10)
        self.assert_mode_scores(intersect_object_congruence_1["MODE_records"], [(0.45, 1.2), (0.67, 1.5)])
        self.assertAlmostEqual(intersect_object_congruence_1["object-p_miss@0.5rfa"], 0.7, places=10)
        self.assertAlmostEqual(intersect_object_congruence_1["object-p_miss@0.2rfa"], 1.0, places=10)
        self.assertAlmostEqual(intersect_object_congruence_1["object-p_miss@0.1rfa"], 1.0, places=10)
        self.assertAlmostEqual(intersect_object_congruence_1["object-p_miss@0.033rfa"], 1.0, places=10)

    def test_object_congruence_passthrough(self):
        object_congruence_1 = build_object_congruence(self.obj_kernel_builder, ref_passthrough_filter, sys_passthrough_filter)(self.rai_1, self.sai_1, {})
        self.assertAlmostEqual(object_congruence_1["minMODE"], 1.375, places=10)
        self.assert_mode_scores(object_congruence_1["MODE_records"], [(0.2, 1.6875), (0.45, 1.375), (0.67, 1.5625)])
        self.assertAlmostEqual(object_congruence_1["object-p_miss@0.5rfa"], 1.0, places=10)
        self.assertAlmostEqual(object_congruence_1["object-p_miss@0.2rfa"], 1.0, places=10)
        self.assertAlmostEqual(object_congruence_1["object-p_miss@0.1rfa"], 1.0, places=10)
        self.assertAlmostEqual(object_congruence_1["object-p_miss@0.033rfa"], 1.0, places=10)

        object_congruence_2 = build_object_congruence(self.obj_kernel_builder, ref_passthrough_filter, sys_passthrough_filter)(self.rai_1, self.sai_2, {})
        self.assertAlmostEqual(object_congruence_2["minMODE"], 0.75, places=10)
        self.assert_mode_scores(object_congruence_2["MODE_records"], [(0.45, 0.75), (0.67, 1.3125)])
        self.assertAlmostEqual(object_congruence_2["object-p_miss@0.5rfa"], float(14) / 32, places=10)
        self.assertAlmostEqual(object_congruence_2["object-p_miss@0.2rfa"], 1.0, places=10)
        self.assertAlmostEqual(object_congruence_2["object-p_miss@0.1rfa"], 1.0, places=10)
        self.assertAlmostEqual(object_congruence_2["object-p_miss@0.033rfa"], 1.0, places=10)


if __name__ == '__main__':
    unittest.main()
