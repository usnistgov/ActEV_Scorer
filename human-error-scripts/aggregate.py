#!/usr/bin/env python3

# aggregate.py
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
This script scans a folder and gather all JSON files it finds. It tries then to
merge them into a single file. Every JSON file which does not repect the
following format will be ignored.
"""

import argparse
import json
import sys
import os
import re


def read_folder(folder: str, recursive=True) -> list:
    """
    Return a list of all JSON files in a folder.
    """
    files = []
    for o in os.listdir(folder):
        obj = os.path.join(folder, o)
        if os.path.isfile(obj) and re.findall(r'\.json$', o):
            files.append(obj)
        elif os.path.isdir(obj) and recursive:
            files += read_folder(obj)
    return files


if __name__ == '__main__':
    # Creating CLI
    parser = argparse.ArgumentParser(
        description="JSON aggregating script for the NIST ActEV evaluation")
    parser.add_argument(
        '-d', '--directory', help="Directory in which JSON will be read.",
        type=str, required=True)
    parser.add_argument(
        '-o', '--output', help="File in which aggregation will be stored.",
        type=str, required=True)
    parser.add_argument(
        '-r', '--recursive', help="Search recursively for JSON files.",
        action="store_true")
    args = parser.parse_args()

    # Gathering JSON files
    print("Reading {}".format(args.directory))
    files = read_folder(args.directory, args.recursive)

    # Aggregating files
    print("Trying to aggregate {} files".format(len(files)))
    ignored = 0
    out = {"activities": [], "filesProcessed": []}
    for jf in files:
        try:
            with open(jf, 'r') as jfs:
                content = json.load(jfs)
                out["activities"] += content["activities"]
                out["filesProcessed"].append(content["filesProcessed"])
        except KeyError:
            ignored += 1
            continue
    file_nbr = len(files) - ignored
    print("Writing results ({} files aggregated)...".format(file_nbr))
    with open(args.output, 'w') as outf:
        json.dump(out, outf, indent=4)
        outf.write('\n')
    print("Done.")
