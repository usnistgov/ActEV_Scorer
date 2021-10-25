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

import numpy as np
from operator import add
from sparse_signal import SparseSignal as S
from alignment_record import *
from helpers import *
from functools import reduce


def _signal_pairs(r, s, signal_accessor, key_join_op=set.union):
    rl, sl = r.localization, s.localization
    return [(signal_accessor(rl, k), signal_accessor(sl, k), k) for
            k in key_join_op(set(rl.keys()), set(sl.keys()))]


def _temporal_signal_accessor(localization, k):
    return S(localization.get(k, {}))


def temporal_signal_pairs(r, s, key_join_op=set.union):
    return _signal_pairs(r, s, _temporal_signal_accessor, key_join_op)


def _single_signal(s, signal_accessor, key_join_op=set.union):
    sl = s.localization
    return [(signal_accessor(sl, k), k) for k in sl.keys()][0]


def temporal_single_signal(s, key_join_op=set.union):
    return _single_signal(s, _temporal_signal_accessor, key_join_op)


def temporal_single_signal_area(s, key_join_op=set.union):
    si = _single_signal(s, _temporal_signal_accessor, key_join_op)
    return si[0].area()


def temporal_intersection(r, s):
    return reduce(
        add, [(r & s).area() for
              r, s, k in temporal_signal_pairs(r, s, set.intersection)], 0)


def temporal_intersection_over_area(r, s):
    ti = temporal_intersection(r, s)
    r_area = temporal_single_signal_area(r)
    return (ti * 1.0) / r_area


def temporal_union(r, s):
    return reduce(
        add, [(r | s).area() for r, s, k in temporal_signal_pairs(r, s)], 0)


def temporal_fa(r, s):
    return reduce(
        add, [(s - (r & s)).area() for
              r, s, k in temporal_signal_pairs(r, s)], 0)


def temporal_miss(r, s):
    return reduce(
        add, [(r - (r & s)).area() for
              r, s, k in temporal_signal_pairs(r, s)], 0)


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


def spatial_signal_pairs(r, s, key_join_op=set.union):
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
    return reduce(
        add, [simple_spatial_intersection(r, s) for
              r, s, k in spatial_signal_pairs(r, s, set.intersection)], 0)


def spatial_union(r, s):
    return reduce(
        add, [simple_spatial_union(r, s) for
              r, s, k in spatial_signal_pairs(r, s)], 0)


def spatial_intersection_over_union(r, s):
    intersection = spatial_intersection(r, s)
    union = spatial_union(r, s)
    # Not sure if this is the best way to handle union == 0; but in
    # practise should never encounter this case
    return float(intersection) / union if union != 0 else 0.0


def compute_auc(tfa_pmiss, typ, thresh=1):
    """ Computes the area under curve (AUC) given FPR and TPR values
    fpr: false positive rates
    tpr: true positive rates
    fpr_stop: fpr value for calculating partial AUC"""

    if typ == "tfa":
        xpoints = [
            'p_miss@0.01tfa', 'p_miss@0.02tfa', 'p_miss@0.03tfa',
            'p_miss@0.1tfa', 'p_miss@0.15tfa', 'p_miss@0.2rfa', 'p_miss@1tfa']
    else:
        xpoints = [
            'p_miss@0.01rfa', 'p_miss@0.02rfa', 'p_miss@0.03rfa',
            'p_miss@0.1rfa', 'p_miss@0.15rfa', 'p_miss@0.2rfa', 'p_miss@1rfa']

    fpr = [0.0, 0.01, 0.03, 0.1, 0.15, 0.2, 1]
    oldkey = "none"
    tnr = [1.0]

    for xp in xpoints:
        try:
            tnr.append(tfa_pmiss[xp])
            oldkey = xp
        except Exception:
            if oldkey == "none":
                tnr.append(1.0)
            else:
                tnr.append(tfa_pmiss[oldkey])
    width = [x - fpr[i] for i, x in enumerate(fpr[1:]) if fpr[i + 1] <= thresh]
    height = [(x + tnr[i]) / 2 for i, x in enumerate(tnr[1:])]
    p_height = height[0:len(width)]
    auc = sum([width[i] * (p_height[i]) for i in range(0, len(width))])
    return auc


def compute_auc_new(pmiss, fa, thresh=1):
    fa_sum = 0
    prev_x = 0
    prev_y = 1
    cur_x = 0
    cur_y = 0
    cnt = 0

    if len(fa) != 0:
        if np.isnan(pmiss[0]):
            return "None"
        while cnt < len(fa):
            if thresh < fa[cnt]:
                break
            if fa[cnt] == 0:
                prev_x = fa[cnt]
                prev_y = pmiss[cnt]
                cnt = cnt + 1
                continue
            cur_x = fa[cnt]
            cur_y = pmiss[cnt]
            fa_sum = fa_sum + (0.5 * (prev_y + cur_y) * (abs(cur_x - prev_x)))
            prev_x = cur_x
            prev_y = cur_y
            cnt = cnt + 1
            if cnt == len(fa):
                break

    if cnt != 0 and thresh == fa[cnt - 1]:
        return fa_sum
    if cnt >= len(fa):
        fa_sum = fa_sum + (prev_y * (thresh - prev_x))
        return fa_sum

    cur_x = thresh
    m = (prev_y - pmiss[cnt]) / (prev_x - fa[cnt])
    b = prev_y - (m * prev_x)
    cur_y = (cur_x * m) + b
    fa_sum = fa_sum + (0.5 * (prev_y + cur_y) * (abs(cur_x - prev_x)))
    return fa_sum


def get_auc_new(dm_data, typ, activity, threshold=[1] + [
        x/100 for x in range(95, 1, -5)]+[0.04, 0.03, 0.02, 0.01]):
    fa = dm_data.fa
    pmiss = dm_data.fn
    audc_meas = []
    threshold.sort()
    for t in threshold:
        audc = compute_auc_new(pmiss, fa, thresh=t)
        audc_meas.append((activity, 'AUDC@' + str(t) + typ.lower(), audc))
        if audc == "None":
            audc_meas.append(
                (activity, 'nAUDC@' + str(t) + typ.lower(), "None"))
        else:
            audc_meas.append(
                (activity, 'nAUDC@' + str(t) + typ.lower(), float(audc)/t))
    return audc_meas


def compute_auc_mean(auc):
    s = 0
    for v in auc:
        s = s + v
    return float(s)/len(auc)


def get_auc_mean(auc_data):
    values = {}
    auc_mean = []
    for d in auc_data:
        if d[2] == "None":
            continue
        if d[1] not in values:
            values[d[1]] = [d[2]]
        else:
            values[d[1]].append(d[2])

    for key, item in values.items():
        auc_mean.append(("mean-" + key, compute_auc_mean(item)))

    return auc_mean


def get_auc(tfa_pmiss, typ, threshold=[1, 0.2, 0.15, 0.1, 0.03, 0.01]):
    auc = {}
    for t in threshold:
        ds = "AUDC@" + str(t) + typ
        auc[ds] = compute_auc(tfa_pmiss, typ, thresh=t)
        dsn = "nAUDC@" + str(t) + typ
        auc[dsn] = auc[ds] / t
    return auc


# aligned_pairs should be a list of tuples being (reference, system);
# where reference and system are each ActivityInstance objects
def n_mide(aligned_pairs, file_framedur_lookup, ns_collar_size, cost_fn_miss,
           cost_fn_fa):
    # Should consider another paramemter for for all files to consider
    # for FA denominator calculation, in the case of cross-file
    # activity instances
    num_aligned = len(aligned_pairs)

    if num_aligned == 0:
        return {"n-mide": None,
                "n-mide_num_rejected": 0}

    def _sub_reducer(init, pair):
        init_miss, init_fa, init_miss_d, init_fa_d = init
        rs, ss, k = pair
        ns_collar = rs.generate_collar(ns_collar_size)
        c_r = rs - ns_collar
        c_s = ss - ns_collar
        col_r = rs | ns_collar
        miss = (c_r - c_s).area()
        fa = (c_s - c_r).area()
        return (init_miss + miss, init_fa + fa, init_miss_d + c_r.area(),
                init_fa_d + (file_framedur_lookup.get(k) - col_r.area()))

    def _reducer(init, pair):
        r, s = pair
        # Using the _sub_reducer here is important in the case of
        # cross-file activity instances
        miss, fa, miss_denom, fa_denom = reduce(
            _sub_reducer, temporal_signal_pairs(r, s), (0, 0, 0, 0))
        if miss_denom > 0 and fa_denom > 0:
            init.append(cost_fn_miss(float(miss) / miss_denom) +
                        cost_fn_fa(float(fa) / fa_denom))
        return init

    mides = reduce(_reducer, aligned_pairs, [])
    if len(mides) == 0:
        return {"n-mide": None,
                "n-mide_num_rejected": len(aligned_pairs)}
    else:
        return {"n-mide": float(reduce(add, mides)) / len(mides),
                "n-mide_num_rejected": len(aligned_pairs) - len(mides)}


def special_join(signals):
    if len(signals) == 1:
        return signals[0][0]

    def _reducer(init, pair):
        if len(pair) == 1:
            init.append(pair[0])
        else:
            if isinstance(pair[0], tuple):
                s1 = pair[0][0]
            else:
                s1 = pair[0]
            if isinstance(pair[1], tuple):
                s2 = pair[1][0]
            else:
                s2 = pair[1]
            init.append(s1.join(s2, add))
        return init
    while len(signals) != 1:
        gr_sig = [signals[i * 2:(i + 1) * 2] for
                  i in range((len(signals) + 2 - 1) // 2)]
        signals = reduce(_reducer, gr_sig, [])
    return signals[0]


def fa_meas_v2(ref_sig, sys_sig, sys_sig_add):
    tfa_denom = {}
    tfa_numer = {}
    System_Sig = {}
    Ref_Sig = {}
    NR_Ref_Sig = {}
    numer_sum = 0
    denom_sum = 0
    ref_temp_add_all = ref_sig[0]
    not_ref_all = ref_sig[1]
    nr_area_all = ref_sig[2]
    for key, value in ref_temp_add_all.items():
        ref_temp_add = value
        not_ref = not_ref_all[key]
        nr_area = nr_area_all[key]
        sys_temp = sys_sig_add[key]
        num_sig = sys_temp - ref_temp_add
        numer = num_sig.area()
        tfa_denom[key] = nr_area
        tfa_numer[key] = numer
        System_Sig[key] = sys_temp
        Ref_Sig[key] = ref_temp_add
        NR_Ref_Sig[key] = not_ref
        numer_sum = numer_sum + numer
        denom_sum = denom_sum + nr_area
    if denom_sum == 0:
        return {"tfa": None,
                "tfa_denom": denom_sum,
                "tfa_numer": numer_sum,
                "System_Sig": System_Sig,
                "Ref_Sig": Ref_Sig,
                "NR_Ref_Sig": NR_Ref_Sig}

    return {"tfa": (float(numer_sum) / denom_sum),
            "tfa_denom": denom_sum,
            "tfa_numer": numer_sum,
            "System_Sig": System_Sig,
            "Ref_Sig": Ref_Sig,
            "NR_Ref_Sig": NR_Ref_Sig}


def fa_meas(ref_sig, sys_sig, sys_sig_add):
    # Need to modify join, find ways to keep from doing full join each time.
    # reference stays the same, calculated once. system, just need to include
    # new false alarms
    System_Sig = {}
    Ref_Sig = {}
    NR_Ref_Sig = {}
    ref_temp_add_all = ref_sig[0]
    not_ref_all = ref_sig[1]
    nr_area_all = ref_sig[2]
    denom_sum = 0
    numer_sum = 0
    for key, value in ref_temp_add_all.items():
        ref_temp_add = value
        not_ref = not_ref_all[key]
        nr_area = nr_area_all[key]
        sys_temp = sys_sig[key]
        System_Sig[key] = sys_temp
        Ref_Sig[key] = ref_temp_add
        NR_Ref_Sig[key] = not_ref

        def _reducer(init, pair):
            r, s = pair
            inters = (r & s).area()
            init = init + inters
            return init

        numer_pairs = [[not_ref, s[0]] for s in sys_temp]
        numer_sum = numer_sum + reduce(_reducer, numer_pairs, 0)
        denom_sum = denom_sum + nr_area
    if denom_sum == 0:
        return {"tfa": None,
                "tfa_denom": denom_sum,
                "tfa_numer": numer_sum,
                "System_Sig": System_Sig,
                "Ref_Sig": Ref_Sig,
                "NR_Ref_Sig": NR_Ref_Sig}
    return {"tfa": (float(numer_sum) / denom_sum),
            "tfa_denom": denom_sum,
            "tfa_numer": numer_sum,
            "System_Sig": System_Sig,
            "Ref_Sig": Ref_Sig,
            "NR_Ref_Sig": NR_Ref_Sig}


def build_n_mide_metric(file_frame_dur_lookup, ns_collar_size,
                        cost_fn_miss=lambda x: 1 * x,
                        cost_fn_fa=lambda x: 1 * x):
    def _n_mide(pairs):
        return n_mide(pairs, file_frame_dur_lookup, ns_collar_size,
                      cost_fn_miss, cost_fn_fa)
    return _n_mide


def build_fa_metric(file_frame_dur_lookup, ns_collar_size,
                    cost_fn_miss=lambda x: 1 * x,
                    cost_fn_fa=lambda x: 1 * x):
    def _fa(pairs):
        return fa_met(pairs, file_frame_dur_lookup, ns_collar_size,
                      cost_fn_miss, cost_fn_fa)
    return _fa


def w_p_miss(num_c, num_m, num_f, denominator, numerator):
    denom = num_m + num_c + denominator
    numer = num_m + numerator
    if num_m + num_c == 0:
        return None
    else:
        return float(numer) / denom


def p_miss(num_c, num_m, num_f):
    denom = num_m + num_c
    if denom == 0:
        return None
    else:
        return float(num_m) / denom


def build_pmiss_metric():
    def _p_miss(c, m, f):
        return {"p_miss": p_miss(len(c), len(m), len(f))}
    return _p_miss


def build_wpmiss_metric(denom, numer):
    def _w_p_miss(c, m, f):
        return {"w_p_miss": w_p_miss(len(c), len(m), len(f), denom, numer)}
    return _w_p_miss


def r_fa(num_c, num_m, num_f, denominator):
    return float(num_f) / denominator


def build_rfa_metric(denom):
    def _r_fa(c, m, f):
        return {"rfa": r_fa(len(c), len(m), len(f), denom)}
    return _r_fa


# Returns y value for lowest confidence value at each x_targ.  The
# points argument should be a list of tuples, where each tuple is of
# the form (confidence_value, metrics_dict)
def get_points_along_confidence_curve(points, x_label, x_key, y_label, y_key,
                                      x_targs, y_default=1.0):
    if len(x_targs) == 0:
        return {}

    def _metric_str(targ):
        return "{}@{}{}".format(y_label, targ, x_label)

    # Note ** currently reporting out the 'y_default' for each targ if
    # the curve is empty
    if len(points) == 0:
        return {_metric_str(t): y_default for t in x_targs}

    sorted_targs = sorted(x_targs, reverse=True)
    curr_targ = sorted_targs[-1]
    out_metrics = {}
    x, y = None, None
    last_y = None
    last_x = 0.0
    exact_match = False
    sorted_points = sorted([(ds, x_key(m), y_key(m)) for
                            ds, m in points], key=lambda x: x[0])
    while True:
        if x is not None:
            if abs(x - curr_targ) < 1e-10:
                exact_match = True
            elif x > curr_targ:
                if last_y is None:
                    out_metrics[_metric_str(curr_targ)] = y_default
                elif exact_match:
                    out_metrics[_metric_str(curr_targ)] = last_y
                    exact_match = False
                else:  # interpolate
                    out_metrics[_metric_str(curr_targ)] = last_y + \
                        (y - last_y) * (
                            float(curr_targ - last_x) / (x - last_x))

                sorted_targs.pop()
                if len(sorted_targs) == 0:
                    break
                else:
                    curr_targ = sorted_targs[-1]
                    continue

        # Only pop the next point if we're sure we haven't overstepped
        # any remaining targs
        last_y, last_x = y, x
        if len(sorted_points) > 0:
            ds, x, y = sorted_points.pop()
        else:
            break

    # If we ran out of points but still have targets, generate the
    # metrics here
    last_y = y
    for targ in sorted_targs:
        out_metrics[_metric_str(targ)] = y_default if last_y is None else \
            last_y

    return out_metrics


def mean_exclude_none(values):
    fv = list(filter(lambda v: v is not None, values))
    return {"mean": float(reduce(add, fv, 0)) /
            len(fv) if len(fv) > 0 else None,
            "mean_num_rejected": len(list(values)) - len(fv) if
            type(values) == map else len(values) - len(fv)}


def mode(num_c, num_m, num_f, cost_m, cost_f):
    return float(cost_m(num_m) + cost_f(num_f)) / (num_c + num_m)


def build_mode_metric(cost_fn_m=lambda x: 1 * x, cost_fn_f=lambda x: 1 * x):
    def _mode(c, m, f):
        # Don't attempt to compute mode if there are no reference
        # objects
        num_c, num_m, num_f = len(c), len(m), len(f)
        value = mode(num_c, num_m, num_f, cost_fn_m, cost_fn_f) if \
            num_m + num_c > 0 else None
        return {"mode": value}
    return _mode


def mote(num_c, num_m, num_f, num_id, cost_m, cost_f, cost_id):
    return float(cost_m(num_m) + cost_f(num_f) + cost_id(num_id)) / \
        (num_c + num_m)


def build_mote_metric(frame_correct_align, conf_func,
                      cost_fn_m=lambda x: 1 * x, cost_fn_f=lambda x: 1 * x,
                      cost_fn_id=lambda x: 1 * x):
    def _mote(c, m, f):
        num_c, num_m, num_f = len(c), len(m), len(f)
        conf = sorted(set(map(conf_func, c + f)))[0]
        num_id = 0
        cur_align = {}
        for i in frame_correct_align:
            ar = i[1]
            if ar.sys.presenceConf >= conf:
                try:
                    if cur_align[ar.ref.objectID] != ar.sys.objectID:
                        num_id += 1
                        cur_align[ar.ref.objectID] = ar.sys.objectID
                except Exception:
                    cur_align[ar.ref.objectID] = ar.sys.objectID

        value = mote(num_c, num_m, num_f, num_id, cost_fn_m, cost_fn_f,
                     cost_fn_id) if num_m + num_c > 0 else None
        return {"mote": value}
    return _mote


def build_ref_sig(ref, file_framedur_lookup):
    # Need to modify join, find ways to keep from doing full join each time.
    # reference stays the same, calculated once. system, just need to include
    # new false alarms
    ref_temp_add = {}
    not_ref = {}
    nr_area = {}
    if ref == {}:
        return [{}, {}, {}]
    for key, value in ref.items():
        ref_temp = [temporal_single_signal(b) for b in value]
        ref_temp_add[key] = reduce(add, [r[0] for r in ref_temp], S())
        not_ref[key] = ref_temp_add[key].not_sig(file_framedur_lookup[key])
        nr_area[key] = not_ref[key].area()

    return[ref_temp_add, not_ref, nr_area]


def build_sys_sig(syssig):
    if len(syssig) == 0:
        return [{}, []]
    sys_temp = [temporal_single_signal(s) for s in syssig]
    sys_temp_add = special_join(sys_temp)
    return [sys_temp_add, sys_temp]


def add_sys_sig(init, newsig):
    if len(newsig) == 0:
        return init
    sys_temp_ret = [temporal_single_signal(s) for s in newsig]
    return sys_temp_ret


def build_sweeper(conf_key_func, measure_funcs, uniq_conf_limit=0,
                  file_framedur_lookup=0):
    def _sweep(alignment_records):
        c, m, f = partition_alignment(alignment_records)
        sys_sig = {}
        sys_sig_add = {}
        ref_all = {}
        if file_framedur_lookup != 0:
            for key in file_framedur_lookup:
                sys_sig[key] = []
                sys_sig_add[key] = S()
                ref_all[key] = []
            for ar in c:
                ref_all[ar.video_file].append(ar.ref)
            for ar in m:
                ref_all[ar.video_file].append((ar.ref))
            ref_sigs = build_ref_sig(ref_all, file_framedur_lookup)
            fa_func = measure_funcs.pop()

        out_points = []
        current_c, current_f = [], []
        # m records don't need to be sorted as they have None
        # confidence scores
        current_m = m + sorted(c, key=conf_key_func)
        remaining_f = sorted(f, key=conf_key_func)
        uniq_confs = sorted(set(map(conf_key_func, c + f)), reverse=True)

        if uniq_conf_limit != 0:
            if (len(uniq_confs) > uniq_conf_limit):
                le = len(uniq_confs)
                indices = np.round(np.linspace(0, len(uniq_confs)-1,
                                   min(len(uniq_confs), uniq_conf_limit))
                                   ).astype(int)
                uniq_confs = list(np.array(uniq_confs)[indices])
                print("""[Info] Reducing to {} unique confidence scores for"""
                      """ Sweeping to {} [{},{}] unique confidence scores"""
                      """""".format(
                        le, len(uniq_confs), uniq_confs[0], uniq_confs[-1]))

        for conf in uniq_confs:
            newsig = {}
            newsig_tem = {}
            while len(current_m) > 0 and current_m[-1].alignment != "MD" and \
                    conf_key_func(current_m[-1]) >= conf:
                if file_framedur_lookup != 0:
                    if not current_m[-1].video_file in newsig:
                        newsig[current_m[-1].video_file] = []
                    newsig[current_m[-1].video_file].append(current_m[-1])
                current_c.append(current_m.pop())
            while len(remaining_f) > 0 and \
                    conf_key_func(remaining_f[-1]) >= conf:
                if file_framedur_lookup != 0:
                    if not remaining_f[-1].video_file in newsig:
                        newsig[remaining_f[-1].video_file] = []
                    newsig[remaining_f[-1].video_file].append(remaining_f[-1])
                current_f.append(remaining_f.pop())
            if file_framedur_lookup != 0:
                if newsig != {}:
                    for key, value in newsig.items():
                        newsig_tem[key] = add_sys_sig(
                            sys_sig[key], [(ar.sys) for ar in newsig[key]])
                        sys_sig[key] = sys_sig[key] + newsig_tem[key]
                        sys_sig_add[key] = reduce(
                            add, [s[0] for s in newsig_tem[key]],
                            sys_sig_add[key])
                out_points.append((
                    conf, reduce(merge_dicts, [
                        m(current_c, current_m, current_f) for
                        m in measure_funcs], fa_func(
                            ref_sigs, sys_sig, sys_sig_add))))
            else:
                out_points.append((
                    conf, reduce(merge_dicts, [
                        m(current_c, current_m, current_f) for
                        m in measure_funcs], {})))
        return out_points
    return _sweep


def flatten_sweeper_records(recs, keys):
    return [[c] + [d[k] for k in keys] for c, d in recs]


def compute_ap(precision, recall):
    mprec = np.hstack([[0], precision, [0]])
    mrec = np.hstack([[0], recall, [1]])
    for i in range(len(mprec) - 1)[::-1]:
        mprec[i] = max(mprec[i], mprec[i + 1])
    idx = np.where(mrec[1::] != mrec[0:-1])[0] + 1
    ap = np.sum((mrec[idx] - mrec[idx - 1]) * mprec[idx])
    return ap


def compute_map(system_activities, reference_activities, activity_index,
                file_index, thresholds=[x/100 for x in range(5, 100, 5)]):
    # Largely inspired from ActivityNet code
    # http://activity-net.org/challenges/2021/tasks/anet_localization.html
    def _filter_by_act(activities, key):
        return list(filter(lambda x: x.activity == key, activities))

    def _filter_by_file(activities, key):
        return list(filter(lambda x: list(
            x.localization.keys())[0] == key, activities))

    ap, precision, recall = {}, {}, {}
    for activity in activity_index:
        syss = _filter_by_act(system_activities, activity)
        refs = _filter_by_act(reference_activities, activity)
        ap[activity] = np.zeros(len(thresholds))
        npos = float(len(refs))
        if npos == 0:
            continue
        lock_gt = np.ones((len(thresholds), len(refs))) * -1

        # Sort predictions by decreasing score order.
        sort_idx = argsort(syss, 'presenceConf')[::-1]
        prediction = [syss[idx] for idx in sort_idx]

        # Initialize true positive and false positive vectors.
        tp = np.zeros((len(thresholds), len(prediction)))
        fp = np.zeros((len(thresholds), len(prediction)))

        for idx, this_pred in enumerate(prediction):
            this_gt = _filter_by_file(
                refs, list(this_pred.localization.keys())[0])
            tiou_arr = [temporal_intersection_over_union(
                ref, this_pred) for ref in this_gt]
            tiou_sorted_idx = argsort(tiou_arr)[::-1]
            for tidx, tiou_thr in enumerate(thresholds):
                for jdx in tiou_sorted_idx:
                    if tiou_arr[jdx] < tiou_thr:
                        fp[tidx, idx] = 1
                        break
                    if lock_gt[tidx, jdx] >= 0:
                        continue
                    # Assign as true positive after the filters above.
                    tp[tidx, idx] = 1
                    lock_gt[tidx, jdx] = idx
                    break

                if fp[tidx, idx] == 0 and tp[tidx, idx] == 0:
                    fp[tidx, idx] = 1

        tp_cumsum = np.cumsum(tp, axis=1).astype(float)
        fp_cumsum = np.cumsum(fp, axis=1).astype(float)
        recall_cumsum = tp_cumsum / npos
        precision_cumsum = tp_cumsum / (tp_cumsum + fp_cumsum)

        for tidx in range(len(thresholds)):
            if thresholds[tidx] == 0.5:
                if list(precision_cumsum[tidx, :]) != []:
                    precision[activity] = precision_cumsum[tidx, :]
                if list(recall_cumsum[tidx, :]) != []:
                    recall[activity] = recall_cumsum[tidx, :]
            ap[activity][tidx] = compute_ap(
                precision_cumsum[tidx, :], recall_cumsum[tidx, :])

    ap_len = len(ap)
    ap_metrics = {'AP': [], 'mAP': [], 'pr': (precision, recall)}
    mAP = {}
    for thd in thresholds:
        mAP[thd] = 0
    for activity in ap:
        for i in range(len(thresholds)):
            thd = thresholds[i]
            v = round(float(ap[activity][i]), 18)
            ap_metrics['AP'].append((activity, 'AP@%.2ftIoU' % thd, v))
            mAP[thd] += v
    for thd in mAP:
        ap_metrics['mAP'].append(('mAP@%.2ftIoU' % thd, mAP[thd]/ap_len))
    return ap_metrics


def object_map(system_activities, reference_activities, activity_index,
               file_index, thresholds=[x/100 for x in range(5, 100, 5)]):
    def _filter(function, iterable):
        return list(filter(function, iterable))

    def _unify_object_ids(instance_list):
        """Makes all object IDs unique in an instance list"""
        curr_id = 1
        for instance in instance_list:
            for obj in instance.objects:
                obj.objectID = curr_id
                curr_id += 1
        return instance_list
    
    def _objects(instance_list):
        """Return a list of all objects embedded in `instance_list`"""
        # Spatial methods require this to work.
        for instance in instance_list:
            k = list(instance.localization.keys())[0]
            for obj in instance.objects:
                obj.localization = obj.localization[k]
        return reduce(lambda x,y: x+y, [inst.objects for inst in instance_list], [])

    ap, precision, recall = {}, {}, {}
    for activity in activity_index:
        ap[activity] = np.zeros(len(thresholds))

        # Filtering s and r
        filter_by_activity = lambda x: x.activity == activity
        refs_by_activity = _filter(filter_by_activity, reference_activities)
        syss_by_activity = _filter(filter_by_activity, system_activities)

        # Storing mAP for each threshold per file
        # That means each element is an array
        # Size <= len(file_index) (some file may not
        #     have any instances for a given activity)
        # Size of each element = len(thresholds)
        files_AP = []
        for video in file_index:
            # Filtering s and r again
            filter_by_video = lambda x: list(x.localization.keys())[0] == video
            refs_by_video = _filter(filter_by_video, refs_by_activity)
            syss_by_video = _filter(filter_by_video, syss_by_activity)

            # Otherwise for each activity instance, ID starts at 1
            refs_by_video = _unify_object_ids(refs_by_video)
            syss_by_video = _unify_object_ids(syss_by_video)

            # Gathering objects
            refs = _objects(refs_by_video)
            syss = _objects(syss_by_video)

            # Sort predictions by decreasing score order.
            def _sort_objects(obj_list):
                # When presenceConf will be set per object and not bbox
                if getattr(obj_list[0], 'presenceConf', None) is not None:
                    return argsort(obj_list, 'presenceConf')[::-1]

                pc = []
                for obj in obj_list:
                    mean = 0
                    size = len(obj.localization.keys())
                    for frame in obj.localization:
                        try:
                            mean += obj.localization[frame].presenceConf
                        except TypeError:  # presenceConf is None for {}
                            size -= 1
                    pc.append(mean / size)
                sorted_pc = sorted(pc, reverse=True)
                sorted_idx = []

                while len(sorted_pc) > 0:
                    elt = sorted_pc.pop(0)
                    idx = pc.index(elt)
                    while idx in sorted_idx:
                        idx = pc[idx+1:].index(elt) + idx+1
                    sorted_idx.append(idx)
                return sorted_idx
            
            sorted_idx = _sort_objects(syss)
            predictions = [syss[idx] for idx in sorted_idx]

            npos = len(refs)
            if npos == 0:
                continue
            lock_gt = np.ones((len(thresholds), npos)) * -1

            # Initialize true positive and false positive vectors.
            tp = np.zeros((len(thresholds), len(predictions)))
            fp = np.zeros((len(thresholds), len(predictions)))

            for idx, this_pred in enumerate(predictions):
                this_gt = [r for r in refs if r.objectType == this_pred.objectType]
                siou_arr = [spatial_intersection_over_union(
                    ref, this_pred) for ref in this_gt]
                siou_sorted_idx = argsort(siou_arr)[::-1]
                for tidx, siou_thr in enumerate(thresholds):
                    for jdx in siou_sorted_idx:
                        if siou_arr[jdx] < siou_thr:
                            fp[tidx, idx] = 1
                            break
                        if lock_gt[tidx, jdx] >= 0:
                            continue
                        # Assign as true positive after the filters above.
                        tp[tidx, idx] = 1
                        lock_gt[tidx, jdx] = idx
                        break

                    if fp[tidx, idx] == 0 and tp[tidx, idx] == 0:
                        fp[tidx, idx] = 1

            tp_cumsum = np.cumsum(tp, axis=1).astype(float)
            fp_cumsum = np.cumsum(fp, axis=1).astype(float)
            recall_cumsum = tp_cumsum / npos
            precision_cumsum = tp_cumsum / (tp_cumsum + fp_cumsum)
            local_AP = []
            for tidx in range(len(thresholds)):
                if thresholds[tidx] == 0.5:
                    if list(precision_cumsum[tidx, :]) != []:
                        precision[activity] = precision_cumsum[tidx, :]
                    if list(recall_cumsum[tidx, :]) != []:
                        recall[activity] = recall_cumsum[tidx, :]
                # Not ap itself, we should happen it to files_AP
                # and then compute a mean
                local_AP.append(compute_ap(
                    precision_cumsum[tidx, :], recall_cumsum[tidx, :]))
            files_AP.append(local_AP)
        # Finally, filling ap
        for tidx in range(len(thresholds)):
            for file_AP in files_AP:
                ap[activity][tidx] += file_AP[tidx]
            ap[activity][tidx] /= len(files_AP)

    ap_len = len(ap)
    ap_metrics = {'AP': [], 'mAP': [], 'pr': (precision, recall)}
    mAP = {}
    for thd in thresholds:
        mAP[thd] = 0
    for activity in ap:
        for i in range(len(thresholds)):
            thd = thresholds[i]
            v = round(float(ap[activity][i]), 18)
            ap_metrics['AP'].append((activity, 'object-AP@%.2ftIoU' % thd, v))
            mAP[thd] += v
    for thd in mAP:
        ap_metrics['mAP'].append(('object-mAP@%.2ftIoU' % thd, mAP[thd]/ap_len))
    return ap_metrics
