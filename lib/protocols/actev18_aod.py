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

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
sys.path.append(lib_path)

from operator import add

from metrics import *
from alignment_record import *
from actev_kernel_components import *
from sed_kernel_components import *
from alignment import *
from helpers import *

class ActEV18_AOD():
    @classmethod
    def get_schema_fn(cls):
        return "actev18_aod_schema.json"

    def __init__(self):
        self.default_scoring_parameters = { "epsilon_temporal_congruence": 1.0e-8,
                                            "epsilon_activity_presenceconf_congruence": 1.0e-6,
                                            "epsilon_object_congruence": 1.0e-10,
                                            "epsilon_object-overlap_congruence": 1.0e-8,
                                            "epsilon_object_presenceconf_congruence": 1.0e-6,
                                            "temporal_overlap_delta": 0.2,
                                            "spatial_overlap_delta": 0.5,
                                            "object_congruence_delta": 0.0,
                                            "nmide_ns_collar_size": 0 }

        self.output_kernel_components = [ "temporal_intersection-over-union",
                                          "presenceconf_congruence",
                                          "object_congruence" ]

        self.output_object_kernel_components = [ "spatial_intersection-over-union",
                                                 "presenceconf_congruence" ]

    def build_kernel(self,
                     system_instances,
                     reference_instances,
                     scoring_parameters):

        def _object_kernel_builder(sys_objs):
            return build_linear_combination_kernel([object_type_match_filter,
                                                    build_simple_spatial_overlap_filter(scoring_parameters["spatial_overlap_delta"])],
                                                   [simple_spatial_intersection_over_union_component,
                                                    build_sed_presenceconf_congruence(sys_objs)],
                                                   {"spatial_intersection-over-union": scoring_parameters["epsilon_object-overlap_congruence"],
                                                    "presenceconf_congruence": scoring_parameters["epsilon_object_presenceconf_congruence"]})

        return build_linear_combination_kernel([build_temporal_overlap_filter(scoring_parameters["temporal_overlap_delta"]),
                                                build_object_congruence_filter(_object_kernel_builder, intersection_filter, intersection_filter, scoring_parameters["object_congruence_delta"])],
                                               [build_object_congruence(_object_kernel_builder, intersection_filter, intersection_filter),
                                                temporal_intersection_over_union_component,
                                                build_sed_presenceconf_congruence(system_instances)],
                                               {"temporal_intersection-over-union": scoring_parameters["epsilon_temporal_congruence"],
                                                "presenceconf_congruence": scoring_parameters["epsilon_activity_presenceconf_congruence"],
                                                "object_congruence": scoring_parameters["epsilon_object_congruence"]})

    def build_metrics(self,
                      scoring_parameters,
                      system_activities,
                      reference_activities,
                      activity_index,
                      file_index):
        # TODO: remove non-selected area from reference and system
        # instances, truncation or ?
        file_framedur_lookup = { k: S({ int(_k): _v for _k, _v in v["selected"].iteritems() }).area() for k, v in file_index.iteritems() }
        total_file_duration_minutes = sum([ float(frames) / file_index[k]["framerate"] for k, frames in file_framedur_lookup.iteritems()]) / float(60)

        rfa_func = self._build_rfa(total_file_duration_minutes)
        def det_point_function(decision_score, num_c, num_m, num_f):
            return (decision_score, rfa_func(num_c, num_m, num_f), p_miss(num_c, num_m, num_f))

        alignment_metrics = { "n-mide": self._build_nmide(file_framedur_lookup, scoring_parameters["nmide_ns_collar_size"]),
                              "n-mide_num_rejected": self._build_nmide_count_rejects(scoring_parameters["nmide_ns_collar_size"])}

        object_target_rfas = [ 0.5, 0.2, 0.1, 0.033 ]

        def alignment_metrics_plus(c, m, f):
            # Build concat object alignment records
            def _concat_align_recs(init, ar):
                init.extend(map(lambda x: x[1], ar.kernel_components["alignment_records"]))
                return init

            combined_alignment_records = reduce(_concat_align_recs, c, [])

            def _localization_reducer(init, loc):
                # Merges the two temporal localization dictionaries by
                # "adding" the signals
                return merge_dicts(init, loc, add)

            ref_filter_area = sum([ v.area() for v in reduce(_localization_reducer, map(lambda x: x.kernel_components["ref_filter_localization"], c), {}).values() ])

            obj_c, obj_m, obj_f = reduce(alignment_partitioner, combined_alignment_records, ([], [], []))
            num_obj_c, num_obj_m, num_obj_f = len(obj_c), len(obj_m), len(obj_f)

            def _sweep_reducer(init, conf):
                num_filtered_c = len(filter(lambda ar: ar.sys.presenceConf >= conf, obj_c))
                num_filtered_fa = len(filter(lambda ar: ar.sys.presenceConf >= conf, obj_f))
                num_miss_w_filtered_c = num_obj_m + num_obj_c - num_filtered_c
                init.append((conf, r_fa(num_filtered_c, num_miss_w_filtered_c, num_filtered_fa, ref_filter_area), p_miss(num_filtered_c, num_miss_w_filtered_c, num_filtered_fa)))
                return init

            det_points = reduce(_sweep_reducer, sorted(list({ ar.sys.presenceConf for ar in obj_c + obj_f })), [])

            return [ ("object-p_miss@{}rfa".format(target_rfa), p_miss_at_r_fa(det_points, target_rfa)) for target_rfa in object_target_rfas ]

        det_curve_metrics = { "p_miss@{}rfa".format(trfa): self._build_pmiss_at_rfa(trfa) for trfa in [ 1, 0.2, 0.15, 0.1, 0.03, 0.01 ] }

        pair_metrics = { "temporal_intersection": temporal_intersection,
                         "temporal_union": temporal_union }

        def pair_aggregate_metrics(pair_metrics):
            def _grouper(metric_rec):
                ref, sys, name, val = metric_rec
                return name

            def _mapper(metric_rec):
                ref, sys, name, val = metric_rec
                return val

            pair_metrics_dict = group_by_func(_grouper, pair_metrics, _mapper)

            def _r(init, metric):
                n = "mean-{}".format(metric)
                init.append((n, mean_exclude_none(pair_metrics_dict.get(metric, []))))
                return init

            return reduce(_r, [ "object-p_miss@{}rfa".format(target_rfa) for target_rfa in object_target_rfas ], [])

        def _build_simple_lookup(component_name):
            def _lkup(components):
                return components[component_name]

            return { component_name: _lkup }

        kernel_component_metrics = reduce(merge_dicts, map(_build_simple_lookup, [ "temporal_intersection-over-union", "minMODE" ] + [ "object-p_miss@{}rfa".format(tfa) for tfa in object_target_rfas ]), {})

        return (det_point_function,
                alignment_metrics,
                alignment_metrics_plus,
                det_curve_metrics,
                pair_metrics,
                pair_aggregate_metrics,
                kernel_component_metrics)


    def _build_pmiss_at_rfa(self, target_rfa):
        def _metric_func(points):
            return p_miss_at_r_fa(points, target_rfa)

        return _metric_func

    def _build_rfa(self, file_duration):
        def _metric_func(num_c, num_m, num_f):
            return r_fa(num_c, num_m, num_f, file_duration)

        return _metric_func

    def _build_nmide(self, file_duration_lookup, ns_collar_size, cost_fn_miss = lambda x: 1 * x, cost_fn_fa = lambda x: 1 * x):
        def _metric_func(c, m, f):
            return n_mide([(ar.ref, ar.sys) for ar in c], file_duration_lookup, ns_collar_size, cost_fn_miss, cost_fn_fa)

        return _metric_func

    def _build_nmide_count_rejects(self, ns_collar_size):
        def _metric_func(c, m, f):
            return n_mide_count_rejected([(ar.ref, ar.sys) for ar in c], ns_collar_size)

        return _metric_func

    def score(self,
              input_scoring_parameters,
              system_activities,
              reference_activities,
              activity_index,
              file_index):

        scoring_parameters = self.default_scoring_parameters.copy()
        scoring_parameters.update(input_scoring_parameters)

        det_point_func, alignment_metrics, alignment_metrics_plus, det_curve_metrics, pair_metrics, pair_aggregate_metrics, kernel_component_metrics = self.build_metrics(scoring_parameters, system_activities, reference_activities, activity_index, file_index)

        def _alignment_reducer(init, activity_record):
            activity_name, activity_properties = activity_record

            alignment_recs, metric_recs, pair_metric_recs, det_curve_metric_recs, det_points = init

            kernel = self.build_kernel(system_activities.get(activity_name, []),
                                       reference_activities.get(activity_name, []),
                                       scoring_parameters)

            correct, miss, fa = perform_alignment(reference_activities.get(activity_name, []),
                                                  system_activities.get(activity_name, []),
                                                  kernel)

            # Add to alignment records
            alignment_recs.setdefault(activity_name, []).extend(correct + miss + fa)

            local_pair_metric_recs = []
            for ar in correct:
                ref, sys = ar.ref, ar.sys
                for pair_metric, metric_func in pair_metrics.iteritems():
                    local_pair_metric_recs.append((ref, sys, pair_metric, metric_func(ref, sys)))

                for kernel_component_metric, metric_func in kernel_component_metrics.iteritems():
                    local_pair_metric_recs.append((ref, sys, kernel_component_metric, metric_func(ar.kernel_components)))

            pair_metric_recs_array = pair_metric_recs.setdefault(activity_name, [])
            pair_metric_recs_array.extend(local_pair_metric_recs)

            metric_recs_array = metric_recs.setdefault(activity_name, [])
            for alignment_metric, metric_func in alignment_metrics.iteritems():
                metric_recs_array.append((alignment_metric, metric_func(correct, miss, fa)))

            metric_recs_array.extend(alignment_metrics_plus(correct, miss, fa))
            metric_recs_array.extend(pair_aggregate_metrics(local_pair_metric_recs))

            num_correct, num_miss, num_fa = len(correct), len(miss), len(fa)
            det_points_array = det_points.setdefault(activity_name, [])
            for presence_conf in sorted(list({ ar.sys.presenceConf for ar in correct + fa })):
                num_filtered_c = len(filter(lambda ar: ar.sys.presenceConf >= presence_conf, correct))
                num_filtered_fa = len(filter(lambda ar: ar.sys.presenceConf >= presence_conf, fa))
                num_miss_w_filtered_c = num_miss + num_correct - num_filtered_c
                det_points_array.append(det_point_func(presence_conf,
                                                       num_filtered_c,
                                                       num_miss_w_filtered_c,
                                                       num_filtered_fa))

            det_curve_metric_recs_array = det_curve_metric_recs.setdefault(activity_name, [])
            for det_metric, metric_func in det_curve_metrics.iteritems():
                det_curve_metric_recs_array.append((det_metric, metric_func(det_points_array)))

            return init

        alignment_records, measure_records, pair_measure_records, det_curve_measure_records, det_point_records = reduce(_alignment_reducer, activity_index.iteritems(), ({}, {}, {}, {}, {}))

        mean_alignment_measure_records = [ ("mean-{}".format(k), mean_exclude_none(v)) for k, v in (group_by_func(lambda kv: kv[0], reduce(add, measure_records.values() + det_curve_measure_records.values(), []), lambda kv: kv[1])).iteritems() ]

        flat_alignment_records = reduce(add, alignment_records.values(), [])
        flat_c, flat_m, flat_f = reduce(alignment_partitioner, flat_alignment_records, ([], [], []))

        def _compute_microavg_alignment_measures(init, metric):
            metric_name, metric_func = metric
            init.append((metric_name, metric_func(flat_c, flat_m, flat_f)))
            return init

        microavg_alignment_measures = reduce(_compute_microavg_alignment_measures, alignment_metrics.iteritems(), [])

        overall_alignment_measures = alignment_metrics_plus(flat_c, flat_m, flat_f)

        def _reformat_alignment_records(init, item):
            key, records = item

            init[key] = map(lambda r: map(str, r.iter_with_extended_properties(self.output_kernel_components)), records)
            return init

        output_alignment_records = reduce(_reformat_alignment_records, alignment_records.iteritems(), {})

        def _object_frame_alignment_records(init, kv):
            activity, recs = kv

            def _m(item):
                def _subm(frame_ar):
                    frame, ar = frame_ar
                    return [str(item.ref),
                            str(item.sys),
                            str(frame),
                            str(ar.ref.objectType if ar.ref is not None else ar.sys.objectType)] + [ x for x in ar.iter_with_extended_properties(self.output_object_kernel_components) ]

                return map(_subm, item.kernel_components.get("alignment_records", []))

            init[activity] = reduce(add, map(_m, filter(lambda r: r.alignment == "CD", recs)), [])
            return init

        object_frame_alignment_records = reduce(_object_frame_alignment_records, alignment_records.iteritems(), {})

        return (scoring_parameters,
                output_alignment_records,
                merge_dicts(measure_records, det_curve_measure_records, add),
                pair_measure_records,
                mean_alignment_measure_records + microavg_alignment_measures + overall_alignment_measures,
                det_point_records,
                object_frame_alignment_records)
