#!/usr/bin/env python3

import sys
import os
import json

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)

import unittest
from activities_edit import *

class Test_Data(unittest.TestCase):
    def check_data(self):
        with open('./data/test_4-0.json') as f:
            test_four_zero = json.load(f)
        output_four_zero = boundingbox_merge(test_four_zero)
        assert(output_four_zero == {'filesProcessed': ['VIRAT_S_000000.mp4'], 'activities': [{'activity': 'Closing', 'activityID': 1, 'localization': {'VIRAT_S_000000.mp4': {'3034': 1, '3062': 0}}, 'objects': [{'objectType': 'Other', 'objectID': 1, 'localization': {'VIRAT_S_000000.mp4': {'3034': {'boundingBox': {'h': 130, 'w': 170, 'x': 10, 'y': 30}}, '3062': {}}}}]}, {'activity': 'Entering', 'activityID': 2, 'localization': {'VIRAT_S_000000.mp4': {'3845': 1, '3897': 0}}, 'objects': [{'objectType': 'Other', 'objectID': 1, 'localization': {'VIRAT_S_000000.mp4': {'3845': {'boundingBox': {'h': 130, 'w': 170, 'x': 10, 'y': 30}}, '3897': {}}}}]}, {'activity': 'Entering', 'activityID': 3, 'localization': {'VIRAT_S_000000.mp4': {'6070': 1, '6099': 0}}, 'objects': [{'objectType': 'Other', 'objectID': 1, 'localization': {'VIRAT_S_000000.mp4': {'6070': {'boundingBox': {'h': 290, 'w': 140, 'x': 10, 'y': 30}}, '6099': {}}}}]}]})

        with open('./data/test_6-0.json') as f:
            test_six_zero = json.load(f)
        output_six_zero = boundingbox_merge(test_six_zero)
        assert(output_six_zero == {'filesProcessed': ['VIRAT_S_040103_03_000284_000425.mp4'], 'activities': [{'activity': 'Opening', 'activityID': 1, 'localization': {'VIRAT_S_040103_03_000284_000425.mp4': {'1557': 1, '1826': 0}}, 'objects': [{'localization': {'VIRAT_S_040103_03_000284_000425.mp4': {'1557': {'boundingBox': {'h': 57, 'w': 29, 'x': 282, 'y': 16}}, '1826': {}}}, 'objectID': 1, 'objectType': 'Other'}]}]})

        with open('./data/test_7-1.json') as f:
            test_seven_one = json.load(f)
        output_seven_one = boundingbox_merge(test_seven_one)
        assert(output_seven_one == {'filesProcessed': ['VIRAT_S_000000.mp4', 'VIRAT_S_999999.mp4'], 'activities': [{'activity': 'Closing', 'activityID': 1, 'localization': {'VIRAT_S_000000.mp4': {'3034': 1, '3062': 0}}, 'objects': [{'objectType': 'Other', 'objectID': 1, 'localization': {'VIRAT_S_000000.mp4': {'3034': {'boundingBox': {'h': 130, 'w': 170, 'x': 10, 'y': 30}}, '3062': {}}}}]}, {'activity': 'Entering', 'activityID': 2, 'localization': {'VIRAT_S_000000.mp4': {'3845': 1, '3897': 0}, 'VIRAT_S_999999.mp4': {'3840': 1, '3898': 0}}, 'objects': [{'objectType': 'Other', 'objectID': 1, 'localization': {'VIRAT_S_000000.mp4': {'3845': {'boundingBox': {'h': 130, 'w': 170, 'x': 10, 'y': 30}}, '3897': {}}, 'VIRAT_S_999999.mp4': {'3840': {'boundingBox': {'x': 10, 'y': 30, 'w': 50, 'h': 20}}, '3898': {}}}}]}, {'activity': 'Entering', 'activityID': 3, 'localization': {'VIRAT_S_000000.mp4': {'6070': 1, '6099': 0}}, 'objects': [{'objectType': 'Other', 'objectID': 1, 'localization': {'VIRAT_S_000000.mp4': {'6070': {'boundingBox': {'h': 290, 'w': 140, 'x': 10, 'y': 30}}, '6099': {}}}}]}, {'activity': 'Entering', 'activityID': 90, 'localization': {'VIRAT_S_999999.mp4': {'6070': 1, '6099': 0}}, 'objects': [{'objectType': 'Other', 'objectID': 1, 'localization': {'VIRAT_S_999999.mp4': {'6070': {'boundingBox': {'h': 290, 'w': 140, 'x': 10, 'y': 30}}, '6099': {}}}}]}]})

        with open('./data/test_8-0.json') as f:
            test_eight_zero = json.load(f)
        output_eight_zero = boundingbox_merge(test_eight_zero)
        assert(output_eight_zero == {'filesProcessed': ['VIRAT_S_000000.mp4'], 'activities': [{'activity': 'Closing', 'activityID': 1, 'localization': {'VIRAT_S_000000.mp4': {'44989': 1, '45013': 0}}, 'objects': [{'objectType': 'Other', 'objectID': 1, 'localization': {'VIRAT_S_000000.mp4': {'44989': {'boundingBox': {'h': 20, 'w': 50, 'x': 10, 'y': 30}}, '45013': {}}}}]}]})

