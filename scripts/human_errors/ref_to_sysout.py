#!/usr/bin/env python3

# ref_to_sysout.py
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
This script turns a reference file into a *system output*-like file. The output
file will be stored in the same directory than the input file.
"""

import sys
import os
import json
import re


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: {} <ref_json_file>".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    ref_file_name = sys.argv[1]
    output = re.sub(r'json$', 'sysout.json', ref_file_name) if re.search(
        r'json$', ref_file_name) else ref_file_name + '.reduced'

    with open(ref_file_name, 'r') as rf:
        data = json.load(rf)
    # Creating sysout file according to references
    sysout = {}
    sysout['filesProcessed'] = data['filesProcessed']
    activities = []
    for ref_act in data['activities']:
        act = {}
        act['activity'] = ref_act['activity']
        act['activityID'] = ref_act['activityID']
        act['presenceConf'] = 1.0
        act['alertFrame'] = 1
        act['localization'] = ref_act['localization']
        activities.append(act)
    sysout['activities'] = activities

    with open(output, 'w') as of:
        json.dump(sysout, of, indent=4)

    print('Done.')
