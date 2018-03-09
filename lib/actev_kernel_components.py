# actev_kernel_components.py
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

from metrics import *
from activity_instance import *
from sparse_signal import SparseSignal as S
from helpers import *
from alignment import *

from operator import add

from pprint import pprint

# Returns true if there's some temporal intersection between the
# system and reference activity instances
def temporal_intersection_filter(r, s):
    return temporal_intersection(r, s) > 0

def build_temporal_overlap_filter(threshold):
    def _filter(r, s):
        return temporal_intersection_over_union(r, s) > threshold

    return _filter

def build_spatial_overlap_filter(threshold):
    def _filter(r, s):
        return spatial_intersection_over_union(r, s) > threshold

    return _filter

def build_simple_spatial_overlap_filter(threshold):
    def _filter(r, s):
        return simple_spatial_intersection_over_union(r.spatial_signal, s.spatial_signal) > threshold

    return _filter

def object_type_match_filter(r, s):
    return r.objectType == s.objectType

def _object_signals_to_lookup(temporal_signal, local_objects):
    # Re-using the same empty ObjectLocalizationFrame, this is OK, as
    # long as we don't mutate it somewhere along the way
    empty_olf = ObjectLocalizationFrame.empty()

    def _r(init, o):
        selected_o = [ x for x in temporal_signal.join(o, lambda a, b: b if a else empty_olf, empty_olf).on_steps(lambda x: len(x.spatial_signal) > 0) ]

        init.extend(selected_o)
        return init

    return group_by_func(lambda x: x[0], reduce(_r, local_objects, []), lambda x: x[1])

# Using a factory function here so we can configure the object kernel
# at the protocol level.  Not sure if this is the best place to pass
# in the weightning functions
def build_object_congruence(obj_kernel_builder, cmiss = lambda x: 1 * x, cfa = lambda x: 1 * x):
    def object_congruence(r, s):
        ro, so = r.objects, s.objects

        # For N_MODE computation, localizations spanning multiple files
        # are treated independently
        total_c, total_m, total_f, total_r = [], [], [], []
        for r, s, k in temporal_signal_pairs(r, s):
            local_so_localizations = map(lambda o: o.localization.get(k, S()), so)
            local_ro_localizations = map(lambda o: o.localization.get(k, S()), ro)

            sos_lookup = _object_signals_to_lookup(s, local_so_localizations)
            ros_lookup = _object_signals_to_lookup(r, local_ro_localizations)

            for frame in sos_lookup.viewkeys() | ros_lookup.viewkeys():
                sys = sos_lookup.get(frame, [])
                ref = ros_lookup.get(frame, [])

                c, m, f = perform_alignment(ref, sys, obj_kernel_builder(sys))
                total_c.extend(c)
                total_m.extend(m)
                total_f.extend(f)
                total_r.extend(ref)

        num_miss = len(total_m)
        num_correct = len(total_c)
        def _modes_reducer(init, conf):
            num_filtered_c = len(filter(lambda ar: ar.sys.presenceConf >= conf, total_c))
            num_filtered_fa = len(filter(lambda ar: ar.sys.presenceConf >= conf, total_f))
            num_miss_w_filtered_c = num_miss + num_correct - num_filtered_c
            init.append((conf, mode(num_filtered_c, num_miss_w_filtered_c, num_filtered_fa, cmiss, cfa)))
            return init

        mode_scores = reduce(_modes_reducer, sorted(list({ ar.sys.presenceConf for ar in total_c + total_f })), [])
        min_mode = min(map(lambda x: x[1], mode_scores))

        return min_mode

    return object_congruence
