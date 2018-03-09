# actev18.py
# Author(s): David Joy

# This software was developed by employees of the National Institute of
# Standards and Technology (NIST), an agency of the Federal
# Government. Pursuant to title 17 United States Code Section 105, works
# of NIST employees are not subject to copyright protection in the
# United States and are considered to be in the public
# domain. Permission to freely use, copy, modify, and distribute this
# software and its documentation without fee is hereby granted, provided
# that this notice and disclaimer of warranty appears in all copies.

# THE SOFTWARE IS PROVIDED 'AS IS' WITHOUT ANY WARRANTY OF ANY KIND,
# EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED
# TO, ANY WARRANTY THAT THE SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, AND FREEDOM FROM INFRINGEMENT, AND ANY WARRANTY THAT THE
# DOCUMENTATION WILL CONFORM TO THE SOFTWARE, OR ANY WARRANTY THAT THE
# SOFTWARE WILL BE ERROR FREE. IN NO EVENT SHALL NIST BE LIABLE FOR ANY
# DAMAGES, INCLUDING, BUT NOT LIMITED TO, DIRECT, INDIRECT, SPECIAL OR
# CONSEQUENTIAL DAMAGES, ARISING OUT OF, RESULTING FROM, OR IN ANY WAY
# CONNECTED WITH THIS SOFTWARE, WHETHER OR NOT BASED UPON WARRANTY,
# CONTRACT, TORT, OR OTHERWISE, WHETHER OR NOT INJURY WAS SUSTAINED BY
# PERSONS OR PROPERTY OR OTHERWISE, AND WHETHER OR NOT LOSS WAS
# SUSTAINED FROM, OR AROSE OUT OF THE RESULTS OF, OR USE OF, THE
# SOFTWARE OR SERVICES PROVIDED HEREUNDER.

# Distributions of NIST software should also include copyright and
# licensing statements of any third-party software that are legally
# bundled with the code in compliance with the conditions of those
# licenses.

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
        total_file_dur_minutes = kwargs.get("total_file_duration_minutes")
        file_framedur_lookup = kwargs.get("file_framedur_lookup")

        self.schema_fn = "actev18_schema.json"
        
        self.epsilon_temporal_congruence = 1.0e-8
        self.epsilon_decisionscore_congruence = 1.0e-6
        self.temporal_overlap_delta = 0.2
        self.nmide_ns_collar_size = 0

        self.temporal_overlap_filter = build_temporal_overlap_filter(self.temporal_overlap_delta)
        
        self.instance_pair_metrics = { "temporal_intersection": temporal_intersection,
                                       "temporal_union": temporal_union }
        self.default_reported_instance_pair_metrics = [ "temporal_intersection",
                                                        "temporal_union" ]

        self.default_reported_kernel_components = [ "temporal_intersection-over-union" ]            

        self.alignment_metrics = { "rate_fa": self._build_rfa(total_file_dur_minutes),
                                   "p_miss": lambda c, m, f: p_miss(len(c), len(m), len(f)),
                                   "n-mide": self._build_nmide(file_framedur_lookup, self.nmide_ns_collar_size) }

        self.det_curve_metrics = { "p_miss@1rfa": self._build_pmiss_at_rfa(1),
                                   "p_miss@0.2rfa": self._build_pmiss_at_rfa(0.2),
                                   "p_miss@0.15rfa": self._build_pmiss_at_rfa(0.15),
                                   "p_miss@0.1rfa": self._build_pmiss_at_rfa(0.1),
                                   "p_miss@0.03rfa": self._build_pmiss_at_rfa(0.03),
                                   "p_miss@0.01rfa": self._build_pmiss_at_rfa(0.01) }

        self.default_reported_alignment_metrics = [ "n-mide" ]

        self.default_reported_det_curve_metrics = [ "p_miss@1rfa",
                                                    "p_miss@0.2rfa",
                                                    "p_miss@0.15rfa",
                                                    "p_miss@0.1rfa",
                                                    "p_miss@0.03rfa",
                                                    "p_miss@0.01rfa" ]

    def build_kernel(self, system_instances):
        return build_linear_combination_kernel([self.temporal_overlap_filter],
                                               [("temporal_intersection-over-union",
                                                 self.epsilon_temporal_congruence,
                                                 temporal_intersection_over_union),
                                                ("decscore_congruence",
                                                 self.epsilon_decisionscore_congruence,
                                                 build_sed_decscore_congruence(system_instances))])

    def _build_pmiss_at_rfa(self, target_rfa):
        def _metric_func(points):
            return p_miss_at_r_fa(points, target_rfa)

        return _metric_func

    def _build_rfa(self, file_duration):
        def _metric_func(c, m, f):
            return r_fa(len(c), len(m), len(f), file_duration)

        return _metric_func

    def _build_nmide(self, file_duration_lookup, ns_collar_size, cost_fn_miss = lambda x: 1 * x, cost_fn_fa = lambda x: 1 * x):
        def _metric_func(c, m, f):
            return n_mide([(ar.ref, ar.sys) for ar in c], file_duration_lookup, ns_collar_size, cost_fn_miss, cost_fn_fa)

        return _metric_func

    def dump_parameters(self):
        return [("epsilon_temporal_congruence", self.epsilon_temporal_congruence),
                ("epsilon_decisionscore_congruence", self.epsilon_decisionscore_congruence),
                ("delta_temporal_overlap_filter", self.temporal_overlap_delta),
                ("N_MIDE_no_score_zone_collar_size", self.nmide_ns_collar_size)]
