from munkres import Munkres, DISALLOWED, make_cost_matrix

# components is a list of (label, weight, function)
def build_linear_combination_kernel(filters, components, initial_similarity = 1):
    def _and(a, b):
        return a and b

    def _reducer(init, component_value):
        initial_similarity, component_values = init
        label, weight, value = component_value

        component_values[label] = value
        return(initial_similarity + weight * value, component_values)
    
    def _kernel(r_i, s_i):
        if reduce(_and, [ f(r_i, s_i) for f in filters ], True):
            return reduce(_reducer, [ (l, w, cf(r_i, s_i)) for l, w, cf in components ], (initial_similarity, {}))
        else:
            return (DISALLOWED, {})

    return _kernel

def perform_alignment(ref_instances, sys_instances, kernel, maximize = True):
    similarity_scores, component_scores = {}, {}

    # Need to keep track of which ref/sys nodes are entirely
    # Disallowed and omit them from the munkres computation, but still
    # need to include them in the mapping as unmapped ref/sys nodes
    ref_matchable, sys_matchable = {}, {}

    max_sim = 0
    for s_i, s in enumerate(sys_instances):
        for r_i, r in enumerate(ref_instances):
            sim, comp = kernel(r, s)
            similarity_scores[(s_i, r_i)] = sim
            component_scores[(s_i, r_i)] = comp
            
            if sim != DISALLOWED:
                ref_matchable[r_i] = True
                sys_matchable[s_i] = True
                if sim > max_sim: max_sim = sim

    sim_matrix, component_matrix = [], []
    for s_i, s in enumerate(sys_instances):
        if sys_matchable.get(s_i, False):
            sim_row = []
            comp_row = []
            for r_i, r in enumerate(ref_instances):
                if ref_matchable.get(r_i, False):
                    sim_row.append(similarity_scores[(s_i, r_i)])
                    comp_row.append(component_scores[(s_i, r_i)])
            sim_matrix.append(sim_row)
            component_matrix.append(comp_row)

    def _build_partition_reducer(matchability_lookup):
        def _partition_reducer(init, enum_elem):
            matchable, unmatchable = init
            i, e = enum_elem

            matchable.append(e) if matchability_lookup.get(i, False) else unmatchable.append(e)
            return(matchable, unmatchable)
        return _partition_reducer
    
    matchable_ref, unmatchable_ref = reduce(_build_partition_reducer(ref_matchable), enumerate(ref_instances), ([], []))
    matchable_sys, unmatchable_sys = reduce(_build_partition_reducer(sys_matchable), enumerate(sys_instances), ([], []))

    if maximize:
        def _inverter(sim):
            return DISALLOWED if sim == DISALLOWED else max_sim - sim
        
        matrix = make_cost_matrix(sim_matrix, _inverter)
    else:
        matrix = sim_matrix
        
    correct_detects, false_alarms, missed_detects = [], [], []
        
    unmapped_sys = set(range(0, len(matchable_sys)))
    unmapped_ref = set(range(0, len(matchable_ref)))
    if len(matrix) > 0:
        for s_i, r_i in Munkres().compute(matrix):
            unmapped_sys.remove(s_i)
            unmapped_ref.remove(r_i)
            correct_detects.append((matchable_ref[r_i], matchable_sys[s_i], sim_matrix[s_i][r_i], component_matrix[s_i][r_i]))

    for r_i in unmapped_ref:
        missed_detects.append((matchable_ref[r_i], None, None, None))
    for r in unmatchable_ref:
        missed_detects.append((r, None, None, None))
        
    for s_i in unmapped_sys:
        false_alarms.append((None, matchable_sys[s_i], None, None))
    for s in unmatchable_sys:
        false_alarms.append((None, s, None, None))

    return(correct_detects, missed_detects, false_alarms)
