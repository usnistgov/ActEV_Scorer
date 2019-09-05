# actev18_aod.py
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
import subprocess
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
sys.path.append(lib_path)

from operator import add

from metrics import *
from alignment_record import *
from actev_kernel_components import *
from sed_kernel_components import *
from alignment import *
from helpers import *
from actev18_ad import *

class ActEV18_AODT(ActEV18_AD):
    @classmethod
    def get_schema_fn(cls):
        return "actev18_aod_schema.json"

    @classmethod
    def requires_object_localization(cls):
        return True

    def __init__(self, scoring_parameters, file_index, activity_index, command):
        default_scoring_parameters = { "activity.epsilon_temporal_congruence": 1.0e-8,
                                       "activity.epsilon_presenceconf_congruence": 1.0e-6,
                                       "activity.temporal_overlap_delta": 0.2,
                                       "activity.p_miss_at_rfa_targets": [ 1, 0.2, 0.15, 0.1, 0.03, 0.01 ],
                                       "activity.n_mide_at_rfa_targets": [ 1, 0.2, 0.15, 0.1, 0.03, 0.01 ],
                                       "nmide.ns_collar_size": 0,
                                       "nmide.cost_miss": 1,
                                       "nmide.cost_fa": 1,
                                       "wpmiss.numerator": 8,
                                       "wpmiss.denominator": 10,
                                       "activity.epsilon_object_congruence": 1.0e-10,
                                       "activity.epsilon_object_tracking_congruence": 1.0e-6, 
                                       "activity.object_congruence_delta": 0.0,
                                       "object.epsilon_object-overlap_congruence": 1.0e-8,
                                       "object.epsilon_presenceconf_congruence": 1.0e-6,
                                       "object.spatial_overlap_delta": 0.5,
                                       "object.p_miss_at_rfa_targets": [ 0.5, 0.2, 0.1, 0.033 ],
                                       "mode.cost_miss": 1,
                                       "mode.cost_fa": 1,
                                       "mode.cost_id": 1,
                                       "command": str(command),
                                       "git.commit": subprocess.check_output(["git", "show", "--oneline", "-s", "--no-abbrev-commit","--pretty=format:%H--%aI"]).strip()}

        scoring_parameters = merge_dicts(default_scoring_parameters, scoring_parameters)

        super(ActEV18_AODT, self).__init__(scoring_parameters, file_index, activity_index, command)

    def default_kernel_builder(self, refs, syss):

        act_presenceconf_congruence = build_sed_presenceconf_congruence(syss)
        simple_temporal_overlap_filter = build_temporal_overlap_filter(self.scoring_parameters["activity.temporal_overlap_delta"])

        def _r(init, sys):
            localization_vals = reduce(add, map(lambda x: x.localization.values(), sys.objects), [])
            init.extend(reduce(add, map(lambda x: x.values(), localization_vals), []))

            return init

        # Have to filter out empty ObjectLocalizationFrames here
        global_sys_obj_localizations = filter(lambda x: x.presenceConf is not None, reduce(_r, syss, []))

        obj_presenceconf_congruence = build_sed_presenceconf_congruence(global_sys_obj_localizations)
        simple_spatial_overlap_filter = build_simple_spatial_overlap_filter(self.scoring_parameters["object.spatial_overlap_delta"])

        mode_cost_miss = self.scoring_parameters["mode.cost_miss"]
        mode_costfn_miss = lambda x: mode_cost_miss * x

        mode_cost_fa = self.scoring_parameters["mode.cost_fa"]
        mode_costfn_fa = lambda x: mode_cost_fa * x

        mode_cost_id = self.scoring_parameters["mode.cost_id"]
        mode_costfn_id = lambda x: mode_cost_id * x

        def _configure_kernel_for_activity(activity, activity_properties, refs, syss):
            object_types = activity_properties.get("objectTypes", [])
            object_type_map = activity_properties.get("objectTypeMap", None)
            #            print "object_type_map: "
            #            print object_type_map
            if object_type_map is None:
                object_type_filter = object_type_match_filter
            else:
                object_type_equiv_class = merge_dicts({ o: o for o in object_types }, object_type_map)
                object_type_filter = build_equiv_class_type_match_filter(object_type_equiv_class)

            def _object_kernel_builder(sys_objs):
                return build_linear_combination_kernel([object_type_filter,
                                                        simple_spatial_overlap_filter],
                                                       [simple_spatial_intersection_over_union_component,
                                                        obj_presenceconf_congruence],
                                                       {"spatial_intersection-over-union": self.scoring_parameters["object.epsilon_object-overlap_congruence"],
                                                        "presenceconf_congruence": self.scoring_parameters["object.epsilon_presenceconf_congruence"]})

            return build_linear_combination_kernel([simple_temporal_overlap_filter,
                                                    build_object_tracking_congruence_filter(_object_kernel_builder,
                                                                                   intersection_filter,
                                                                                   intersection_filter,
                                                                                   self.scoring_parameters["activity.object_congruence_delta"],
                                                                                   object_types,
                                                                                   mode_costfn_miss,
                                                                                   mode_costfn_fa,
                                                                                   mode_costfn_id,
                                                                                   self.scoring_parameters["object.p_miss_at_rfa_targets"])],
                                                   [build_object_tracking_congruence(_object_kernel_builder,
                                                                            intersection_filter,
                                                                            intersection_filter,
                                                                            object_types,
                                                                            mode_costfn_miss,
                                                                            mode_costfn_fa,
                                                                            mode_costfn_id,
                                                                            self.scoring_parameters["object.p_miss_at_rfa_targets"]),
                                                    temporal_intersection_over_union_component,
                                                    act_presenceconf_congruence],
                                                   {"temporal_intersection-over-union": self.scoring_parameters["activity.epsilon_temporal_congruence"],
                                                    "presenceconf_congruence": self.scoring_parameters["activity.epsilon_presenceconf_congruence"],
                                                    "object_tracking_congruence": self.scoring_parameters["activity.epsilon_object_tracking_congruence"]})

        return _configure_kernel_for_activity

    def compute_obj_det_points_and_measures(self, alignment, rfa_denom, uniq_conf, rfa_targets):
        sweeper = build_sweeper(lambda ar: ar.sys_presence_conf, [ build_rfa_metric(rfa_denom),
                                                                   build_pmiss_metric() ], uniq_conf)

        det_points = sweeper(alignment)

        pmiss_measures = get_points_along_confidence_curve(det_points,
                                                           "rfa",
                                                           lambda r: r["rfa"],
                                                           "p_miss",
                                                           lambda r: r["p_miss"],
                                                           rfa_targets)

        return (flatten_sweeper_records(det_points, [ "rfa", "p_miss" ]), pmiss_measures)

    def compute_aggregate_obj_det_points_and_measures(self, records, factorization_func, rfa_denom_func, uniq_conf, rfa_targets, default_factorizations = None):
        # Build concat object alignment records
        def _concat_align_recs(init, ar):
            init.extend(map(lambda x: x[1], ar.kernel_components["alignment_records"]))
            return init

        def _r(init, item):
            p, m = init
            factorization, recs = item

            combined_alignment_records = reduce(_concat_align_recs, recs, [])

            det_points, measures = self.compute_obj_det_points_and_measures(combined_alignment_records, rfa_denom_func(recs), uniq_conf, rfa_targets)

            p["-".join(factorization)] = det_points

            for _m, v in measures.iteritems():
                m.append(factorization + ("object-{}".format(_m), v))

            return (p, m)

        return reduce(_r, group_by_func(factorization_func, records, default_groups = default_factorizations).iteritems(), ({}, []))

    def compute_results(self, alignment, uniq_conf):
        c, m, f = partition_alignment(alignment)

        # Building off of the metrics computed for AD
        ad_results = super(ActEV18_AODT, self).compute_results(alignment, uniq_conf)
        #print ad_results
        def _object_frame_alignment_records(init, kv):
            activity, recs = kv
            object_type_map = self.activity_index[activity].get("objectTypeMap", {})

            def _m(item):
                def _subm(frame_ar):
                    frame, ar = frame_ar
                    ref_object_type = ar.ref.objectType if ar.ref is not None else None
                    sys_object_type = ar.sys.objectType if ar.sys is not None else None
                    mapped_type = object_type_map.get(ref_object_type if ref_object_type is not None else sys_object_type,
                                                      ref_object_type if ref_object_type is not None else sys_object_type)
                    return map(str, [activity,
                                     item.ref,
                                     item.sys,
                                     frame,
                                     ref_object_type,
                                     sys_object_type,
                                     object_type_map.get(ref_object_type, ref_object_type) if ref_object_type is not None else None,
                                     object_type_map.get(sys_object_type, sys_object_type) if sys_object_type is not None else None]) + [ x for x in ar.iter_with_extended_properties(["spatial_intersection-over-union", "presenceconf_congruence"]) ]

                return map(_subm, item.kernel_components.get("alignment_records", []))

            init.extend(reduce(add, map(_m, filter(lambda r: r.alignment == "CD", recs)), []))
            return init

        object_frame_alignment_records = reduce(_object_frame_alignment_records, group_by_func(lambda rec: rec.activity, alignment).iteritems(), [])

        def _obj_pmiss_at_rfa(targ):
            t = "object-p_miss@{}rfa".format(targ)
            return self.build_simple_measure(lambda x: (x.kernel_components.get(t),), t, identity)
        
        aod_pair_measures = [ self.build_simple_measure(lambda x: (x.kernel_components.get("minMOTE"),), "minMOTE", identity)] + [ self.build_simple_measure(lambda x: (x.kernel_components.get("minMODE"),), "minMODE", identity)] + map(_obj_pmiss_at_rfa, self.scoring_parameters["object.p_miss_at_rfa_targets"])
        #print "aod_pair_measures"
        #print aod_pair_measures
        def _pair_properties_map(rec):
            return (rec.activity, rec.ref.activityID, rec.sys.activityID)

        aod_pair_results = self.compute_atomic_measures(c, _pair_properties_map, aod_pair_measures)
        #print "aod_pair_results"
        #print aod_pair_results
        def _activity_grouper(rec):
            return (rec.activity,)

        def _empty_grouper(rec):
            return tuple() # empty tuple

        def _rfa_denom_fn(correct_recs):
            def _localization_reducer(init, loc):
                # Merges the two temporal localization dictionaries by
                # "adding" the signals
                return merge_dicts(init, loc, add)
            #print correct_recs
#       build_simple_measure     print [lambda x: x.kernel_components["ref_filter_localization"], correct_recs]
#            print reduce(_localization_reducer, map(lambda x: x.kernel_components["ref_filter_localization"], correct_recs), {})
#            print reduce(_localization_reducer, map(lambda x: x.kernel_components["ref_filter_localization"], correct_recs), {}).values()
#            print [v.area() for v in reduce(_localization_reducer, map(lambda x: x.kernel_components["ref_filter_localization"], correct_recs), {}).values() ]
            return sum([ v.area() for v in reduce(_localization_reducer, map(lambda x: x.kernel_components["ref_filter_localization"], correct_recs), {}).values() ])

        activity_obj_det_points, activity_obj_det_measures = self.compute_aggregate_obj_det_points_and_measures(c, _activity_grouper, _rfa_denom_fn, uniq_conf, self.scoring_parameters["object.p_miss_at_rfa_targets"], self.default_activity_groups)

        def _pair_metric_means(init, res):
            a, ress = res

            for r in self.compute_record_means(ress, map(lambda targ: "object-p_miss@{}rfa".format(targ), self.scoring_parameters["object.p_miss_at_rfa_targets"])):
                label, val = r

                # Explicitly setting mean object-p_miss@rfa to be 1.0
                # rather than None in the case where no activity
                # instances were detected for a given activity. TODO
                # find a cleaner way to incorporate this
                init.extend([ (a, label, 1.0 if val is None else val) ])

            return init

        obj_activity_means = reduce(_pair_metric_means, group_by_func(lambda t: t[0], aod_pair_results, default_groups = self.activity_index.keys()).iteritems(), [])

        agg_obj_det_points, agg_obj_det_measures = self.compute_aggregate_obj_det_points_and_measures(c, _empty_grouper, _rfa_denom_fn, uniq_conf, self.scoring_parameters["object.p_miss_at_rfa_targets"], [ tuple() ])

        agg_obj_activity_means = self.compute_record_means(obj_activity_means)

        agg_obj_means = self.compute_record_means(activity_obj_det_measures)

        appended_results = merge_dicts(ad_results, { "scores_by_activity": activity_obj_det_measures + obj_activity_means,
                                                     "pair_metrics": aod_pair_results,
                                                     "object_frame_alignment_records": object_frame_alignment_records,
                                                     "scores_aggregated": agg_obj_det_measures + agg_obj_activity_means + agg_obj_means }, add)

        def _align_rec_mapper(rec):
            return (rec.activity,) + tuple(rec.iter_with_extended_properties([ "temporal_intersection-over-union", "presenceconf_congruence", "object_congruence" ]))

        output_alignment_records = map(_align_rec_mapper, alignment)

        # Replacement results for AODT
        return merge_dicts(appended_results, { "output_alignment_records": output_alignment_records })
