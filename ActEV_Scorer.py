#!/usr/bin/env python3

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
from functools import reduce
from tempfile import NamedTemporaryFile

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
sys.path.append(lib_path)
protocols_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib/protocols")
sys.path.append(protocols_path)

from activity_instance import *
from plot import *
from helpers import *
from datacontainer import DataContainer
from render import Render
from logger import build_logger
from ActivitiesFilePruner import prune
from sparse_signal import SparseSignal

def err_quit(msg, exit_status=1):
    print("[Error] {}".format(msg))
    exit(exit_status)

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
    def listify(records):
        l_records = records
        if isinstance(records, (map, tuple, list)):
            l_records = list(records)
            for i in range(len(l_records)):
                l_records[i] = listify(l_records[i])
        return l_records

    l_records = listify(records)
    sorted_rec = sorted(l_records)

    def _write_recs(out_f):
        for rec in [field_names] + sorted_rec:
            out_f.write("{}\n".format(sep.join(map(str, rec))))

    yield_file_to_function(out_path, _write_recs)

def serialize_as_json(out_path, out_object):
    def _write_json(out_f):
        out_f.write("{}\n".format(json.dumps(out_object, indent=2, sort_keys=True)))
    yield_file_to_function(out_path, _write_json)

def load_system_output(log, system_output_file):
    return load_json(system_output_file)

def load_reference(log, reference_file):
    log(1, "[Info] Loading reference file")
    return load_json(reference_file)

def load_activity_index(log, activity_index_file):
    log(1, "[Info] Loading activity index file")
    return load_json(activity_index_file)

def load_file_index(log, file_index_file):
    log(1, "[Info] Loading file index file")
    return load_json(file_index_file)

def load_scoring_parameters(log, scoring_parameters_file):
    log(1, "[Info] Loading scoring parameters file")
    return load_json(scoring_parameters_file)

def load_schema_for_protocol(log, protocol):
    log(1, "[Info] Loading JSON schema")
    schema_path = "{}/{}".format(protocols_path, protocol.get_schema_fn())
    return load_json(schema_path)

def parse_activities(deserialized_json, file_index, load_objects = False, ignore_extraneous = False, ignore_missing = False):
    raw_instances = [ a for a in deserialized_json.get("activities", []) ]
    if args.ignore_no_score_regions:
        activity_instances = [ ActivityInstance(a, load_objects) for a in raw_instances ]
    else:
        filtered_instances = []
        for inst in raw_instances:
            fn = list(inst['localization'].keys())[0]
            frames = SparseSignal(inst['localization'][fn])
            try:
                f_frames = SparseSignal(file_index[fn]['selected'])
                if (f_frames | frames) == f_frames:
                    filtered_instances.append(inst)
            except KeyError as e:  # may append if there are extra files
                if not args.ignore_extraneous_files:
                    raise e
                pass
        activity_instances = [ ActivityInstance(a, load_objects) for a in filtered_instances ]

    if ignore_extraneous or ignore_missing:
        if deserialized_json.get('processingReport', None) is None:
            files = set(deserialized_json.get("filesProcessed", []))
        else:
            files = deserialized_json.get("processingReport").get('fileStatuses').keys()
        extraneous_files = files - file_index.keys()
        missing_files = file_index.keys() - files

        def _r(init, a):
            if ignore_extraneous:
                for f in extraneous_files & a.localization.keys():
                    del a.localization[f]
            if ignore_missing:
                for f in missing_files & a.localization.keys():
                    del a.localization[f]
            # Throw out activity instances only localized to "extraneous" files
            if len(a.localization) > 0:
                init.append(a)
            return init

        return reduce(_r, activity_instances, [])
    else:
        return activity_instances

def validate_input(log, system_output, system_output_schema):
    log(1, "[Info] Validating system output against JSON schema")
    try:
        jsonschema.validate(system_output, system_output_schema)
        log(1, "[Info] System output validated successfully against JSON schema")
    except jsonschema.exceptions.ValidationError as verr:
        err_quit("{}\n[Error] JSON schema validation of system output failed. Aborting!".format(verr))

    # Assuming that the input is valid if we make it this far
    return True

# Check system "filesProcessed" vs file index
def check_file_index_congruence(log, system_output, file_index, ignore_extraneous = False, ignore_missing = False):
    isReportProcessing = system_output.get("processingReport", {}) != {}
    key = 'processingReport' if isReportProcessing else 'filesProcessed'
    if not isReportProcessing:
        sys_files = set(system_output.get("filesProcessed", []))
    else:
        sys_files = set(system_output.get("processingReport", {}).get('fileStatuses', {}).keys())
    index_files = set(file_index.keys())

    missing = index_files - sys_files
    extraneous = sys_files - index_files

    log(1, "[Info] Checking file index against system's \"%s\"" % key)

    error = False
    if not ignore_extraneous:
        if len(extraneous) > 0:
            for e in extraneous:
                log(0, "[Error] Extraneous file '%s' in system's \"%s\"" % (e, key))
            error = True
    if not ignore_missing:
        if len(missing) > 0:
            for m in missing:
                log(0, "[Error] Missing file '%s' from system's \"%s\"" % (m, key))
            error = True
    if error:
        err_quit("System \"%s\" and file index are incongruent. Aborting!" % key)
    return True


def write_out_scoring_params(output_dir, params):
    out_file = "{}/scoring_parameters.json".format(output_dir)
    for key in sorted(params.keys()):
        if type(params[key])==bytes:
            params[key] = str(params[key])[2:-1]
    serialize_as_json(out_file, params)

    return out_file

def score_actev19_ad(args):
    from actev19_ad import ActEV19_AD
    score_basic(ActEV19_AD, args)

def score_actev19_ad_v2(args):
    from actev19_ad_v2 import ActEV19_AD_V2
    score_basic(ActEV19_AD_V2, args)

def score_actev_sdl_v1(args):
    from actev_sdl_v1 import ActEV_SDL_V1
    score_basic(ActEV_SDL_V1, args)

def score_actev_sdl_v2(args):
    from actev_sdl_v2 import ActEV_SDL_V2
    score_basic(ActEV_SDL_V2, args)

def score_actev_sdl_v2_pr(args):
    from actev_sdl_v2_pr import ActEV_SDL_V2_PR
    score_basic(ActEV_SDL_V2_PR, args)
    
def score_actev18_ad(args):
    from actev18_ad import ActEV18_AD
    score_basic(ActEV18_AD, args)

def score_actev18pc_ad(args):
    from actev18pc_ad import ActEV18PC_AD
    score_basic(ActEV18PC_AD, args)

def score_actev18_ad_tfa(args):
    from actev18_ad_tfa import ActEV18_AD_TFA
    score_basic(ActEV18_AD_TFA, args)

def score_actev18_ad_1secol(args):
    from actev18_ad_1SecOL import ActEV18_AD_1SecOL
    score_basic(ActEV18_AD_1SecOL, args)
    
def score_actev18_aod(args):
    from actev18_aod import ActEV18_AOD
    score_basic(ActEV18_AOD, args)

def score_actev18_aodt(args):
    from actev18_aodt import ActEV18_AODT
    score_basic(ActEV18_AODT, args)

def score_basic(protocol_class, args):
    verbosity_threshold = 1 if args.verbose else 0
    log = build_logger(verbosity_threshold)
    log(1, "[Info] Command: {}".format(" ".join(sys.argv)))

    if not args.validation_only:
        # Check for now-required arguments
        if args.reference_file is None:
            err_quit("Missing required REFERENCE_FILE argument (-r, --reference-file).  Aborting!")

        if args.output_dir is None:
            err_quit("Missing required OUTPUT_DIR argument (-o, --output-dir).  Aborting!")

    activity_index = load_activity_index(log, args.activity_index)

    file_index = load_file_index(log, args.file_index)
    input_scoring_parameters = load_scoring_parameters(log, args.scoring_parameters_file) if args.scoring_parameters_file else {}
    protocol = protocol_class(input_scoring_parameters, file_index, activity_index, " ".join(sys.argv))
    protocol.pn = args.processes_number
    protocol.minmax = None
    plot_options = load_json(args.plotting_parameters_file) if args.plotting_parameters_file else {}
    system_output_schema = load_schema_for_protocol(log, protocol)

    log(1, "[Info] Loading activities and references")
    if args.prune_system_output:
        system_output, minmax = prune(args.system_output_file, args.prune_system_output, file_index, log)
        protocol.minmax = minmax
    else:
        system_output = load_system_output(log, args.system_output_file)

    if not args.skip_validation:
        validate_input(log, system_output, system_output_schema)
        check_file_index_congruence(log, system_output, file_index, args.ignore_extraneous_files, args.ignore_missing_files)
        log(1, "[Info] Validation successful")

    if args.validation_only:
        exit(0)

    system_activities = parse_activities(system_output, file_index, protocol_class.requires_object_localization, args.ignore_extraneous_files, args.ignore_missing_files)
    reference = load_reference(log, args.reference_file)
    reference_activities = parse_activities(reference, file_index, protocol_class.requires_object_localization, args.ignore_extraneous_files, args.ignore_missing_files)

    if not args.include_zero_ref_instances:
        # Removing activities from activity-index that doesn't appear in the reference instances.
        for act in [act for act in activity_index if act not in [inst.activity for inst in reference_activities]]:
            del activity_index[act]
        # Now we regenerate protocol ans stuff
        protocol = protocol_class(input_scoring_parameters, file_index, activity_index, " ".join(sys.argv))
        protocol.pn = args.processes_number
        protocol.minmax = None
        system_output_schema = load_schema_for_protocol(log, protocol)

    log(1, "[Info] Computing alignments ..")
    alignment = protocol.compute_alignment(system_activities, reference_activities)
    log(1, '[Info] Scoring ..')
    results = protocol.compute_results(alignment, args.det_point_resolution)

    mkdir_p(args.output_dir)
    log(1, "[Info] Saving results to directory '{}'".format(args.output_dir))
    audc_by_activity = []
    mean_audc = []
    if not args.disable_plotting:
        export_records(log, results.get("det_point_records", {}), results.get("tfa_det_point_records", {}), args.output_dir, plot_options)
        audc_by_activity, mean_audc = protocol.compute_auc(args.output_dir)

    write_out_scoring_params(args.output_dir, protocol.scoring_parameters)
    write_records_as_csv("{}/alignment.csv".format(args.output_dir), ["activity", "alignment", "ref", "sys", "sys_presenceconf_score", "kernel_similarity", "kernel_components"], results.get("output_alignment_records", []))
    write_records_as_csv("{}/pair_metrics.csv".format(args.output_dir), ["activity", "ref", "sys", "metric_name", "metric_value"], results.get("pair_metrics", []))
    write_records_as_csv("{}/scores_by_activity.csv".format(args.output_dir), ["activity", "metric_name", "metric_value"], results.get("scores_by_activity", []) + audc_by_activity)
    write_records_as_csv("{}/scores_aggregated.csv".format(args.output_dir), [ "metric_name", "metric_value" ], results.get("scores_aggregated", []) + mean_audc)
    write_records_as_csv("{}/scores_by_activity_and_threshold.csv".format(args.output_dir), [ "activity", "score_threshold", "metric_name", "metric_value" ], results.get("scores_by_activity_and_threshold", []))

    if vars(args).get("dump_object_alignment_records", False):
        write_records_as_csv("{}/object_alignment.csv".format(args.output_dir), ["activity", "ref_activity", "sys_activity", "frame", "ref_object_type", "sys_object_type", "mapped_ref_object_type", "mapped_sys_object_type", "alignment", "ref_object", "sys_object", "sys_presenceconf_score", "kernel_similarity", "kernel_components"], results.get("object_frame_alignment_records", []))


def export_records(log, dm_records_rfa, dm_records_tfa, output_dir, plot_options):
    figure_dir = "{}/figures".format(output_dir)
    mkdir_p(figure_dir)
    log(1, "[Info] Saving figures to directory '{}'".format(figure_dir))

    dm_dir = "{}/dm".format(output_dir)
    mkdir_p(dm_dir)
    log(1, "[Info] Saving dm files to directory '{}'".format(dm_dir))

    def _export_records(records, prefix):
        if (len(records) > 0):
            dc_dict = records_to_dm(records)
            for activity, dc in dc_dict.items():
                dc.activity = activity
                dc.fa_label = prefix
                dc.fn_label = "PMISS"
                save_dm(dc, dm_dir, "{}_{}.dm".format(prefix, activity))
                log(1, "[Info] Plotting {} DET curve for {}".format(prefix, activity))
                plot_options['title'] = activity
                save_DET(dc, figure_dir, "DET_{}_{}.png".format(prefix, activity), plot_options)

            mean_label = "{}_mean_byfa".format(prefix)
            dc_agg = DataContainer.aggregate(dc_dict.values(), output_label=mean_label, average_resolution=500)
            dc_agg.activity = "AGGREGATED"
            dc_agg.fa_label = prefix
            dc_agg.fn_label = "PMISS"
            save_dm(dc_agg, dm_dir, "{}.dm".format(mean_label))
            log(1, "[Info] Plotting mean {} curve for {} activities".format(prefix, len(dc_dict.values())))
            save_DET(dc_agg, figure_dir, "DET_{}.png".format(mean_label), plot_options)
            log(1, "[Info] Plotting combined {} DET curves".format(prefix))
            plot_options['title'] = "All Activities"
            save_DET(dc_dict.values(), figure_dir, "DET_{}_{}.png".format(prefix, "COMBINED"), plot_options)
            plot_options['title'] = "All Activities and Aggregate"
            save_DET(list(dc_dict.values()) + [dc_agg], figure_dir, "DET_{}_{}.png".format(prefix, "COMBINEDAGG"), plot_options)

    _export_records(dm_records_rfa, "RFA")
    _export_records(dm_records_tfa, "TFA")

def records_to_dm(records):
    dc_dict = {}
    for activity, records in records.items():
        fa_array = [e[1] for e in records]
        fn_array = [e[2] for e in records]
        threshold = [e[0] for e in records]
        dc = DataContainer(fa_array, fn_array, threshold, label=activity)
        dc.line_options['color'] = None
        dc_dict[activity] = dc
    return dc_dict

def save_dm(dc, path, file_name):
    dc.dump("{}/{}".format(path, file_name))

def save_DET(dc, path, file_name, plot_options):
    if type(dc) is {}.values().__class__:
        dc = list(dc)
    if isinstance(dc, DataContainer):
        dc = [dc]
    rd = Render(plot_type="det")
    fig = rd.plot(dc, display=False, plot_options=plot_options)
    fig.savefig("{}/{}".format(path, file_name))
    rd.close_fig(fig)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scoring script for the NIST ActEV evaluation")

    subparsers = parser.add_subparsers(help="Scoring protocols.  Include the '-h' argument after the selected protocol to see it's usage (e.g. ActEV18_AD -h)")

    base_args = [[["-s", "--system-output-file"], dict(help="System output JSON file", type=str, required=True)],
                 [["-r", "--reference-file"], dict(help="Reference JSON file", type=str)],
                 [["-a", "--activity-index"], dict(help="Activity index JSON file", type=str, required=True)],
                 [["-f", "--file-index"], dict(help="file index JSON file", type=str, required=True)],
                 [["-t", "--det-point-resolution"], dict(help="Number of Unique confidence scores to use", type=int, default=0, required=False)],
                 [["-F", "--ignore-extraneous-files"], dict(help="Ignore system detection localizations for files not included in the file index", action="store_true")],
                 [["-m", "--ignore-missing-files"], dict(help="Ignore system detection localizations for files not included in the system output", action="store_true")],
                 [["-o", "--output-dir"], dict(help="Output directory for results", type=str)],
                 [["-d", "--disable-plotting"], dict(help="Disable DET Curve plotting of results", action="store_true")],
                 [["-v", "--verbose"], dict(help="Toggle verbose log output", action="store_true")],
                 [["-p", "--scoring-parameters-file"], dict(help="Scoring parameters JSON file", type=str)],
                 [["-V", "--validation-only"], dict(help="Only perform system output validation step", action="store_true")],
                 [["-P", "--prune-system-output"], dict(help=("Prune system output before processing it."), type=float)],
                 [["-i", "--ignore-no-score-regions"], dict(help="Don't discard instances which overlap no-score regions.", action="store_true", default=False)],
                 [["-n", "--processes-number"], dict(help="Number of processes to use to compute results", type=int, default=8)],
                 [["-c", "--plotting-parameters-file"], dict(help="Optional plotting options JSON file", type=str)],
                 [["-I", "--include-zero-ref-instances"], dict(help="Legacy behavior. Take into account `zero reference activity instances`", action="store_true")],
                 [["-S", "--skip-validation"], dict(help="Skip system output validation step", action="store_true", default=False)]]

    def add_protocol_subparser(name, kwargs, func, arguments):
        subp = subparsers.add_parser(name, **kwargs)
        for a, b in arguments:
            subp.add_argument(*a, **b)

        subp.set_defaults(func=func)
        return subp

    add_protocol_subparser("ActEV19_AD",
                           dict(help="Scoring protocol for the ActEV19 Activity Detection task"),
                           score_actev19_ad,
                           base_args)
    
    add_protocol_subparser("ActEV19_AD_V2",
                           dict(help="Scoring protocol for the ActEV19 V2 Activity Detection task"),
                           score_actev19_ad_v2,
                           base_args)

    add_protocol_subparser("ActEV_SDL_V1",
                           dict(help="Scoring protocol for the ActEV SDL V1 Activity Detection task"),
                           score_actev_sdl_v1,
                           base_args)
    
    add_protocol_subparser("ActEV_SDL_V2",
                           dict(help="Scoring protocol for the ActEV SDL V2 Activity Detection task"),
                           score_actev_sdl_v2,
                           base_args)
    
    add_protocol_subparser("ActEV_SDL_V2_PR",
                           dict(help="Scoring protocol for the ActEV SDL V2 Activity Detection task"),
                           score_actev_sdl_v2_pr,
                           base_args)
    
    add_protocol_subparser("ActEV18_AD",
                           dict(help="Scoring protocol for the ActEV18 Activity Detection task"),
                           score_actev18_ad,
                           base_args)

    add_protocol_subparser("ActEV18PC_AD",
                           dict(help="Scoring protocol for the ActEV18 Prize Challenge Activity Detection task"),
                           score_actev18pc_ad,
                           base_args)
    
    add_protocol_subparser("ActEV18_AD_TFA",
                           dict(help="Scoring protocol for the ActEV18 Activity Detection task with Temporal False Alarm"),
                           score_actev18_ad_tfa,
                           base_args)
    
    add_protocol_subparser("ActEV18_AD_1SECOL",
                           dict(help="Scoring protocol for the ActEV18 Activity Detection task with 1 Second Overlap Kernel Function"),
                           score_actev18_ad_1secol,
                           base_args)
    
    add_protocol_subparser("ActEV18_AOD",
                           dict(help="Scoring protocol for the ActEV18 Activity and Object Detection task"),
                           score_actev18_aod,
                           base_args + [[["-j", "--dump-object-alignment-records"], dict(help="Dump out per-frame object alignment records", action="store_true")]])

    add_protocol_subparser("ActEV18_AODT",
                           dict(help="Scoring protocol for the ActEV18 Activity and Object Detection and Tracking task"),
                           score_actev18_aodt,
                           base_args + [[["-j", "--dump-object-alignment-records"], dict(help="Dump out per-frame object alignment records", action="store_true")]])

    args = parser.parse_args()
    if args == argparse.Namespace():
        parser.parse_args(['-h'])
    args.func(args)
