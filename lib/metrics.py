# metrics.py
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

from operator import add
from sparse_signal import SparseSignal as S

def _signal_pairs(r, s, signal_accessor, key_join_op = set.union):
    rl, sl = r.localization, s.localization
    return [ (signal_accessor(rl, k), signal_accessor(sl, k), k) for k in key_join_op(set(rl.keys()), set(sl.keys())) ]

def _temporal_signal_accessor(localization, k):
    return S(localization.get(k, {}))

def temporal_signal_pairs(r, s, key_join_op = set.union):
    return _signal_pairs(r, s, _temporal_signal_accessor, key_join_op)

def temporal_intersection(r, s):
    return reduce(add, [ (r & s).area() for r, s, k in temporal_signal_pairs(r, s, set.intersection) ], 0)

def temporal_union(r, s):
    return reduce(add, [ (r | s).area() for r, s, k in temporal_signal_pairs(r, s) ], 0)

def temporal_fa(r, s):
    return reduce(add, [ (s - (r & s)).area() for r, s, k in temporal_signal_pairs(r, s) ], 0)

def temporal_miss(r, s):
    return reduce(add, [ (r - (r & s)).area() for r, s, k in temporal_signal_pairs(r, s) ], 0)

def temporal_intersection_over_union(r, s):
    intersection = temporal_intersection(r, s)
    union = temporal_union(r, s)

    # Not sure if this is the best way to handle union == 0; but in
    # practise should never encounter this case
    return float(intersection) / union if union != 0 else 0.0

def _spatial_signal_accessor(localization, k):
    if k in localization:
        return localization.get(k).spatial_signal
    else:
        return S()

def spatial_signal_pairs(r, s, key_join_op = set.union):
    return _signal_pairs(r, s, _spatial_signal_accessor, key_join_op)

def simple_spatial_intersection(r, s):
    return r.join_nd(s, 2, min).area()

def simple_spatial_union(r, s):
    return r.join_nd(s, 2, max).area()

def simple_spatial_intersection_over_union(r, s):
    intersection = simple_spatial_intersection(r, s)
    union = simple_spatial_union(r, s)

    # Not sure if this is the best way to handle union == 0; but in
    # practise should never encounter this case
    return float(intersection) / union if union != 0 else 0.0

def spatial_intersection(r, s):
    return reduce(add, [ simple_spatial_intersection(r, s) for r, s, k in spatial_signal_pairs(r, s, set.intersection) ], 0)

def spatial_union(r, s):
    return reduce(add, [ simple_spatial_union(r, s) for r, s, k in spatial_signal_pairs(r, s) ], 0)

def spatial_intersection_over_union(r, s):
    intersection = spatial_intersection(r, s)
    union = spatial_union(r, s)

    # Not sure if this is the best way to handle union == 0; but in
    # practise should never encounter this case
    return float(intersection) / union if union != 0 else 0.0

# aligned_pairs should be a list of tuples being (reference, system);
# where reference and system are each ActivityInstance objects
def n_mide(aligned_pairs, file_framedur_lookup, ns_collar_size, cost_fn_miss, cost_fn_fa):
    # Should consider another paramemter for for all files to consider
    # for FA denominator calculation, in the case of cross-file
    # activity instances
    num_aligned = len(aligned_pairs)

    if num_aligned == 0:
        return None

    def _sub_reducer(init, pair):
        init_miss, init_fa, init_miss_d, init_fa_d = init
        rs, ss, k = pair

        ns_collar = rs.generate_collar(ns_collar_size)
        c_r = rs - ns_collar
        c_s = ss - ns_collar
        col_r = rs | ns_collar

        miss = (c_r - c_s).area()
        fa = (c_s - c_r).area()

        return (init_miss + miss, init_fa + fa, init_miss_d + c_r.area(), init_fa_d + (file_framedur_lookup.get(k) - col_r.area()))

    def _reducer(init, pair):
        r, s = pair
        # Using the _sub_reducer here is important in the case of
        # cross-file activity instances
        miss, fa, miss_denom, fa_denom = reduce(_sub_reducer, temporal_signal_pairs(r, s), (0, 0, 0, 0))
        if miss_denom > 0 and fa_denom > 0:
            init.append(cost_fn_miss(float(miss) / miss_denom) + cost_fn_fa(float(fa) / fa_denom))

        return init

    mides = reduce(_reducer, aligned_pairs, [])

    if len(mides) == 0:
        return None
    else:
        return float(reduce(add, mides)) / len(mides)

# Should refactor this to be part of the n_mide calculation
def n_mide_count_rejected(aligned_pairs, file_framedur_lookup, ns_collar_size):
    if len(aligned_pairs) == 0:
        return 0

    def _sub_reducer(init, pair):
        miss_denom, fa_denom = init
        rs, ss, k = pair

        ns_collar = rs.generate_collar(ns_collar_size)
        c_r = rs - ns_collar
        col_r = rs | ns_collar

        return (miss_denom + c_r.area(), fa_denom + file_framedur_lookup.get(k) - col_r.area())

    def _reducer(init, pair):
        r, s = pair
        # Using the _sub_reducer here is important in the case of
        # cross-file activity instances
        total_miss_denom, total_fa_denom = reduce(_sub_reducer, temporal_signal_pairs(r, s), (0, 0))

        return init + 1 if total_miss_denom == 0 or total_fa_denom <= 0 else init

    return reduce(_reducer, aligned_pairs, 0)

def p_miss(num_c, num_m, num_f):
    denom = num_m + num_c
    if denom == 0:
        return None
    else:
        return float(num_m) / denom

def r_fa(num_c, num_m, num_f, denominator):
    return float(num_f) / denominator

# Really just a generic function for finding lowest y at a given x for
# a DET curve
def p_miss_at_r_fa(points, target_rfa):
    last_pmiss = None
    last_rfa = 0.0
    exact_match = False
    for p in sorted(points, None, lambda x: x[0], True):
        ds, rfa, pmiss = p

        if abs(rfa - target_rfa) < 1e-10:
            exact_match = True
        elif rfa > target_rfa:
            if last_pmiss == None:
                return 1.0
            elif exact_match:
                return last_pmiss
            else: # interpolate
                return last_pmiss + (pmiss - last_pmiss) * (float(target_rfa - last_rfa) / (rfa - last_rfa))

        last_pmiss = pmiss
        last_rfa = rfa

    return last_pmiss

def mean_exclude_none(values):
    fv = filter(lambda v: v is not None, values)
    return float(reduce(add, fv, 0)) / len(fv) if len(fv) > 0 else None

def mode(num_c, num_m, num_f, cost_m, cost_f):
    return float(cost_m(num_m) + cost_f(num_f)) / (num_c + num_m)
