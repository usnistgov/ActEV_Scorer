# plot.py
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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scipy.stats import norm

def _make_clamp(_min, _max):
    def clamp(n):
        if n < _min:
            return _min
        elif n > _max:
            return _max
        else:
            return n

    return clamp

def det_curve(points_dict, out_fn, typ="standard"):
    ytick_values = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999]
    ytick_labels = [ str(y * 100) for y in ytick_values ]
    ytick = norm.ppf(ytick_values)

    # norm.ppf for 0 and 1 is -inf and inf respectively, so we clamp
    # those values to something reasonably smaller/larger than the
    # min/max yticks so that matplotlib can plot them, but they won't
    # be shown in the plot view
    clamp = _make_clamp(ytick[0] - 10, ytick[-1] + 10)

    xtick_values = [0.01, 0.1, 1, 10]

    plt.figure(num=0, figsize=(7, 6.5), dpi=240)
    for k, points in sorted(points_dict.items()):
        plt.plot([ x for ds, x, y in points ], [ clamp(norm.ppf(y)) for ds, x, y in points ], label = k)

    # Need the following line for matplotlib 1.5.1.  Without explicit
    # limits, matplotlib attempts to infer them from the data, but if
    # all xvalues are 0, a ValueError is raised when trying to set
    # xscale
    plt.xlim(xtick_values[0], xtick_values[-1])
    plt.ylim(ytick_values[0], ytick_values[-1])

    plt.xscale("log")
    plt.xticks(xtick_values, map(str, xtick_values))

    plt.yticks(ytick, ytick_labels)

    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, fontsize='small')
    if typ=="tfa":
        plt.xlabel("Time-Based False Alarm (%)")
    else:
        plt.xlabel("Rate of false alarm (per minute)")
    plt.ylabel("Probability of missed detection")

    plt.savefig(out_fn, bbox_inches="tight")
    plt.close()
