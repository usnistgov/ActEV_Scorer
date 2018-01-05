from munkres import Munkres, DISALLOWED, make_cost_matrix, UnsolvableMatrix
from munkres import print_matrix

import pprint

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

    disallowed = {}

    max_sim = 0
    for s_i, s in enumerate(sys_instances):
        for r_i, r in enumerate(ref_instances):
            sim, comp = kernel(r, s)

            similarity_scores[(s_i, r_i)] = sim
            component_scores[(s_i, r_i)] = comp

            if sim == DISALLOWED:
                disallowed[(s_i, r_i)] = True
            else:
                if sim > max_sim: max_sim = sim

    sim_matrix, component_matrix = [], []
    for s_i, s in enumerate(sys_instances):
        sim_row = []
        comp_row = []
        for r_i, r in enumerate(ref_instances):
            sim_row.append(similarity_scores[(s_i, r_i)])
            comp_row.append(component_scores[(s_i, r_i)])
        sim_matrix.append(sim_row)
        component_matrix.append(comp_row)
    
    if maximize:
        def _mapper(sim):
            return max_sim + 1 if sim == DISALLOWED else (max_sim + 1) - sim
    else:
        def _mapper(sim):
            return max_sim + 1 if sim == DISALLOWED else sim


    matrix = make_cost_matrix(sim_matrix, _mapper)
    
    correct_detects, false_alarms, missed_detects = [], [], []
    # print_matrix(matrix)
    unmapped_sys = set(range(0, len(sys_instances)))
    unmapped_ref = set(range(0, len(ref_instances)))
    if len(matrix) > 0:
        for s_i, r_i in Munkres().compute(matrix):
            if disallowed.get((s_i, r_i), False):
                continue
                
            unmapped_sys.remove(s_i)
            unmapped_ref.remove(r_i)
            correct_detects.append((ref_instances[r_i], sys_instances[s_i], sim_matrix[s_i][r_i], component_matrix[s_i][r_i]))

    for r_i in unmapped_ref:
        missed_detects.append((ref_instances[r_i], None, None, None))
        
    for s_i in unmapped_sys:
        false_alarms.append((None, sys_instances[s_i], None, None))

    return(correct_detects, missed_detects, false_alarms)
