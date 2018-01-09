from operator import add
from sparse_signal import SparseSignal as S

# Handles multi-file localizations
def _temporal_intersection(r, s):
    rl, sl = r.localization, s.localization
    return reduce(add, [ (S(rl[k]) & S(sl[k])).area() for k in set(rl.keys()) & set(sl.keys()) ], 0)

def _temporal_union(r, s):
    rl, sl = r.localization, s.localization
    return reduce(add, [ (S(rl.get(k, {})) | S(sl.get(k, {}))).area() for k in set(rl.keys()) | set(sl.keys()) ], 0)

# Returns true if there's some temporal intersection between the
# system and reference activity instances
def temporal_intersection_filter(r, s):
    return _temporal_intersection(r, s) > 0

# Intersection over union
def temporal_iou(r, s):
    intersection = _temporal_intersection(r, s)
    union = _temporal_union(r, s)

    # Not sure if this is the best way to handle union == 0; but in
    # practise should never encounter this case
    return float(intersection) / union if union != 0 else 0.0

