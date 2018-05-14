# helpers.py
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

# Optional default_groups ensures the inclusion of the
# specified groups in the output dictionary
def group_by_func(key_func, items, map_func = None, default_groups = None):
    def _r(h, x):
        h.setdefault(key_func(x), []).append(x if map_func == None else map_func(x))
        return h

    grouped = reduce(_r, items, {})
    if default_groups is None:
        return grouped
    else:
        return merge_dicts({ k: [] for k in default_groups }, grouped)

def dict_to_records(d, value_map = None):
    def _r(init, kv):
        k, v = kv
        for _v in v:
            init.append([k] + (_v if value_map == None else value_map(_v)))

        return init

    return reduce(_r, d.iteritems(), [])

def merge_dicts(a, b, conflict_func = None):
    def _r(init, k):
        if k in a:
            if k in b:
                init[k] = conflict_func(a[k], b[k]) if conflict_func else b[k]
            else:
                init[k] = a[k]
        else:
            init[k] = b[k]

        return init

    return reduce(_r, a.viewkeys() | b.viewkeys(), {})

def identity(x):
    return x
