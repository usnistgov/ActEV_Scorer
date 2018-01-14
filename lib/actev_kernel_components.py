from metrics import *

# Returns true if there's some temporal intersection between the
# system and reference activity instances
def temporal_intersection_filter(r, s):
    return temporal_intersection(r, s) > 0

