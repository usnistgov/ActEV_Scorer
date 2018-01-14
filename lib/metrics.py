from operator import add
from math import ceil
from sparse_signal import SparseSignal as S

def _signal_pairs(r, s, key_join_op = set.union):
    rl, sl = r.localization, s.localization
    return [ (S(rl.get(k, {})), S(sl.get(k, {}))) for k in key_join_op(set(rl.keys()), set(sl.keys())) ]

def temporal_intersection(r, s):
    return reduce(add, [ (r & s).area() for r, s in _signal_pairs(r, s, set.intersection) ], 0)

def temporal_union(r, s):
    return reduce(add, [ (r | s).area() for r, s in _signal_pairs(r, s) ], 0)        

def temporal_intersection_over_union(r, s):
    intersection = temporal_intersection(r, s)
    union = temporal_union(r, s)

    # Not sure if this is the best way to handle union == 0; but in
    # practise should never encounter this case
    return float(intersection) / union if union != 0 else 0.0

def _mide_core(r, s, ns_collar_size):
    ns_collar = r.generate_collar(ns_collar_size)
    c_r = r - ns_collar
    c_s = s - ns_collar

    return (c_r - c_s).area(), (c_s - c_r).area()
    
def mide(r, s, ns_collar_size, cost_fn_miss, cost_fn_fa):
    miss_area, fa_area = _mide_core(r, s, ns_collar_size)
    return cost_fn_miss(miss_area) + cost_fn_fa(fa_area)

# aligned_pairs should be a list of tuples being (reference, system);
# where reference and system are each ActivityInstance objects
def n_mide(aligned_pairs, ns_collar_size, cost_fn_miss, cost_fn_fa):
    def _sub_reducer(init, pair):
        init_miss, init_fa = init
        rs, ss = pair
        
        miss, fa = _mide_core(rs, ss, ns_collar_size)

        return (init_miss + miss, init_fa + fa)

    def _reducer(init, pair):
        r, s = pair
        miss, fa = reduce(_sub_reducer, _signal_pairs(r, s), (0, 0))

        return init + cost_fn_miss(miss) + cost_fn_fa(fa)

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

def p_miss_at_r_fa(c, m, f, fa_denominator, target_rfa, key_func = lambda x: x):
    num_allowed_f = int(ceil(target_rfa * fa_denominator))
    num_f = len(f)
    
    if num_f == 0 or num_allowed_f >= num_f:
        return p_miss(len(c), len(m), num_f)
    else:
        last_f_key = key_func(sorted(f, None, key_func, True)[num_allowed_f])
        num_filtered_c = len(filter(lambda x: key_func(x) > last_f_key, c))
        return p_miss(num_filtered_c, len(m) + (len(c) - num_filtered_c), num_f)
