# default.py
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

import sys
import os

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
sys.path.append(lib_path)

from metrics import *
from alignment_record import *
from alignment import *
from helpers import *

class Default(object):
    @classmethod
    def get_schema_fn(cls):
        raise NotImplementedError

    @classmethod
    def requires_object_localization(cls):
        return False

    def __init__(self, scoring_parameters, file_index, activity_index, command):
        self.scoring_parameters = scoring_parameters
        self.file_index = file_index
        self.activity_index = activity_index
        self.default_activity_groups = [ (k,) for k in self.activity_index.viewkeys() ]

    # assumes syss, and refs are simple lists of activities
    def default_cohort_gen(self, refs, syss):
        yield (refs, syss)

    def compute_alignment(self,
                          system_activities,
                          reference_activities,
                          cohort_gen = None,
                          kernel_builder_func = None):
        if kernel_builder_func is None:
            kernel_builder_func = self.default_kernel_builder

        if cohort_gen is None:
            cohort_gen = self.default_cohort_gen

        # Kernel building happens in two phases, first configuring
        # based on the global list of reference and system activity
        # instances.  Then configured per-activity and activity
        # instances for both ref and sys
        kernel_builder = kernel_builder_func(reference_activities, system_activities)

        activity_getter = lambda x: x.activity
        ref_by_act = group_by_func(activity_getter, reference_activities)
        sys_by_act = group_by_func(activity_getter, system_activities)

        alignment_recs = []
        for activity, activity_properties in self.activity_index.iteritems():
            refs = ref_by_act.get(activity, [])
            syss = sys_by_act.get(activity, [])

            # Second phase of kernel building, taking into account the
            # activity
#            print "BEFORE KERNEL"
            kernel = kernel_builder(activity, activity_properties, refs, syss)
#            print "AFTER KERNEL"
            for rs, ss in cohort_gen(refs, syss):
#                print "BEFORE ALIGNMENT"
                c, m, f = perform_alignment(rs, ss, kernel)
#                print "AFTER ALIGNMENT"

                alignment_recs.extend(c)
                alignment_recs.extend(m)
                alignment_recs.extend(f)

        return alignment_recs

    def compute_measures(self, record, measures):
        return reduce(merge_dicts, [ m(record) for m in measures ], {})

    # Optional default_factorizations ensures the inclusion of the
    # specified factorizations in the output records, but if not
    # otherwise present in records, measures will be computed over an
    # empty list for the given factorization
    def compute_aggregate_measures(self, records, factorization_func, measures, default_factorizations = None):
        def _r(init, item):
            factorization, recs = item

            for mv in self.compute_measures(recs, measures).iteritems():
                init.append(factorization + mv)

            return init

        return reduce(_r, group_by_func(factorization_func, records, default_groups = default_factorizations).iteritems(), [])

    def compute_atomic_measures(self, records, rec_map_func, measures = None):
        if measures is None:
            measures = self.default_pair_measures()

        def _r(init, rec):
            for mv in self.compute_measures(rec, measures).iteritems():
                init.append(rec_map_func(rec) + mv)

            return init

        return reduce(_r, records, [])

    # This method assumes that the "metric_name" is the second-to-last
    # element, and that "metric_value" is the last element.  Should
    # consider refactoring, perhaps using namedtuples for metric
    # records would be better
    def compute_means(self, records, selected_measures = None):
        if selected_measures is None:
            filtered_records = records
        else:
            filtered_records = filter(lambda r: r[-2] in selected_measures, records)

        if selected_measures is None:
            return self.compute_aggregate_measures(filtered_records, lambda r: (r[-2],), [ lambda recs: mean_exclude_none(map(lambda r: r[-1], recs)) ])
        else:
            return self.compute_aggregate_measures(filtered_records, lambda r: (r[-2],), [ lambda recs: mean_exclude_none(map(lambda r: r[-1], recs)) ], [ (m,) for m in selected_measures ])


    def build_simple_measure(self, arg_func, name, measure_func):
        #        print arg_func
        #        print name
        #        print measure_func
        def _m(*rec):
            return { name: measure_func(*arg_func(*rec)) }

        return _m
