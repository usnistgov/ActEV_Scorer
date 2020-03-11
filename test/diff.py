#!/usr/bin/env python3

# diff.py
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

# Optional default_groups ensures the inclusion of the
# specified groups in the output dictionary

import sys
import os
import re


def main():
    # Checking arguments
    if len(sys.argv) != 3:
        sys.exit(1)
    ref_folder = sys.argv[1]
    out_folder = sys.argv[2]

    def eprint(fn, ln, rl, ol):
        print("""
            Difference found in file %s line %d.
                Expected: %s
                Found:    %s
            """ % (os.path.join(out_folder, fn), ln, rl, ol), file=sys.stderr)

    # Checking content
    # diff --exclude \*dm --exclude \*png -I "command" -I "git.commit" -r "$checkfile_outdir" "$compcheckfile_outdir"

    for file_name in os.listdir(ref_folder):
        # diff --exclude \*dm --exclude \*png --exclude \*log
        if os.path.isfile(file_name) and not re.match(r".*\.(dm|png|log)$", file_name):
            try:
                ref = open(os.path.join(ref_folder, file_name), 'r')
                out = open(os.path.join(out_folder, file_name), 'r')
                line_nbr = 1
                for ref_line in ref.readlines():
                    out_line = out.readline()
                    # diff -I "command" -I "git.commit"
                    if not re.match(r"[command|git\.commit]", ref_line):
                        if ref_line != out_line:
                            # it could be because of higher precision checking for
                            # floats
                            float_regex = r"[0-9]+\.[0-9]+"
                            if re.search(float_regex, out_line):
                                # rounding floats to 13 digits after comma
                                out_floats = re.findall(float_regex, out_line)
                                ref_floats = re.findall(float_regex, ref_line)
                                if len(out_floats) != len(ref_floats):
                                    eprint(file_name, line_nbr, ref_line, out_line)
                                    sys.exit(1)
                                for i in range(len(ref_floats)):
                                    if abs(round(float(ref_floats[i]), 11) - round(float(out_floats[i]), 11)) > 1e-09:
                                        eprint(file_name, line_nbr, ref_line, out_line)
                                        sys.exit(1)
                    line_nbr += 1
            except FileNotFoundError as e:
                print("Missing file {}".format(e.filename), file=sys.stderr)
                sys.exit(1)
            finally:
                ref.close()
                out.close()


if __name__ == "__main__":
    main()
