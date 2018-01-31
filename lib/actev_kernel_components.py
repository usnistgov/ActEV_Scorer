from metrics import *

# Returns true if there's some temporal intersection between the
# system and reference activity instances
def temporal_intersection_filter(r, s):
    return temporal_intersection(r, s) > 0

def build_temporal_overlap_filter(threshold):
    def _filter(r, s):
        return temporal_intersection_over_union(r, s) > threshold

    return _filter
