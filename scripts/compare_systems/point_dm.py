#!/usr/bin/env python3

# point_dm.py
# Author(s): Jesse Zhang

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

import argparse
import sys
sys.path.append('/Users/bnc8/Desktop/ActEV_Scorer/lib')
from datacontainer import DataContainer


def single_point_dm(fa_point, fn_point, threshold, file_name,
                    label=None, fa_label=None, fn_label=None):
    my_dm = DataContainer(fa_array=[fa_point], fn_array=[fn_point],
                          threshold=[threshold], label=label,
                          fa_label=fa_label, fn_label=fn_label)
    my_dm.validate_array_input()
    my_dm.dump(file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-fa", "--fa_point", action="store", type=float,
                        dest="fa_point")
    parser.add_argument("-fn", "--fn_point", action="store", type=float,
                        dest="fn_point")
    parser.add_argument("-t", "--threshold", action="store", type=float,
                        dest="threshold")
    parser.add_argument("-o", "--output", action="store", dest="output_file")
    parser.add_argument("-l", "--label", action="store", dest="label")
    parser.add_argument("-fal", "--fa_label", action="store", dest="fa_label")
    parser.add_argument("-fnl", "--fn_label", action="store", dest="fn_label")
    args = parser.parse_args()

    single_point_dm(fa_point=args.fa_point, fn_point=args.fn_point,
                    threshold=args.threshold, file_name=args.output_file,
                    label=args.label, fa_label=args.fa_label,
                    fn_label=args.fn_label)
