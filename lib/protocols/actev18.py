import sys
import os

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
sys.path.append(lib_path)

from metrics import *
from actev_kernel_components import *
from sed_kernel_components import *
from alignment import *

class ActEV18():
    def __init__(self, **kwargs):
        self.target_rfa = kwargs.get("target_rfa", 10)
        total_file_dur_minutes = kwargs.get("total_file_duration_minutes")
        
        self.instance_pair_metrics = { "temporal_intersection": temporal_intersection,
                                       "temporal_union": temporal_union }
        self.default_reported_instance_pair_metrics = [ "temporal_intersection",
                                                        "temporal_union" ]

        self.default_reported_kernel_components = [ "temporal_intersection-over-union" ]            

        self.alignment_metrics = { "rate_fa": self._build_rfa(total_file_dur_minutes),
                                   "p_miss": lambda c, m, f: p_miss(len(c), len(m), len(f)),
                                   "p_miss@10rfa": self._build_pmiss_at_rfa(total_file_dur_minutes, self.target_rfa) }
        self.default_reported_alignment_metrics = [ "rate_fa",
                                                    "p_miss",
                                                    "p_miss@10rfa" ]

    def build_kernel(self, system_instances):
        return build_linear_combination_kernel([temporal_intersection_filter],
                                               [("temporal_intersection-over-union", 1.0e-8, temporal_intersection_over_union),
                                                ("decscore_congruence", 1.0e-6, build_sed_decscore_congruence(system_instances))])

    def _build_pmiss_at_rfa(self, file_duration, target_rfa):
        def _metric_func(c, m, f):
            return p_miss_at_r_fa(c, m, f, file_duration, target_rfa, lambda x: x.decisionScore)

        return _metric_func

    def _build_rfa(self, file_duration):
        def _metric_func(c, m, f):
            return r_fa(len(c), len(m), len(f), file_duration)

        return _metric_func

    def __str__(self):
        return "target_rfa: {}".format(self.target_rfa)
