#!/usr/bin/env python2

import sys
import os
import errno
import argparse
import json
import jsonschema
from collections import namedtuple

import pprint ###

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
sys.path.append(lib_path)
protocols_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib/protocols")
sys.path.append(protocols_path)

from alignment import *
from sed_kernel_components import *
from actev_kernel_components import *
from sparse_signal import SparseSignal as S
from activity_instance import *
from metrics import *
from plot import *

from actev18 import *

def err_quit(msg, exit_status=1):
    print(msg)
    exit(exit_status)

def build_logger(verbosity_threshold=0):
    def _log(depth, msg):
        if depth <= verbosity_threshold:
            print(msg)

    return _log

def load_json(json_fn):
    try:
        with open(json_fn, 'r') as json_f:
            return json.load(json_f)
    except IOError as ioerr:
        err_quit("{}. Aborting!".format(ioerr))

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            err_quit("{}. Aborting!".format(exc))

def yield_file_to_function(file_path, function):
    try:
        with open(file_path, 'w') as out_f:
            function(out_f)
    except IOError as ioerr:
        err_quit("{}. Aborting!".format(ioerr))
        
def write_records_as_csv(out_path, field_names, records, sep = "|"):
    def _write_recs(out_f):
        for rec in [field_names] + records:
            out_f.write("{}\n".format(sep.join(map(str, rec))))

    yield_file_to_function(out_path, _write_recs)

# Reducer function for generating an activity instance lookup dict
def _activity_instance_reducer(init, a):
    init.setdefault(a["activity"], []).append(ActivityInstance(a))
    return init

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Soring script for the NIST ActEV evaluation")
    # TODO: protocol argument
#    parser.add_argument('protocol', choices=['ActEV18'])
    parser.add_argument("-s", "--system-output-file", help="System output JSON file", type=str, required=True)
    parser.add_argument("-r", "--reference-file", help="Reference JSON file", type=str, required=True)
    parser.add_argument("-a", "--activity-index", help="Activity index JSON file", type=str, required=True)
    parser.add_argument("-f", "--file-index", help="file index JSON file", type=str, required=True)
    parser.add_argument("-o", "--output-dir", help="Output directory for results", type=str, required=True)
    parser.add_argument("-d", "--disable-plotting", help="Disable DET Curve plotting of results", action="store_true")
    parser.add_argument("-v", "--verbose", help="Toggle verbose log output", action="store_true")
    args = parser.parse_args()

    verbosity_threshold = 1 if args.verbose else 0
    log = build_logger(verbosity_threshold)
    
    log(1, "[Info] Loading system output file")
    system_output = load_json(args.system_output_file)
    system_activities = reduce(_activity_instance_reducer, system_output["activities"], {})
    
    log(1, "[Info] Loading reference file")
    reference = load_json(args.reference_file)
    reference_activities = reduce(_activity_instance_reducer, reference["activities"], {})

    log(1, "[Info] Loading activity index file")
    activity_index = load_json(args.activity_index)

    log(1, "[Info] Loading file index file")
    file_index = load_json(args.file_index)

    # TODO: remove non-selected area from reference and system
    # instances, truncation or ?
    total_file_duration_minutes = sum([ S({ int(_k): _v for _k, _v in v["selected"].iteritems() }).area() / float(v["framerate"]) for v in file_index.values() ]) / float(60)

    protocol = ActEV18(total_file_duration_minutes = total_file_duration_minutes)
    
    def _alignment_reducer(init, activity_record):
        activity_name, activity_properties = activity_record

        alignment_recs, metric_recs, pair_metric_recs, det_points = init

        kernel = protocol.build_kernel(system_activities[activity_name])
        
        correct, miss, fa = perform_alignment(reference_activities[activity_name],
                                              system_activities[activity_name],
                                              kernel)

        # Add to alignment records
        alignment_recs.setdefault(activity_name, []).extend(correct + miss + fa)

        pair_metric_recs_array = pair_metric_recs.setdefault(activity_name, [])
        for ar in correct:
            ref, sys = ar.ref, ar.sys

            for pair_metric in protocol.default_reported_instance_pair_metrics:
                pair_metric_recs_array.append((ref, sys, pair_metric, protocol.instance_pair_metrics[pair_metric](ref, sys)))

            for kernel_component in protocol.default_reported_kernel_components:
                pair_metric_recs_array.append((ref, sys, kernel_component, ar.kernel_components[kernel_component]))

        metric_recs_array = metric_recs.setdefault(activity_name, [])
        for alignment_metric in protocol.default_reported_alignment_metrics:
            metric_recs_array.append((alignment_metric, protocol.alignment_metrics[alignment_metric](correct, miss, fa)))

        num_correct, num_miss, num_fa = len(correct), len(miss), len(fa)
        det_points_array = det_points.setdefault(activity_name, [])
        for decision_score in sorted(list({ ar.sys.decisionScore for ar in correct + fa })):
            num_filtered_c = len(filter(lambda ar: ar.sys.decisionScore >= decision_score, correct))
            num_filtered_fa = len(filter(lambda ar: ar.sys.decisionScore >= decision_score, fa))
            num_miss_w_filtered_c = num_miss + num_correct - num_filtered_c
            det_points_array.append((decision_score,
                                     r_fa(num_filtered_c, num_miss_w_filtered_c, num_filtered_fa, total_file_duration_minutes),
                                     p_miss(num_filtered_c, num_miss_w_filtered_c, num_filtered_fa)))

        return init

    alignment_records, metric_records, pair_metric_records, det_point_records = reduce(_alignment_reducer, activity_index.iteritems(), ({}, {}, {}, {}))

    def dict_to_records(d, value_map = lambda x: x):
        out_list = []
        for k, v in d.iteritems():
            for _v in v:
                out_list.append([k] + value_map(_v))

        return out_list

    mkdir_p(args.output_dir)
    log(1, "[Info] Saving results to directory '{}'".format(args.output_dir))

    write_records_as_csv("{}/config.csv".format(args.output_dir), ["parameter", "value"], [("command", " ".join(sys.argv)), ("protocol", "ActEV18")] + protocol.dump_parameters())

    write_records_as_csv("{}/alignment.csv".format(args.output_dir), ["activity", "alignment", "ref", "sys", "sys_decision_score", "kernel_similarity", "kernel_components"], dict_to_records(alignment_records, lambda v: map(str, v.iter_with_extended_properties())))

    write_records_as_csv("{}/pair_metrics.csv".format(args.output_dir), ["activity", "ref", "sys", "metric_name", "metric_value"], dict_to_records(pair_metric_records, lambda v: map(str, v)))

    write_records_as_csv("{}/alignment_metrics.csv".format(args.output_dir), ["activity", "metric_name", "metric_value"], dict_to_records(metric_records, lambda v: map(str, v)))

    if not args.disable_plotting:
        figure_dir = "{}/figures".format(args.output_dir)
        mkdir_p(figure_dir)
        log(1, "[Info] Saving figures to directory '{}'".format(figure_dir))
        log(1, "[Info] Plotting combined DET curve")
        det_curve(det_point_records, "{}/DET_COMBINED.png".format(figure_dir))

        for k, v in det_point_records.iteritems():
            log(1, "[Info] Plotting DET curve for {}".format(k))
            det_curve({k: v}, "{}/DET_{}.png".format(figure_dir, k))

