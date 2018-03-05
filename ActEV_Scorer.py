#!/usr/bin/env python2

# ActEV_Scorer.py
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
import errno
import argparse
import json
import jsonschema
from operator import add

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
sys.path.append(lib_path)
protocols_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib/protocols")
sys.path.append(protocols_path)

from activity_instance import *
from plot import *
from helpers import *

def err_quit(msg, exit_status=1):
    print("[Error] {}".format(msg))
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
        for rec in [field_names] + sorted(records):
            out_f.write("{}\n".format(sep.join(map(str, rec))))

    yield_file_to_function(out_path, _write_recs)

def serialize_as_json(out_path, out_object):
    def _write_json(out_f):
        out_f.write("{}\n".format(json.dumps(out_object, indent=2)))

    yield_file_to_function(out_path, _write_json)

# Reducer function for generating an activity instance lookup dict
def _activity_instance_reducer(init, a):
    init.setdefault(a["activity"], []).append(ActivityInstance(a))
    return init

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Soring script for the NIST ActEV evaluation")
    parser.add_argument('protocol', choices=['ActEV18_AD'], help="Scoring protocol")
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

    log(1, "[Info] Command: {}".format(" ".join(sys.argv)))

    if args.protocol == 'ActEV18_AD':
        from actev18_ad import *
        protocol = ActEV18_AD
    else:
        err_quit("Unrecognized protocol.  Aborting!")

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

    log(1, "[Info] Loading JSON schema")
    schema_path = "{}/{}".format(protocols_path, protocol.get_schema_fn())
    system_output_schema = load_json(schema_path)

    log(1, "[Info] Validating system output against JSON schema")
    try:
        jsonschema.validate(system_output, system_output_schema)
        log(1, "[Info] System output validated successfully against JSON schema")
    except jsonschema.exceptions.ValidationError as verr:
        err_quit("{}\n[Error] JSON schema validation of system output failed, Aborting!".format(verr))

    scoring_parameters, alignment_records, activity_measure_records, pair_measure_records, aggregate_measure_records, det_point_records = protocol().score({}, system_activities, reference_activities, activity_index, file_index)

    mkdir_p(args.output_dir)
    log(1, "[Info] Saving results to directory '{}'".format(args.output_dir))

    serialize_as_json("{}/scoring_parameters.json".format(args.output_dir), scoring_parameters)

    write_records_as_csv("{}/alignment.csv".format(args.output_dir), ["activity", "alignment", "ref", "sys", "sys_decision_score", "kernel_similarity", "kernel_components"], dict_to_records(alignment_records, lambda v: map(str, v.iter_with_extended_properties())))

    write_records_as_csv("{}/pair_metrics.csv".format(args.output_dir), ["activity", "ref", "sys", "metric_name", "metric_value"], dict_to_records(pair_measure_records, lambda v: map(str, v)))

    write_records_as_csv("{}/scores_by_activity.csv".format(args.output_dir), ["activity", "metric_name", "metric_value"], dict_to_records(activity_measure_records, lambda v: map(str, v)))

    write_records_as_csv("{}/scores_aggregated.csv".format(args.output_dir), [ "metric_name", "metric_value" ], aggregate_measure_records)

    if not args.disable_plotting:
        figure_dir = "{}/figures".format(args.output_dir)
        mkdir_p(figure_dir)
        log(1, "[Info] Saving figures to directory '{}'".format(figure_dir))
        log(1, "[Info] Plotting combined DET curve")
        det_curve(det_point_records, "{}/DET_COMBINED.png".format(figure_dir))

        for k, v in det_point_records.iteritems():
            log(1, "[Info] Plotting DET curve for {}".format(k))
            det_curve({k: v}, "{}/DET_{}.png".format(figure_dir, k))
