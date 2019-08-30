# actev18_ad.py
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
from pprint import pprint
import subprocess
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
sys.path.append(lib_path)

from metrics import *
from alignment_record import *
from actev_kernel_components import *
from sed_kernel_components import *
from alignment import *
from helpers import *
from default import *

class ActEV18_AD_TFA(Default):
    @classmethod
    def get_schema_fn(cls):
        return "actev18_ad_schema.json"

    def __init__(self, scoring_parameters, file_index, activity_index, command):
        default_scoring_parameters = { "activity.epsilon_temporal_congruence": 1.0e-8,
                                       "activity.epsilon_presenceconf_congruence": 1.0e-6,
                                       "activity.temporal_overlap_delta": 0.2,
                                       "activity.p_miss_at_rfa_targets": [ 1, 0.2, 0.15, 0.1, 0.03, 0.01 ],
                                       "activity.w_p_miss_at_rfa_targets": [ 1, 0.2, 0.15, 0.1, 0.03, 0.01 ],
                                       "activity.auc_at_fa_targets": [ 1, 0.2, 0.15, 0.1, 0.03, 0.01 ],
                                       "activity.n_mide_at_rfa_targets": [ 1, 0.2, 0.15, 0.1, 0.03, 0.01 ],
                                       "activity.fa_at_rfa_targets": [ 1, 0.2, 0.15, 0.1, 0.03, 0.01 ],
                                       "nmide.ns_collar_size": 0,
                                       "nmide.cost_miss": 1,
                                       "nmide.cost_fa": 1,
                                       "wpmiss.numerator": 8,
                                       "wpmiss.denominator": 10,
                                       "fa.ns_collar_size": 0,
                                       "scoring_protocol": "actev18_ad_tfa",
                                       "command": str(command),
                                       "git.commit": subprocess.check_output(["git", "show", "--oneline", "-s", "--no-abbrev-commit","--pretty=format:%H--%aI"]).strip()}

        scoring_parameters = merge_dicts(default_scoring_parameters, scoring_parameters)

        super(ActEV18_AD_TFA, self).__init__(scoring_parameters, file_index, activity_index, command)
        self.file_framedur_lookup = { k: S({ int(_k): _v for _k, _v in v["selected"].iteritems() }).area() for k, v in file_index.iteritems() }
        self.total_file_duration_minutes = sum([ float(frames) / file_index[k]["framerate"] for k, frames in self.file_framedur_lookup.iteritems()]) / float(60)
        #self.file_framerate = [file_index[k]["framerate"] for k, v in file_index.iteritems()][0]
        
    # Warning ** this cohort generation function only works when
    # activity instances are localized to a single file!!  This is
    # enforced by the schemas for ActEV18_AD and ActEV18_AOD
    def default_cohort_gen(self, refs, syss):
        def _localization_file_grouper(instance):
            return instance.localization.keys()[0]

        ref_groups = group_by_func(_localization_file_grouper, refs)
        sys_groups = group_by_func(_localization_file_grouper, syss)

        for k in ref_groups.viewkeys() | sys_groups.viewkeys():
            yield (ref_groups.get(k, []), sys_groups.get(k, []))

    def default_kernel_builder(self, refs, syss):
        kernel = build_linear_combination_kernel([ build_temporal_overlap_filter(self.scoring_parameters["activity.temporal_overlap_delta"]) ],
                                               [ temporal_intersection_over_union_component,
                                                 build_sed_presenceconf_congruence(syss) ],
                                               { "temporal_intersection-over-union": self.scoring_parameters["activity.epsilon_temporal_congruence"],
                                                 "presenceconf_congruence": self.scoring_parameters["activity.epsilon_presenceconf_congruence"] })

        # Kernel for AD doesn't change based on activity, just
        # returning the predefined kernel
        def _configure_kernel_for_activity(activity, activity_properties, refs, syss):
            return kernel

        return _configure_kernel_for_activity

    def build_ar_nmide_measure(self):
        _core_nmide = self.build_nmide_measure()
        def _nmide(ars):
            c = filter(lambda rec: rec.alignment == "CD", ars)
            return _core_nmide(c, None, None)

        return _nmide

    def build_nmide_measure(self):
        def _nmide(c, m, f):
            return n_mide([ (ar.ref, ar.sys) for ar in c ],
                          self.file_framedur_lookup,
                          self.scoring_parameters["nmide.ns_collar_size"],
                          lambda x: self.scoring_parameters["nmide.cost_miss"] * x,
                          lambda x: self.scoring_parameters["nmide.cost_miss"] * x)

        return _nmide
    
    def build_fa_measure(self):
        def _fa_meas(ref_sig, sys_sig, sys_sig_add):
            return fa_meas(ref_sig, sys_sig, sys_sig_add)

        return _fa_meas
        
    def compute_det_points_and_measures(self, alignment, rfa_denom, rfa_targets, nmide_targets, fa_targets, wpmiss_denom, wpmiss_numer):
        sweeper = build_sweeper(lambda ar: ar.sys_presence_conf, [ build_rfa_metric(rfa_denom),
                                                                   build_pmiss_metric(),
                                                                   build_wpmiss_metric(wpmiss_denom, wpmiss_numer),
                                                                   self.build_nmide_measure(),
                                                                   self.build_fa_measure()], file_framedur_lookup = self.file_framedur_lookup)

        
        det_points = sweeper(alignment)
        #print "det_points"
        #pprint(det_points)

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
        fa_measures = get_points_along_confidence_curve(det_points,
                                                        "tfa",
                                                        lambda r: r["tfa"],
                                                        "p_miss",
                                                        lambda r: r["p_miss"],
                                                        fa_targets)
        auc_measure_f = get_auc(fa_measures, "tfa", threshold = self.scoring_parameters["activity.auc_at_fa_targets"])
        auc_measure_r = get_auc(pmiss_measures, "rfa", threshold = self.scoring_parameters["activity.auc_at_fa_targets"])
        return (flatten_sweeper_records(det_points, [ "rfa", "p_miss" ]), flatten_sweeper_records(det_points, [ "tfa", "p_miss" ]), flatten_sweeper_records(det_points, [ "rfa", "p_miss", "tfa", "tfa_denom", "tfa_numer" ]), merge_dicts(pmiss_measures, merge_dicts(nmide_measures, merge_dicts(wpmiss_measures, merge_dicts(fa_measures,merge_dicts(auc_measure_f,auc_measure_r))))))
    

    def compute_aggregate_det_points_and_measures(self, records, factorization_func, rfa_denom_func, rfa_targets, nmide_targets, fa_targets, default_factorizations = []):
        def _r(init, item):
            p, t, fa, m = init
            factorization, recs = item
            f={}
            det_points, tfa_det_points, fa_data, measures = self.compute_det_points_and_measures(recs, rfa_denom_func(recs), rfa_targets, nmide_targets, fa_targets, self.scoring_parameters["wpmiss.denominator"], self.scoring_parameters["wpmiss.numerator"])

            p["-".join(factorization)] = det_points
            f["-".join(factorization)] = fa_data
            t["-".join(factorization)] = tfa_det_points
            for k in f:
                for i in f[k]:
                    fa.append((k, i[0], "p_miss", i[2]))
                    fa.append((k, i[0], "rfa", i[1]))
                    fa.append((k, i[0], "tfa", i[3]))
                    fa.append((k, i[0], "tfa_denom", i[4]))
                    fa.append((k, i[0], "tfa_numer", i[5]))
#            for k, v in f.iteritems():
#                print k,v
                #fa.append(factorization + (k, v))
                #for k in f.keys():
                
            for _m, v in measures.iteritems():
                m.append(factorization + (_m, v))

            return (p, t, fa, m)

        grouped = merge_dicts({ k: [] for k in default_factorizations }, group_by_func(factorization_func, records))
        return reduce(_r, grouped.iteritems(), ({}, {}, [], []))

    def compute_record_means(self, records, selected_measures = None):
        raw_means = self.compute_means(records, selected_measures)

        def _r(init, r):
            f, m, v = r

            if m == "mean":
                init.append(("mean-{}".format(f), v))

            return init

        return reduce(_r, raw_means, [])

    def compute_results(self, alignment):
        c, m, f = partition_alignment(alignment)
        #print c[0].ref
        #print c[0].sys
        ar_nmide_measure = self.build_ar_nmide_measure()

        def _pair_arg_map(rec):
            return (rec.ref, rec.sys)

        pair_measures = [ self.build_simple_measure(_pair_arg_map, "temporal_intersection", temporal_intersection),
                          self.build_simple_measure(_pair_arg_map, "temporal_union", temporal_union),
                          self.build_simple_measure(_pair_arg_map, "temporal_fa", temporal_fa),
                          self.build_simple_measure(_pair_arg_map, "temporal_miss", temporal_miss),
                          self.build_simple_measure(lambda x: (x.kernel_components.get("temporal_intersection-over-union"),), "temporal_intersection-over-union", identity) ]

        # Pairs
        def _pair_properties_map(rec):
            return (rec.activity, rec.ref.activityID, rec.sys.activityID)

        pair_results = self.compute_atomic_measures(c, _pair_properties_map, pair_measures)

        # Activity level + Pair Aggregates
        def _activity_grouper(rec):
            return (rec.activity,)

        activity_nmides = self.compute_aggregate_measures(alignment, _activity_grouper, [ ar_nmide_measure ], self.default_activity_groups)
        out_det_points, out_tfa_det_points, out_fa_data, det_measures = self.compute_aggregate_det_points_and_measures(alignment, _activity_grouper, lambda x: self.total_file_duration_minutes, self.scoring_parameters["activity.p_miss_at_rfa_targets"], self.scoring_parameters["activity.n_mide_at_rfa_targets"], self.scoring_parameters["activity.fa_at_rfa_targets"], self.default_activity_groups)
#        print "out_det_points"
#        print out_det_points
        # Overall level + Activity Aggregates + Pair Agg. Aggregates
        def _empty_grouper(rec):
            return tuple() # empty tuple

        activity_results = activity_nmides + det_measures
#        print activity_results
        overall_nmide = self.compute_aggregate_measures(alignment, _empty_grouper, [ ar_nmide_measure ])
        activity_means = self.compute_record_means(activity_results)

        def _align_rec_mapper(rec):
            return (rec.activity,) + tuple(rec.iter_with_extended_properties(["temporal_intersection-over-union", "presenceconf_congruence"]))

        output_alignment_records = map(_align_rec_mapper, alignment)

        return { "pair_metrics": pair_results,
                 "scores_by_activity": activity_results,
                 "scores_aggregated": activity_means + overall_nmide,
                 "det_point_records": out_det_points,
                 "tfa_det_point_records": out_tfa_det_points,
                 "output_alignment_records": output_alignment_records,
                 "scores_by_activity_and_threshold": out_fa_data}
