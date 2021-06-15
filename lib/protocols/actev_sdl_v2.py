# actev_sdl_v2.py
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
import dill
from concurrent.futures import ProcessPoolExecutor

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
sys.path.append(lib_path)

from metrics import *
from alignment_record import *
from actev_kernel_components import *
from sed_kernel_components import *
from alignment import *
from helpers import *
from default import *

class ActEV_SDL_V2(Default):
    @classmethod
    def get_schema_fn(cls):
        return "actev_sdl_v2_schema.json"

    def __init__(self, scoring_parameters, file_index, activity_index, command):
        default_scoring_parameters = { "activity.epsilon_presenceconf_congruence": 1.0,
                                       "activity.temporal_overlap_delta": 0.5,
                                       "activity.p_miss_at_rfa_targets":   [ 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.50, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01 ],
                                       "activity.auc_at_fa_targets":       [ 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.50, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01 ],
                                       "activity.w_p_miss_at_rfa_targets": [ 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.50, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01 ],
                                       "activity.n_mide_at_rfa_targets":   [ 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.50, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01 ],
                                       "activity.fa_at_rfa_targets":       [ 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.50, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01 ],
                                       "nmide.ns_collar_size": 0,
                                       "nmide.cost_miss": 1,
                                       "nmide.cost_fa": 1,
                                       "wpmiss.numerator": 8,
                                       "wpmiss.denominator": 10,
                                       "fa.ns_collar_size": 0,
                                       "scoring_protocol": "actev_sdl_v2",
                                       "command": str(command),
                                       "git.commit": subprocess.check_output(["git", "--git-dir="+ os.path.join(lib_path, "../")+".git", "show", "--oneline", "-s", "--no-abbrev-commit","--pretty=format:%H--%aI"]).strip()} #.split(" ")[0]} #git show --oneline -s --no-abbrev-commit --pretty=format:%H--%aI

        scoring_parameters = merge_dicts(default_scoring_parameters, scoring_parameters)
        super(ActEV_SDL_V2, self).__init__(scoring_parameters, file_index, activity_index, command)

        self.file_framedur_lookup = { k: S({ int(_k): _v for _k, _v in v["selected"].items() }).area() for k, v in file_index.items() }
        self.total_file_duration_minutes = sum([ float(frames) / file_index[k]["framerate"] for k, frames in self.file_framedur_lookup.items()]) / float(60)
        self.file_framerate = [file_index[k]["framerate"] for k, v in file_index.items()][0]

    # Warning ** this cohort generation function only works when
    # activity instances are localized to a single file!!  This is
    # enforced by the schemas for ActEV18_AD and ActEV18_AOD
    """
    def default_cohort_gen(self, refs, syss):
        def _localization_file_grouper(instance):
            return list(instance.localization)[0]

        ref_groups = group_by_func(_localization_file_grouper, refs)
        sys_groups = group_by_func(_localization_file_grouper, syss)

        for k in ref_groups.keys() | sys_groups.keys():
            yield (ref_groups.get(k, []), sys_groups.get(k, []))
    """
    def default_cohort_gen(self, refs, syss):
        def get_next_reference_instances(srefs, ngs, syss):
            if srefs == []:
                return []
            refs = []
            # First call when creating a group
            if ngs == None:
                refs.append(srefs.pop(0))
                while len(srefs) and temporal_intersection(refs[-1], srefs[0]):
                    refs.append(srefs.pop(0))
            # Happen if the last ref instance wasn't detected by the system
            # In that case we can add all the following that the system missed
            elif ngs == []:
                while len(srefs) and len(syss) and temporal_intersection(refs[-1], syss[0] == 0):
                    refs.append(srefs.pop(0))
                # if there's no more sys insts (not very likely but still) 
                if not len(syss):
                    while (len(srefs)):
                        refs.append(srefs.pop(0))
            # Successive calls: happens if the last added system instance
            # overlaps another reference instance
            else:
                for s in ngs:
                    while len(srefs) and temporal_intersection(s, srefs[0]):
                        refs.append(srefs.pop(0))
            return refs

        def get_next_system_instances(ssyss, ngr, srefs):
            """try:
                print('+', len(ngr))
            except TypeError:
                print('s none')"""
            if ssyss == [] or ngr == None or ngr == []:
                return []
            if srefs == []:
                syss = []
                while len(ssyss):
                    syss.append(ssyss.pop(0))
                return syss
            syss = []
            syss.append(ssyss.pop(0))
            k = list(ngr[0].localization)[0]
            max_end_frame = max(int(list(r.localization[k])[1]) for r in ngr)
            # adding all sys detections that match nothing and strictly
            # happened before the next reference instance
            # they will be counted as FA
            while len(ssyss) and int(list(ssyss[0].localization[k])[0]) < max_end_frame and temporal_intersection(ssyss[0], ngr[-1]) == 0:
                syss.append(ssyss.pop(0))
            # now we add all possible candidates
            while len(ssyss) and temporal_intersection(ssyss[0], ngr[-1]):
                syss.append(ssyss.pop(0))
            return syss

        # First sorting by timestamp all instances
        srefs, ssyss = sorted(refs), sorted(syss)
        # Then group them by smaller parts
        i = 0
        while len(srefs) or len(ssyss):
            # intermediate groups of instances
            grefs, gsyss = [], []
            next_gr, next_gs = None, None
            while not (next_gr == [] and next_gs == []):
                next_gr = get_next_reference_instances(srefs, next_gs, gsyss)
                grefs.extend(next_gr)
                next_gs = get_next_system_instances(ssyss, next_gr, srefs)
                gsyss.extend(next_gs)
            yield (grefs, gsyss)


    def default_kernel_builder(self, refs, syss):
        kernel = build_linear_combination_kernel([ build_temporal_second_overlap_filter_v2(self.file_framerate, self.scoring_parameters["activity.temporal_overlap_delta"]) ],
                                               [ build_sed_presenceconf_congruence(syss, minmax=self.minmax) ],
                                               { "presenceconf_congruence": self.scoring_parameters["activity.epsilon_presenceconf_congruence"] })

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
            return fa_meas_v2(ref_sig, sys_sig, sys_sig_add)
        #[ (ar.ref, ar.sys) for ar in c ],
        #                  [(ar.ref) for ar in m],
        #                  [(ar.sys) for ar in f],
        #                  self.file_framedur_lookup,
        #                  self.scoring_parameters["fa.ns_collar_size"])
        return _fa_meas
        
    def compute_det_points_and_measures(self, alignment, rfa_denom, uniq_conf, rfa_targets, nmide_targets, fa_targets, wpmiss_denom, wpmiss_numer):
        sweeper = build_sweeper(lambda ar: ar.sys_presence_conf, [ build_rfa_metric(rfa_denom),
                                                                   build_pmiss_metric(),
                                                                   build_wpmiss_metric(wpmiss_denom, wpmiss_numer),
                                                                   self.build_nmide_measure(),
                                                                   self.build_fa_measure()], uniq_conf, file_framedur_lookup = self.file_framedur_lookup)
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
        
        fa_measures = get_points_along_confidence_curve(det_points,
                                                        "tfa",
                                                        lambda r: r["tfa"],
                                                        "p_miss",
                                                        lambda r: r["p_miss"],
                                                        fa_targets)

        wpmiss_tfa_measures = get_points_along_confidence_curve(det_points,
                                                                "tfa",
                                                                lambda r: r["tfa"],
                                                                "w_p_miss",
                                                                lambda r: r["w_p_miss"],
                                                                fa_targets)

        #auc_measure_t = get_auc(fa_measures, "tfa", threshold = self.scoring_parameters["activity.auc_at_fa_targets"])
        #auc_measure_r = get_auc(pmiss_measures, "rfa", threshold = self.scoring_parameters["activity.auc_at_fa_targets"])
        #return (flatten_sweeper_records(det_points, [ "rfa", "p_miss" ]), flatten_sweeper_records(det_points, [ "tfa", "p_miss" ]), flatten_sweeper_records(det_points, [ "rfa", "p_miss", "tfa", "tfa_denom", "tfa_numer" ]), merge_dicts(pmiss_measures, merge_dicts(nmide_measures, merge_dicts(wpmiss_measures, merge_dicts(fa_measures, merge_dicts(wpmiss_tfa_measures,merge_dicts(auc_measure_t,auc_measure_r)))))))
        return (flatten_sweeper_records(det_points, [ "rfa", "p_miss" ]), flatten_sweeper_records(det_points, [ "tfa", "p_miss" ]), flatten_sweeper_records(det_points, [ "rfa", "p_miss", "tfa", "tfa_denom", "tfa_numer" ]), merge_dicts(pmiss_measures, merge_dicts(nmide_measures, merge_dicts(wpmiss_measures, merge_dicts(fa_measures, wpmiss_tfa_measures)))))
    

    def compute_aggregate_det_points_and_measures(self, records, factorization_func, rfa_denom_func, uniq_conf, rfa_targets, nmide_targets, fa_targets, default_factorizations = []):
        def _r(init, item):
            p, t, fa, m = init
            factorization, recs = item
            f={}
            det_points, tfa_det_points, fa_data, measures = self.compute_det_points_and_measures(recs, rfa_denom_func(recs), uniq_conf, rfa_targets, nmide_targets, fa_targets, self.scoring_parameters["wpmiss.denominator"], self.scoring_parameters["wpmiss.numerator"])
            p["-".join(factorization)] = det_points
            f["-".join(factorization)] = fa_data
            t["-".join(factorization)] = tfa_det_points
            
            for k in f:
                for i in f[k]:
                    ii = i[0] if 'e' in str(i[0]) else round(i[0], 5)
                    fa.append((k, ii, "p_miss", i[2]))
                    fa.append((k, ii, "rfa", i[1]))
                    fa.append((k, ii, "tfa", i[3]))
                    fa.append((k, ii, "tfa_denom", i[4]))
                    fa.append((k, ii, "tfa_numer", i[5]))
                
            for _m, v in measures.items():
                m.append(factorization + (_m, v))
            return (p, t, fa, m)

        grouped = merge_dicts({ k: [] for k in default_factorizations }, group_by_func(factorization_func, records))
        _r_srlz = dill.dumps(_r)
        args = []
        for key in grouped:
            args.append((_r_srlz, (key, grouped[key]), ({}, {}, [], [])))

        with ProcessPoolExecutor(self.pn) as pool:
            res = pool.map(unserialize_fct_res, args)

        p, t, fa, m = {}, {}, [], []
        for entry in res:
            p.update(entry[0])
            t.update(entry[1])
            fa.extend(entry[2])
            m.extend(entry[3])
        return (p, t, fa, m)

    def compute_record_means(self, records, selected_measures = None):
        raw_means = self.compute_means(records, selected_measures)

        def _r(init, r):
            f, m, v = r

            if m == "mean":
                init.append(("mean-{}".format(f), v))

            return init

        return reduce(_r, raw_means, [])

    def compute_results(self, alignment, uniq_conf):
        # Activity level + Pair Aggregates
        def _activity_grouper(rec):
            return (rec.activity,)

        out_det_points, out_tfa_det_points, out_fa_data, det_measures = self.compute_aggregate_det_points_and_measures(
            alignment, _activity_grouper,
            lambda x: self.total_file_duration_minutes, uniq_conf, self.scoring_parameters["activity.p_miss_at_rfa_targets"], self.scoring_parameters["activity.n_mide_at_rfa_targets"], self.scoring_parameters["activity.fa_at_rfa_targets"], self.default_activity_groups)

        # Overall level + Activity Aggregates + Pair Agg. Aggregates
        def _empty_grouper(rec):
            return tuple() # empty tuple

        ar_nmide_measure = self.build_ar_nmide_measure()
        activity_nmides = self.compute_aggregate_measures(alignment, _activity_grouper, [ ar_nmide_measure ], self.default_activity_groups)
        activity_results = activity_nmides + det_measures

        overall_nmide = self.compute_aggregate_measures(alignment, _empty_grouper, [ ar_nmide_measure ])
        activity_means = self.compute_record_means(activity_results)

        # Pairs
        def _pair_arg_map(rec):
            return (rec.ref, rec.sys)

        pair_measures = [ self.build_simple_measure(_pair_arg_map, "temporal_intersection", temporal_intersection),
                          self.build_simple_measure(_pair_arg_map, "temporal_union", temporal_union),
                          self.build_simple_measure(_pair_arg_map, "temporal_fa", temporal_fa),
                          self.build_simple_measure(_pair_arg_map, "temporal_miss", temporal_miss),
                          self.build_simple_measure(lambda x: (x.kernel_components.get("temporal_intersection-over-union"),), "temporal_intersection-over-union", identity) ]

        c, m, f = partition_alignment(alignment)
        def _pair_properties_map(rec):
            return (rec.activity, rec.ref.activityID, rec.sys.activityID)
        pair_results = self.compute_atomic_measures(c, _pair_properties_map, pair_measures)

        # Output alignment records
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
