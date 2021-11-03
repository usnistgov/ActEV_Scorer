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
from functools import reduce
import dill
from concurrent.futures import ProcessPoolExecutor
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
sys.path.append(lib_path)

from operator import add

from metrics import *
from alignment_record import *
from actev_kernel_components import *
from sed_kernel_components import *
from alignment import *
from helpers import *
from srl_ad_v1 import *

class SRL_AOD_V1(SRL_AD_V1):
    @classmethod
    def get_schema_fn(cls):
        return "srl_aod_v1.json"

    @classmethod
    def requires_object_localization(cls):
        return True

    def __init__(self, scoring_parameters, file_index, activity_index, command):
        default_scoring_parameters = { "activityo.epsilon_temporal_congruence": 1.0e-8,
                                       "activity.epsilon_presenceconf_congruence": 1.0e-6,
                                       "activity.fa_at_rfa_targets":     [ 10, 5, 2, 1, 0.5, 0.2, 0.15, 0.1, 0.03, 0.01 ],
                                       "activity.temporal_overlap_delta": 0.2,
                                       "activity.p_miss_at_rfa_targets": [ 10, 5, 2, 1, 0.5, 0.2, 0.15, 0.1, 0.05, 0.02, 0.01 ],
                                       "activity.n_mide_at_rfa_targets": [ 10, 5, 2, 1, 0.5, 0.2, 0.15, 0.1, 0.05, 0.02, 0.01 ],
                                       "activity.epsilon_object_congruence": 1.0e-10,
                                       "activity.object_congruence_delta": 0.3,
                                       "activity.n_mode_at_rfa_targets": [ 10, 5, 2, 1, 0.5, 0.2, 0.15, 0.1, 0.05, 0.02, 0.01 ],
                                       "mode.cost_miss": 1,
                                       "mode.cost_fa": 1,
                                       "nmide.ns_collar_size": 0,
                                       "nmide.cost_miss": 1,
                                       "nmide.cost_fa": 1,
                                       "object.epsilon_object-overlap_congruence": 1.0e-8,
                                       "object.epsilon_presenceconf_congruence": 0,
                                       "object.spatial_overlap_delta": 0.2,
                                       "object.p_miss_at_rfa_targets": [ 0.5, 0.2, 0.1, 0.033 ],
                                       "wpmiss.numerator": 8,
                                       "wpmiss.denominator": 10,
                                       "scoring_protocol": "srl_aod_v1",
                                       "command": str(command),
                                       "git.commit": subprocess.check_output(["git", "--git-dir="+ os.path.join(lib_path, "../")+".git", "show", "--oneline", "-s", "--no-abbrev-commit","--pretty=format:%H--%aI"]).strip()}
        scoring_parameters = merge_dicts(default_scoring_parameters, scoring_parameters)
        super(SRL_AOD_V1, self).__init__(scoring_parameters, file_index, activity_index, command)

    def default_kernel_builder(self, refs, syss):
        act_presenceconf_congruence = build_sed_presenceconf_congruence(syss, minmax=self.minmax)
        simple_temporal_overlap_filter = build_temporal_overlap_filter(self.scoring_parameters["activity.temporal_overlap_delta"])

        def _r(init, sys):
            localization_vals = reduce(add, map(lambda x: list(x.localization.values()), sys.objects), [])
            init.extend(reduce(add, map(lambda x: list(x.values()), localization_vals), []))
            return init

        # Have to filter out empty ObjectLocalizationFrames here
        global_sys_obj_localizations = filter(lambda x: x.presenceConf is not None, reduce(_r, syss, []))

        obj_presenceconf_congruence = build_sed_presenceconf_congruence(global_sys_obj_localizations, minmax=self.minmax)
        simple_spatial_overlap_filter = build_simple_spatial_overlap_filter(self.scoring_parameters["object.spatial_overlap_delta"])

        mode_cost_miss = self.scoring_parameters["mode.cost_miss"]
        mode_costfn_miss = lambda x: mode_cost_miss * x

        mode_cost_fa = self.scoring_parameters["mode.cost_fa"]
        mode_costfn_fa = lambda x: mode_cost_fa * x

        def _configure_kernel_for_activity(activity, activity_properties, refs, syss):
            object_types = activity_properties.get("objectTypes", [])
            object_type_map = activity_properties.get("objectTypeMap", None)

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
                                                    build_object_congruence_filter(_object_kernel_builder,
                                                                                   intersection_filter,
                                                                                   intersection_filter,
                                                                                   self.scoring_parameters["activity.object_congruence_delta"],
                                                                                   object_types,
                                                                                   mode_costfn_miss,
                                                                                   mode_costfn_fa,
                                                                                   self.scoring_parameters["object.p_miss_at_rfa_targets"])],
                                                   [build_object_congruence(_object_kernel_builder,
                                                                            intersection_filter,
                                                                            intersection_filter,
                                                                            object_types,
                                                                            mode_costfn_miss,
                                                                            mode_costfn_fa,
                                                                            self.scoring_parameters["object.p_miss_at_rfa_targets"]),
                                                    temporal_intersection_over_union_component,
                                                    act_presenceconf_congruence],
                                                   {"temporal_intersection-over-union": self.scoring_parameters["activity.epsilon_temporal_congruence"],
                                                    "presenceconf_congruence": self.scoring_parameters["activity.epsilon_presenceconf_congruence"],
                                                    "object_congruence": self.scoring_parameters["activity.epsilon_object_congruence"]})

        return _configure_kernel_for_activity
    
    def build_nmode_measure(self):
        def _nmode(c, m, f):
            return n_mode(c)
        return _nmode

    # def compute_obj_det_points_and_measures(self, alignment, rfa_denom, uniq_conf, rfa_targets):
    #     sweeper = build_sweeper(lambda ar: ar.sys_presence_conf, [ build_rfa_metric(rfa_denom),
    #                                                                build_pmiss_metric(),
    #                                                                self.build_nmode_measure() ], uniq_conf)

    #     det_points = sweeper(alignment)

    #     pmiss_measures = get_points_along_confidence_curve(det_points,
    #                                                        "rfa",
    #                                                        lambda r: r["rfa"],
    #                                                        "p_miss",
    #                                                        lambda r: r["p_miss"],
    #                                                        rfa_targets)
    #     nmode_measures = get_points_along_confidence_curve(det_points,
    #                                                        "rfa",
    #                                                        lambda r: r["rfa"],
    #                                                        "n-mode",
    #                                                        lambda r: r["n-mode"],
    #                                                        self.scoring_parameters['activity.n_mode_at_rfa_targets'])

    #     return (flatten_sweeper_records(det_points, [ "rfa", "p_miss" ]), flatten_sweeper_records(det_points, [ "rfa", "p_miss", "n-mode" ]), merge_dicts(pmiss_measures, nmode_measures))

    # def compute_aggregate_obj_det_points_and_measures(self, records, factorization_func, rfa_denom_func, uniq_conf, rfa_targets, default_factorizations = None):
    #     # Build concat object alignment records
    #     def _concat_align_recs(init, ar):
    #         init.extend(map(lambda x: x[1], ar.kernel_components["alignment_records"]))
    #         return init

    #     def _r(init, item):
    #         p, fa, m = init
    #         factorization, recs = item
    #         f = {}
    #         combined_alignment_records = reduce(_concat_align_recs, recs, [])

    #         det_points, _, measures = self.compute_obj_det_points_and_measures(combined_alignment_records, rfa_denom_func(recs), uniq_conf, rfa_targets)
    #         _, fa_data, _ = self.compute_obj_det_points_and_measures(recs, rfa_denom_func(recs), uniq_conf, rfa_targets)

    #         p["-".join(factorization)] = det_points
    #         f["-".join(factorization)] = fa_data
            
    #         for k in f:
    #             for i in f[k]:
    #                 ii = i[0] if 'e' in str(i[0]) else round(i[0], 3)
    #                 fa.append((k, ii, "p_miss", i[2]))
    #                 fa.append((k, ii, "rfa", i[1]))
    #                 fa.append((k, ii, "n-mode", i[3]))

    #         for _m, v in measures.items():
    #             m.append(factorization + ("object-{}".format(_m), v))

    #         return (p, fa, m)

    #     grouped = group_by_func(factorization_func, records, default_groups = default_factorizations)
    #     _r_srlz = dill.dumps(_r)
    #     args = []
    #     for key in grouped:
    #         args.append((_r_srlz, (key, grouped[key]), ({}, [], [])))
    
    #     with ProcessPoolExecutor(self.pn) as pool:
    #         res = pool.map(unserialize_fct_res, args)

    #     p, fa, m = {}, [], []
    #     for entry in res:
    #         p.update(entry[0])
    #         fa.extend(entry[1])
    #         m.extend(entry[2])
    #     return (p, fa, m)

    # def compute_results_with_obj(self, alignment, uniq_conf):
    #     c, m, f = partition_alignment(alignment)

    #     # Building off of the metrics computed for AD
    #     ad_results = super(SRL_AOD_V1, self).compute_results(alignment, uniq_conf)

    #     def _object_frame_alignment_records(init, kv):
    #         activity, recs = kv
    #         object_type_map = self.activity_index[activity].get("objectTypeMap", {})

    #         def _m(item):
    #             def _subm(frame_ar):
    #                 frame, ar = frame_ar
    #                 ref_object_type = ar.ref.objectType if ar.ref is not None else None
    #                 sys_object_type = ar.sys.objectType if ar.sys is not None else None
    #                 mapped_type = object_type_map.get(ref_object_type if ref_object_type is not None else sys_object_type,
    #                                                   ref_object_type if ref_object_type is not None else sys_object_type)
    #                 return list(map(str, [activity,
    #                                  item.ref,
    #                                  item.sys,
    #                                  frame,
    #                                  ref_object_type,
    #                                  sys_object_type,
    #                                  object_type_map.get(ref_object_type, ref_object_type) if ref_object_type is not None else None,
    #                                  object_type_map.get(sys_object_type, sys_object_type) if sys_object_type is not None else None])) + [ x for x in ar.iter_with_extended_properties(["spatial_intersection-over-union", "presenceconf_congruence"]) ]

    #             return list(map(_subm, item.kernel_components.get("alignment_records", [])))

    #         for entry in map(_m, filter(lambda r: r.alignment == "CD", recs)):
    #             init.extend(entry)
    #         return init

    #     grouped = group_by_func(lambda rec: rec.activity, alignment).items()
    #     object_frame_alignment_records = reduce(_object_frame_alignment_records, grouped, [])

    #     def _obj_pmiss_at_rfa(targ):
    #         t = "object-p_miss@{}rfa".format(targ)
    #         return self.build_simple_measure(lambda x: (x.kernel_components.get(t),), t, identity)

    #     aod_pair_measures = [ self.build_simple_measure(lambda x: (x.kernel_components.get("minMODE"),), "minMODE", identity)] + list(map(_obj_pmiss_at_rfa, self.scoring_parameters["object.p_miss_at_rfa_targets"]))

    #     def _pair_properties_map(rec):
    #         return (rec.activity, rec.ref.activityID, rec.sys.activityID)

    #     aod_pair_results = self.compute_atomic_measures(c, _pair_properties_map, aod_pair_measures)

    #     def _activity_grouper(rec):
    #         return (rec.activity,)

    #     def _empty_grouper(rec):
    #         return tuple() # empty tuple

    #     def _rfa_denom_fn(correct_recs):
    #         def _localization_reducer(init, loc):
    #             # Merges the two temporal localization dictionaries by
    #             # "adding" the signals
    #             return merge_dicts(init, loc, add)
    #         return sum([ v.area() for v in reduce(_localization_reducer, map(lambda x: x.kernel_components["ref_filter_localization"], correct_recs), {}).values() ])

    #     activity_obj_det_points, fa_data, activity_obj_det_measures = self.compute_aggregate_obj_det_points_and_measures(c, _activity_grouper, _rfa_denom_fn, uniq_conf, self.scoring_parameters["object.p_miss_at_rfa_targets"], self.default_activity_groups)

    #     def _pair_metric_means(init, res):
    #         a, ress = res

    #         for r in self.compute_record_means(ress, map(lambda targ: "object-p_miss@{}rfa".format(targ), self.scoring_parameters["object.p_miss_at_rfa_targets"])):
    #             label, val = r

    #             # Explicitly setting mean object-p_miss@rfa to be 1.0
    #             # rather than None in the case where no activity
    #             # instances were detected for a given activity. TODO
    #             # find a cleaner way to incorporate this
    #             init.extend([ (a, label, 1.0 if val is None else val) ])

    #         return init

    #     obj_activity_means = reduce(_pair_metric_means, group_by_func(lambda t: t[0], aod_pair_results, default_groups = self.activity_index.keys()).items(), [])

    #     agg_obj_det_points, agg_fa_data, agg_obj_det_measures = self.compute_aggregate_obj_det_points_and_measures(c, _empty_grouper, _rfa_denom_fn, uniq_conf, self.scoring_parameters["object.p_miss_at_rfa_targets"], [ tuple() ])

    #     agg_obj_activity_means = self.compute_record_means(obj_activity_means)

    #     agg_obj_means = self.compute_record_means(activity_obj_det_measures)

    #     appended_results = merge_dicts(ad_results, {"scores_by_activity": activity_obj_det_measures + obj_activity_means,
    #                                                 "pair_metrics": aod_pair_results,
    #                                                 "object_frame_alignment_records": object_frame_alignment_records,
    #                                                 "scores_aggregated": agg_obj_det_measures + agg_obj_activity_means + agg_obj_means,
    #                                                 "scores_by_activity_and_threshold": fa_data}, add)

    #     def _align_rec_mapper(rec):
    #         return (rec.activity,) + tuple(rec.iter_with_extended_properties([ "temporal_intersection-over-union", "presenceconf_congruence", "object_congruence" ]))

    #     output_alignment_records = map(_align_rec_mapper, alignment)

    #     # Replacement results for AOD
    #     return merge_dicts(appended_results, {"output_alignment_records": output_alignment_records})


    def compute_aod_det_points_and_measures(self, alignment, rfa_denom, uniq_conf, rfa_targets, nmide_targets, wpmiss_denom, wpmiss_numer):
        sweeper = build_sweeper(lambda ar: ar.sys_presence_conf, [ build_rfa_metric(rfa_denom),
                                                                   build_pmiss_metric(),
                                                                   build_wpmiss_metric(wpmiss_denom, wpmiss_numer),
                                                                   self.build_nmide_measure(),
                                                                   self.build_nmode_measure()], uniq_conf)

        det_points = sweeper(alignment)

        pmiss_measures = get_points_along_confidence_curve(det_points,
                                                           "rfa",
                                                           lambda r: r["rfa"],
                                                           "p_miss",
                                                           lambda r: r["p_miss"],
                                                           rfa_targets)
        
        wpmiss_measures = get_points_along_confidence_curve(det_points,
                                                            "rfa",
                                                            lambda r: r["rfa"],
                                                            "w_p_miss",
                                                            lambda r: r["w_p_miss"],
                                                            rfa_targets)

        nmide_measures = get_points_along_confidence_curve(det_points,
                                                           "rfa",
                                                           lambda r: r["rfa"],
                                                           "n-mide",
                                                           lambda r: r["n-mide"],
                                                           nmide_targets,
                                                           None)

        nmode_measures = get_points_along_confidence_curve(det_points,
                                                           "rfa",
                                                           lambda r: r["rfa"],
                                                           "n-mode",
                                                           lambda r: r["n-mode"],
                                                           rfa_targets,
                                                           None)

        return (flatten_sweeper_records(det_points, [ "rfa", "p_miss", "n-mode" ]),
                merge_dicts(pmiss_measures, merge_dicts(nmide_measures, merge_dicts(wpmiss_measures, nmode_measures))))

    def compute_aggregate_aod_det_points_and_measures(self, records, factorization_func, rfa_denom_func, uniq_conf, rfa_targets, nmide_targets, default_factorizations = []):
        def _r(init, item):
            p, m = init
            factorization, recs = item

            det_points, measures = self.compute_aod_det_points_and_measures(recs, rfa_denom_func(recs), uniq_conf, rfa_targets, nmide_targets, self.scoring_parameters["wpmiss.denominator"], self.scoring_parameters["wpmiss.numerator"])
            
            p["-".join(factorization)] = det_points

            for _m, v in measures.items():
                m.append(factorization + (_m, v))

            return (p, m)

        grouped = merge_dicts({ k: [] for k in default_factorizations }, group_by_func(factorization_func, records))
        _r_srlz = dill.dumps(_r)
        args = []
        for key in grouped:
            args.append((_r_srlz, (key, grouped[key]), ({}, [])))

        with ProcessPoolExecutor(self.pn) as pool:
            res = pool.map(unserialize_fct_res, args)

        p, m = {}, []
        for entry in res:
            p.update(entry[0])
            m.extend(entry[1])
        return (p, m)
    

    def compute_results(self, alignment, uniq_conf):
        c, m, f = partition_alignment(alignment)

        ar_nmide_measure = self.build_ar_nmide_measure()

        def _pair_arg_map(rec):
            return (rec.ref, rec.sys)

        pair_measures = [ self.build_simple_measure(_pair_arg_map, "temporal_intersection", temporal_intersection),
                          self.build_simple_measure(_pair_arg_map, "temporal_union", temporal_union),
                          self.build_simple_measure(_pair_arg_map, "temporal_fa", temporal_fa),
                          self.build_simple_measure(_pair_arg_map, "temporal_miss", temporal_miss),
                          self.build_simple_measure(lambda x: (x.kernel_components.get("temporal_intersection-over-union"),), "temporal_intersection-over-union", identity),
                          self.build_simple_measure(lambda x: (x.kernel_components.get("minMODE"),), "minMODE", identity) ]

        # Pairs from the alignments
        def _pair_properties_map(rec):
            return (rec.activity, rec.ref.activityID, rec.sys.activityID)

        pair_results = self.compute_atomic_measures(c, _pair_properties_map, pair_measures)
        
        # Activity level + Pair Aggregates
        def _activity_grouper(rec):
            return (rec.activity,)

        activity_nmides = self.compute_aggregate_measures(alignment, _activity_grouper, [ ar_nmide_measure ], self.default_activity_groups)
        out_det_points, det_measures = self.compute_aggregate_aod_det_points_and_measures(alignment, _activity_grouper, lambda x: self.total_file_duration_minutes, uniq_conf, self.scoring_parameters["activity.p_miss_at_rfa_targets"], self.scoring_parameters["activity.n_mide_at_rfa_targets"], self.default_activity_groups)

        # Overall level + Activity Aggregates + Pair Agg. Aggregates
        def _empty_grouper(rec):
            return tuple() # empty tuple

        activity_results = activity_nmides + det_measures

        overall_nmide = self.compute_aggregate_measures(alignment, _empty_grouper, [ ar_nmide_measure ])
        activity_means = self.compute_record_means(activity_results)

        def _align_rec_mapper(rec):
            return (rec.activity,) + tuple(rec.iter_with_extended_properties(["temporal_intersection-over-union", "presenceconf_congruence", "object_congruence", "minMODE"]))

        output_alignment_records = map(_align_rec_mapper, alignment)

        output_thresh = []
        for activity in out_det_points:
            for thd, rfa, pmiss, nmode in out_det_points[activity]:
                output_thresh.append((activity, thd, 'rfa', rfa))
                output_thresh.append((activity, thd, 'p_miss', pmiss))
                output_thresh.append((activity, thd, 'n-mode', nmode))

        return { "pair_metrics": pair_results,
                 "scores_by_activity": activity_results,
                 "scores_aggregated": activity_means + overall_nmide,
                 "det_point_records": out_det_points,
                 "output_alignment_records": output_alignment_records,
                 "scores_by_activity_and_threshold": output_thresh }
