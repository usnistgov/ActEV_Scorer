# alignment.py
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

from munkres import Munkres, DISALLOWED, make_cost_matrix, UnsolvableMatrix
from operator import and_

from alignment_record import AlignmentRecord
from helpers import *

# components is a list of (label, weight, function)
def build_linear_combination_kernel(filters, components, weights, initial_similarity = 1):
    def _kernel(r_i, s_i):
        def _filter_reducer(init, f):
            ok, cache = init
            f_ok, f_cache = f(r_i, s_i)
            cache.update(f_cache)
            return (ok and f_ok, cache)

        ok, cache = reduce(_filter_reducer, filters, (True, {}))
        if ok:
            component_values = reduce(merge_dicts, [ cf(r_i, s_i, cache) for cf in components ], {})

            def _r(init, key_weight):
                key, weight = key_weight
                return init + weight * component_values.get(key, 0)

            sim = reduce(_r, weights.iteritems(), initial_similarity)

            return (sim, component_values)
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
    unmapped_sys = set(range(0, len(sys_instances)))
    unmapped_ref = set(range(0, len(ref_instances)))
    if len(matrix) > 0:
        for s_i, r_i in Munkres().compute(matrix):
            if disallowed.get((s_i, r_i), False):
                continue

            unmapped_sys.remove(s_i)
            unmapped_ref.remove(r_i)
            correct_detects.append(AlignmentRecord(ref_instances[r_i], sys_instances[s_i], sim_matrix[s_i][r_i], component_matrix[s_i][r_i]))

    for r_i in unmapped_ref:
        missed_detects.append(AlignmentRecord(ref_instances[r_i], None, None, None))

    for s_i in unmapped_sys:
        false_alarms.append(AlignmentRecord(None, sys_instances[s_i], None, None))

    return(correct_detects, missed_detects, false_alarms)
