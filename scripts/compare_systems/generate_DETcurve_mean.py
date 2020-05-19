#!/usr/bin/env python3

# generate_DETcurve_mean.py
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
This script generates the DET curve of an activity from the corresponding DM
file, using the DMRender script.
Arguments:
* `-i, --input`: Directory of several Scorer outputs.
  Example: data/
              - System1/
                - figures/
                - dm/
                - etc
              - System2/
              - etc
* `-r, --reference`: Directory of several Scorer outputs used as references.
* `-a, --activity-index`: List of activities to plot DET curves for.
* `-o, --output`: Output directory to save plots.
* `-c, --curve-type`: Type of curve to plot (Default "DET", can also be "ROC").

N.B.: If you want custom labels for sumup DET curves (both sys and ref), you
can add a `label.txt` file in each folder. The content of the first line will
be used as the label for the corresponding curve.
"""

import argparse
import json
import os
import re

command = "python3 %s/../../lib/ActEV_DMRender.py -i %s --outputFolder \
%s --outputFileNameSuffix %s --plotType %s"
DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    # Creating CLI
    parser = argparse.ArgumentParser(description="DET curve generation script")
    parser.add_argument(
        '-i', '--input', help="Directory of several Scorer outputs",
        type=str, required=True)
    parser.add_argument(
        '-r', '--reference', help="Directory of the reference Scorer output",
        type=str, required=True)
    parser.add_argument(
        '-o', '--output', help="Output directory to save plots.",
        type=str, required=False, default='.')
    parser.add_argument(
        '-c', '--curve-type', help="Curve type.",
        type=str, required=False, default='DET')
    args = parser.parse_args()

    if not os.path.isdir(args.output):
        os.mkdir(args.output)

    out_path = args.output
    if not os.path.isdir(out_path):
        os.mkdir(out_path)

    systems = [os.path.join(args.input, thing)
                for thing in os.listdir(args.input)
                if os.path.isdir(os.path.join(args.input, thing))]

    rargs = []

    def get_label(path):
        try:
            with open(os.path.join(path, 'label.txt'), 'r') as f:
                label = f.readline().split('\n')[0]
            return label
        except Exception:  # no label.txt file
            if re.findall('/', path):
                candidate = path.split(os.path.sep)[-1]
                return candidate if candidate != '' \
                    else path.split(os.path.sep)[-2]
            else:
                return path

    for system in systems:
        dm_args = {}
        dm_args['path'] = os.path.join(system, 'dm', 'TFA_mean_byfa.dm')
        dm_args['label'] = get_label(system)
        dm_args['show_label'] = True
        plot_args = {'linewidth': 2, 'markersize': 24}
        rargs.append([dm_args, plot_args])
    # Adding references
    references = [os.path.join(args.reference, thing)
                    for thing in os.listdir(args.reference)
                    if os.path.isdir(os.path.join(args.reference, thing))]
    for reference in references:
        rargs.append([{
            'path': os.path.join(
                reference, 'dm', 'TFA_mean_byfa.dm'),
            'label': get_label(reference),
            'show_label': True}, {
                'linestyle': 'solid', 'marker': '.', 'markersize': 4}])

    # print(rargs)
    os.system(command % (DIR, '"%s"' % (str(rargs)), out_path,
                "mean_byfa", args.curve_type) +
                " --plotTitle mean_byfa")


if __name__ == '__main__':
    main()
