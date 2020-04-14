#!/usr/bin/env python3

# reduce.py
# Author(s): Baptiste Chocot

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

"""
This script needs two reference files (or *system outputs*) and a file index.
For these three given files, it will rewrite them with a reduced
`filesProcessed` list. Only files found in the three files will be kept. The
three output files will be written in the specified output directory (likely
`<file>.sysout.json`).
"""

import json
import sys
import threading
import re
import os


def _get_processed_files(file, output, data):
    """
    Fill the array :param output: with strings stored in
    :param file:['filesProcessed'] and `data` with :param file:['activities'].
    """
    with open(file, 'r') as f:
        fdata = json.load(f)
        data['filesProcessed'] = fdata['filesProcessed']
        data['activities'] = fdata['activities']
        del fdata
        files = data['filesProcessed']
        for fn in files:
            output.append(fn)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(
            "usage: {} <ref_file_A> <ref_file_B> <file_index> "
            "<output_dir>".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    ref_file_A = sys.argv[1]
    ref_file_B = sys.argv[2]
    file_index = sys.argv[3]
    output_dir = sys.argv[4]
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # Defining filenames
    out_A = os.path.join(output_dir, ref_file_A.split(os.path.sep)[-1])
    out_A = re.sub(r'json$', 'reduced.json', out_A) if re.search(
        r'json$', out_A) else out_A + '.reduced'
    out_B = os.path.join(output_dir, ref_file_B.split(os.path.sep)[-1])
    out_B = re.sub(r'json$', 'reduced.json', out_B) if re.search(
        r'json$', out_B) else out_B + '.reduced'
    out_F = os.path.join(output_dir, 'file-index.reduced.json')

    # Loading all processed files
    file_list_A = []
    file_list_B = []
    data_A = {}
    data_B = {}

    t_A = threading.Thread(
        target=_get_processed_files, args=(ref_file_A, file_list_A, data_A))
    t_B = threading.Thread(
        target=_get_processed_files, args=(ref_file_B, file_list_B, data_B))
    t_A.start()
    t_B.start()
    t_A.join()
    t_B.join()

    # Finding common filenames
    is_fz_larger = len(file_list_A) > len(file_list_B)
    common_files = [
        f for f in (file_list_A if is_fz_larger else file_list_B) if
        f in ((file_list_B if is_fz_larger else file_list_A))
    ]

    # Removing files not in file-index
    with open(file_index, 'r') as fi:
        fi_data = json.load(fi)

    for fn in common_files.copy():
        if fn not in fi_data.keys():
            common_files.remove(fn)

    # Updating `filesProcessed` and `activities` for each reference file
    data_A['filesProcessed'] = common_files
    copy = data_A['activities'].copy()
    for act in copy:
        filename = list(act['localization'].keys())[0]
        if filename not in common_files:
            data_A['activities'].remove(act)
    with open(out_A, 'w') as f:
        json.dump(data_A, f, indent=4)
    del data_A

    data_B['filesProcessed'] = common_files
    copy = data_B['activities'].copy()
    for act in copy:
        filename = list(act['localization'].keys())[0]
        if filename not in common_files:
            data_B['activities'].remove(act)
    with open(out_B, 'w') as f:
        json.dump(data_B, f, indent=4)
    del data_B
    del copy

    # Updating file index
    fi_data_copy = fi_data.copy()
    for file_name in fi_data:
        if file_name not in common_files:
            del fi_data_copy[file_name]
    # Here the copy contains all entries from file-index.json which are in
    # common with both refs
    with open(out_F, 'w') as nfi:
        json.dump(fi_data_copy, nfi, indent=4)

    print('Done.')
