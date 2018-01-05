#!/usr/bin/env python2

import sys
import os
import argparse
import json
import jsonschema

import pprint ###

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
sys.path.append(lib_path)

from alignment import *
from sed_kernel_components import *

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

# def group_by_fun(fun, inlist):
#     def _reducer(init, item):
#         init.setdefault(fun(item), []).append(item)
#         return init

#     return reduce(_reducer, inlist, {})
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Soring script for the NIST ActEV evaluation")
    parser.add_argument("-s", "--system-output-file", help="System output JSON file", type=str, required=True)
    parser.add_argument("-r", "--reference-file", help="Reference JSON file", type=str, required=True)
    parser.add_argument("-a", "--activity-index", help="Activity index JSON file", type=str, required=True)
    parser.add_argument("-f", "--file-index", help="file index JSON file", type=str, required=True)
    parser.add_argument("-v", "--verbose", help="Toggle verbose log output", action="store_true")
    args = parser.parse_args()

    verbosity_threshold = 1 if args.verbose else 0
    log = build_logger(verbosity_threshold)

    def _activity_instance_reducer(init, item):
        init.setdefault(item["activity"], {}).setdefault(item["localization"]["file"], []).append(item)
        return init
    
    log(1, "[Info] Loading system output file")
    system_output = load_json(args.system_output_file)
    system_output_activities = reduce(_activity_instance_reducer, system_output["activities"], {})
    
    log(1, "[Info] Loading reference file")
    reference = load_json(args.reference_file)
    reference_activities = reduce(_activity_instance_reducer, reference["activities"], {})

    log(1, "[Info] Loading activity index file")
    activity_index = load_json(args.activity_index)

    log(1, "[Info] Loading file index file")
    file_index = load_json(args.file_index)
    
    def _get_activity_instances(activity, filename, instances_dict):
        if activity in instances_dict:
            return instances_dict[activity].get(filename, [])
        else:
            return []

    def _alignment_reducer(init, activity_record):
        activity = activity_record["activity"]

        def _sub_reducer(init, filename):
            log(1, "[Info] Aligning activity {} in file {}".format(activity, filename))

            reference_activity_instances = _get_activity_instances(activity, filename, reference_activities)
            system_activity_instances = _get_activity_instances(activity, filename, system_output_activities)

            # According to SED eval plan delta_t is 10 seconds (seems
            # long?), not 10 frames
            delta_t = file_index[filename]["fps"] * 10
            sed_kernel = build_linear_combination_kernel([build_sed_time_overlap_filter(delta_t)],
                                                         [("time_congruence", 1.0e-8, sed_time_congruence),
                                                          ("decscore_congruence", 1.0e-6, build_sed_decscore_congruence(system_activity_instances))])
        
            correct, miss, fa = perform_alignment(reference_activity_instances,
                                                  system_activity_instances,
                                                  sed_kernel)

            for c in correct:
                init.append((activity, filename, "Correct") + c)
            for m in miss:                
                init.append((activity, filename, "Miss") + m)
            for f in fa:
                init.append((activity, filename, "FA") + f)

            return init

        return reduce(_sub_reducer, file_index.keys(), init)

    alignment_records = reduce(_alignment_reducer, activity_index, [])

    def _format_activity_instance(ai):
        if ai is None:
            return "None"
        else:
            return "{}[{}:{}]".format(ai["activityID"], ai["localization"]["beginFrame"], ai["localization"]["endFrame"])

    def _alignment_record_to_str(rec):
        activity, filename, alignment, r, s, sim, components = rec

        return "|".join((activity, filename, alignment, _format_activity_instance(r), _format_activity_instance(s), str(sim), str(components)))
        
    print "\n".join(map(_alignment_record_to_str, alignment_records))
