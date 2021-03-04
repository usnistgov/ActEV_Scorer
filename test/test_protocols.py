#!/usr/bin/env python3

import sys
import os
import unittest

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")
sys.path.append(lib_path)
from activity_instance import *

protocols_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib/protocols")
sys.path.append(protocols_path)
from actev_sdl_v2 import ActEV_SDL_V2


class TestProtocols(unittest.TestCase):
    def setUp(self):
        # several files with different framerates, durations and no-score regions
        self.file_index = {
            # basic ones
            "test_video-file_000.mp4": {
                "framerate": 30.0,
                "selected": {
                    "1": 1,
                    "9001": 0
                }
            },
            "test_video-file_001.mp4": {
                "framerate": 30.0,
                "selected": {
                    "1": 1,
                    "2001": 0
                }
            },
            "test_video-file_002.mp4": {
                "framerate": 30.0,
                "selected": {
                    "1": 1,
                    "5001": 0
                }
            },
            # 2 with no-score regions
            "test_video-file_003.mp4": {
                "framerate": 30.0,
                "selected": {
                    "1": 1,
                    "1001": 0,
                    "1800": 1,
                    "9002": 0
                }
            },
            "test_video-file_004.mp4": {
                "framerate": 30.0,
                "selected": {
                    "1": 1,
                    "2345": 0,
                    "3456": 1,
                    "4567": 0,
                    "5678": 1,
                    "6001": 0
                }
            },
            # framerates
            "test_video-file_005.mp4": {
                "framerate": 25.0,
                "selected": {
                    "1": 1,
                    "7001": 0
                }
            },
            "test_video-file_006.mp4": {
                "framerate": 29.0,
                "selected": {
                    "1": 1,
                    "9001": 0
                }
            },
            "test_video-file_007.mp4": {
                "framerate": 15.0,
                "selected": {
                    "1": 1,
                    "4501": 0
                }
            }
        }
        self.activity_index = { "test_activity_%03d" % i: {} for i in range(5) }

        self.fp = [ "test_video-file_%03d" % i for i in range(len(self.file_index)) ]
        self.reference = {
            'filesProcessed': self.fp
        }
        self.system = {
            'filesProcessed': self.fp
        }

    def assertCohortEqual(self, observed, expected):
        self.assertEqual(len(observed), len(expected))
        for i in range(len(observed)):
            rs, ss = observed[i]
            self.assertEqual(len(rs), expected[i][0])
            self.assertEqual(len(ss), expected[i][1])

rid, sid = 1, 1


def gen_inst(act, f, loc, pc=-1):
    iid = rid if pc == -1 else sid
    k = list(loc)[0]
    dic = {
        'activity': act,
        'activityID': iid,
        'localization': {
            f: {
                str(loc[0]): 1,
                str(loc[1]): 0
            }
        }
    }
    iid += 1
    if pc != -1:
        dic['presenceConf'] = pc
    return ActivityInstance(dic)


class TestActEVSDLV2(TestProtocols):
    def setUp(self):
        super().setUp()
        self.protocol = ActEV_SDL_V2({}, self.file_index, self.activity_index, "")

        # one file with several activity types
        self.ref1 = []
        self.ref1.append(gen_inst('test_activity_000', 'test_video-file_000', (10, 44)))
        self.ref1.append(gen_inst('test_activity_000', 'test_video-file_000', (100, 121)))
        self.ref1.append(gen_inst('test_activity_001', 'test_video-file_000', (120, 162)))
        self.ref1.append(gen_inst('test_activity_001', 'test_video-file_000', (150, 162)))
        self.ref1.append(gen_inst('test_activity_000', 'test_video-file_000', (280, 503)))
        self.ref1.append(gen_inst('test_activity_002', 'test_video-file_000', (301, 316)))
        self.ref1.append(gen_inst('test_activity_001', 'test_video-file_000', (457, 483)))
        self.ref1.append(gen_inst('test_activity_000', 'test_video-file_000', (501, 800)))
        self.ref1.append(gen_inst('test_activity_002', 'test_video-file_000', (1016, 1039)))

        self.sys1 = []
        self.sys1.append(gen_inst('test_activity_000', 'test_video-file_000', (10, 50), 0.7))
        self.sys1.append(gen_inst('test_activity_000', 'test_video-file_000', (14, 50), 0.75))
        self.sys1.append(gen_inst('test_activity_000', 'test_video-file_000', (20, 29), 0.65))
        self.sys1.append(gen_inst('test_activity_000', 'test_video-file_000', (140, 200), 0.8))
        self.sys1.append(gen_inst('test_activity_002', 'test_video-file_000', (310, 1050), 0.77))

        # several files, only one activity type
        self.ref2 = []
        self.ref2.append(gen_inst('test_activity_003', 'test_video-file_001', (333, 379)))
        self.ref2.append(gen_inst('test_activity_003', 'test_video-file_001', (404, 666)))
        self.ref2.append(gen_inst('test_activity_003', 'test_video-file_001', (1020, 1420)))
        self.ref2.append(gen_inst('test_activity_003', 'test_video-file_002', (555, 598)))
        self.ref2.append(gen_inst('test_activity_003', 'test_video-file_002', (909, 1224)))
        self.ref2.append(gen_inst('test_activity_003', 'test_video-file_002', (1009, 1234)))
        self.ref2.append(gen_inst('test_activity_003', 'test_video-file_003', (365, 443)))
        self.ref2.append(gen_inst('test_activity_003', 'test_video-file_003', (532, 621)))
        self.ref2.append(gen_inst('test_activity_003', 'test_video-file_003', (800, 824)))

        self.sys2 = []
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_001', (330, 333), 0.3))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_001', (333, 337), 0.7))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_001', (347, 388), 0.4))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_001', (367, 401), 0.99))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_001', (420, 666), 0.33))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_001', (400, 1000), 0.63))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_001', (650, 1200), 0.71))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_001', (1430, 1433), 0.2))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_002', (50, 100), 0.812))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_002', (500, 560), 0.654))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_002', (560, 700), 0.783))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_002', (899, 910), 0.82))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_002', (921, 1024), 0.817))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_002', (1226, 1300), 0.42))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_003', (300, 304), 0.8))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_003', (307, 310), 0.333))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_003', (399, 900), 0.55))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_003', (650, 700), 0.546))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_003', (1023, 1200), 0.1))
        self.sys2.append(gen_inst('test_activity_003', 'test_video-file_003', (1123, 1409), 0.2))

        # several files, several activity types
        self.ref3 = []
        self.ref3.append(gen_inst('test_activity_004', 'test_video-file_001', (333, 379)))
        self.ref3.append(gen_inst('test_activity_004', 'test_video-file_001', (404, 666)))
        self.ref3.append(gen_inst('test_activity_004', 'test_video-file_002', (1020, 1420)))
        self.ref3.append(gen_inst('test_activity_004', 'test_video-file_002', (555, 598)))
        self.ref3.append(gen_inst('test_activity_004', 'test_video-file_003', (909, 1224)))
        self.ref3.append(gen_inst('test_activity_004', 'test_video-file_003', (1009, 1234)))
        self.ref3.append(gen_inst('test_activity_004', 'test_video-file_004', (365, 443)))
        self.ref3.append(gen_inst('test_activity_004', 'test_video-file_004', (532, 621)))
        self.ref3.append(gen_inst('test_activity_004', 'test_video-file_004', (800, 824)))

        # all mixed
        self.ref4 = self.ref1.copy()
        self.ref4.extend(self.ref2)
        #self.ref4.extend(self.ref3)

        self.sys4 = self.sys1.copy()
        #self.sys4.extend(self.sys2)
        #self.sys4.extend(self.sys3)

    def test_cohort_gen(self):
        # test_001
        # Should fail because there are different activity types
        self.assertRaises(TypeError, self.protocol.default_cohort_gen(self.ref1, self.sys1))
        expected_cohort_001 = {
            'test_activity_000': [[1, 3], [1, 1], [2, 0]],
            'test_activity_001': [[3, 0]],
            'test_activity_002': [[2, 1]]
        }
        print('')
        for act in ["test_activity_%03d" % i for i in range(3)]:
            print(act)
            refs = [r for r in self.ref1 if r.activity == act]
            syss = [s for s in self.sys1 if s.activity == act]
            cohort = list(self.protocol.default_cohort_gen(refs, syss))
            self.assertCohortEqual(cohort, expected_cohort_001[act])

        # test_002
        # Should fail because there are different video files
        self.assertRaises(TypeError, self.protocol.default_cohort_gen(self.ref2, self.sys2))
        expected_cohort_002 = {
            'test_video-file_001': [[1, 4], [2, 4]],
            'test_video-file_002': [[1, 3], [2, 3]],
            'test_video-file_003': [[3, 6]]
        }
        for f in ["test_video-file_%03d" % i for i in [3]]:
            print(f)
            refs = [r for r in self.ref2 if r.localization.get(f, None)]
            syss = [s for s in self.sys2 if s.localization.get(f, None)]
            cohort = list(self.protocol.default_cohort_gen(refs, syss))
            self.assertCohortEqual(cohort, expected_cohort_002[f])

