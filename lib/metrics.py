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
from alignment_record import *
from helpers import *

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
        return { "n-mide": None,
                 "n-mide_num_rejected": 0 }

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
        return { "n-mide": None,
                 "n-mide_num_rejected": len(aligned_pairs) }
    else:
        return { "n-mide": float(reduce(add, mides)) / len(mides),
                 "n-mide_num_rejected": len(aligned_pairs) - len(mides) }

def build_n_mide_metric(file_frame_dur_lookup, ns_collar_size, cost_fn_miss = lambda x: 1 * x, cost_fn_fa = lambda x: 1 * x):
    def _n_mide(pairs):
        return n_mide(pairs, file_frame_dur_lookup, ns_collar_size, cost_fn_miss, cost_fn_fa)

    return _n_mide

def p_miss(num_c, num_m, num_f):
    denom = num_m + num_c
    if denom == 0:
        return None
    else:
        return float(num_m) / denom

def build_pmiss_metric():
    def _p_miss(num_c, num_m, num_f):
        return { "p_miss": p_miss(num_c, num_m, num_f) }
    return _p_miss

def r_fa(num_c, num_m, num_f, denominator):
    return float(num_f) / denominator

def build_rfa_metric(denom):
    def _r_fa(num_c, num_m, num_f):
        return { "rfa": r_fa(num_c, num_m, num_f, denom) }

    return _r_fa

# Returns lowest y value for each x_targ.  The points argument should
# be a list of tuples, where each tuple is of the form
# (confidence_value, metrics_dict)
def get_points_along_confidence_curve(points, x_label, x_key, y_label, y_key, x_targs, y_default = 1.0):
    if len(x_targs) == 0:
        return {}

    def _metric_str(targ):
        return "{}@{}{}".format(y_label, targ, x_label)

    # Note ** currently reporting out the 'y_default' for each targ if
    # the curve is empty
    if len(points) == 0:
        return { _metric_str(t): y_default for t in x_targs }

    sorted_targs = sorted(x_targs, reverse = True)
    curr_targ = sorted_targs[-1]

    out_metrics = {}

    x, y = None, None
    last_y = None
    last_x = 0.0
    exact_match = False
    sorted_points = sorted([ (ds, x_key(m), y_key(m)) for ds, m in points ], None, lambda x: x[0])
    while True:
        if x is not None:
            if abs(x - curr_targ) < 1e-10:
                exact_match = True
            elif x > curr_targ:
                if last_y == None:
                    out_metrics[_metric_str(curr_targ)] = y_default
                elif exact_match:
                    out_metrics[_metric_str(curr_targ)] = last_y
                    exact_match = False
                else: # interpolate
                    out_metrics[_metric_str(curr_targ)] = last_y + (y - last_y) * (float(curr_targ - last_x) / (x - last_x))

                sorted_targs.pop()
                if len(sorted_targs) == 0:
                    break
                else:
                    curr_targ = sorted_targs[-1]
                    continue

        # Only pop the next point if we're sure we haven't overstepped any remaining targs
        last_y, last_x = y, x
        if len(sorted_points) > 0:
            ds, x, y = sorted_points.pop()
        else:
            break

    # If we ran out of points but still have targets, generate the
    # metrics here
    last_y = y
    for targ in sorted_targs:
        out_metrics[_metric_str(targ)] = y_default if last_y is None else last_y

    return out_metrics

def mean_exclude_none(values):
    fv = filter(lambda v: v is not None, values)
    return { "mean": float(reduce(add, fv, 0)) / len(fv) if len(fv) > 0 else None,
             "mean_num_rejected": len(values) - len(fv) }

def mode(num_c, num_m, num_f, cost_m, cost_f):
    return float(cost_m(num_m) + cost_f(num_f)) / (num_c + num_m)

def build_mode_metric(cost_fn_m = lambda x: 1 * x, cost_fn_f = lambda x: 1 * x):
    def _mode(num_c, num_m, num_f):
        # Don't attempt to compute mode if there are no reference
        # objects
        value = mode(num_c, num_m, num_f, cost_fn_m, cost_fn_f) if num_m + num_c > 0 else None
        return { "mode": value }

    return _mode

def build_sweeper(conf_key_func, measure_funcs):
    def _sweep(alignment_records):
        c, m, f = partition_alignment(alignment_records)
        total_c = len(c)
        num_m = len(m)
        # num_f = len(f)

        out_points = []
        current_c, current_f = 0, 0
        ars = sorted(c + f, None, conf_key_func)
        while len(ars) > 0:
            ar = ars.pop()
            conf = conf_key_func(ar)

            if ar.alignment == "CD":
                current_c += 1
            elif ar.alignment == "FA":
                current_f += 1

            if len(ars) > 0:
                if conf != conf_key_func(ars[-1]):
                    out_points.append((conf, reduce(merge_dicts, [ m(current_c, num_m + (total_c - current_c), current_f) for m in measure_funcs ], {})))
            else:
                out_points.append((conf, reduce(merge_dicts, [ m(current_c, num_m + (total_c - current_c), current_f) for m in measure_funcs ], {})))

        return out_points

    return _sweep

def flatten_sweeper_records(recs, keys):
    return [ [ c ] + [ d[k] for k in keys ] for c, d in recs ]

def build_det_sweeper(conf_key_func, rfa_denom):
    return build_sweeper(conf_key_func, [ build_rfa_metric(rfa_denom),
                                          build_pmiss_metric() ])
