from operator import add
from sparse_signal import SparseSignal as S

def _signal_pairs(r, s, key_join_op = set.union):
    rl, sl = r.localization, s.localization
    return [ (S(rl.get(k, {})), S(sl.get(k, {})), k) for k in key_join_op(set(rl.keys()), set(sl.keys())) ]

def temporal_intersection(r, s):
    return reduce(add, [ (r & s).area() for r, s, k in _signal_pairs(r, s, set.intersection) ], 0)

def temporal_union(r, s):
    return reduce(add, [ (r | s).area() for r, s, k in _signal_pairs(r, s) ], 0)        

def temporal_intersection_over_union(r, s):
    intersection = temporal_intersection(r, s)
    union = temporal_union(r, s)

    # Not sure if this is the best way to handle union == 0; but in
    # practise should never encounter this case
    return float(intersection) / union if union != 0 else 0.0

# aligned_pairs should be a list of tuples being (reference, system);
# where reference and system are each ActivityInstance objects
def n_mide(aligned_pairs, file_framedur_lookup, ns_collar_size, cost_fn_miss, cost_fn_fa):
    # Should consider another paramemter for for all files to consider
    # for FA denominator calculation, in the case of cross-file
    # activity instances
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
        miss, fa, miss_denom, fa_denom = reduce(_sub_reducer, _signal_pairs(r, s), (0, 0, 0, 0))

        return init + cost_fn_miss(float(miss) / miss_denom) + cost_fn_fa(float(fa) / fa_denom)

    num_aligned = len(aligned_pairs)

    if num_aligned == 0:
        return None
    else:
        return reduce(_reducer, aligned_pairs, 0.0) / num_aligned

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
