# sparse_signal.py
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

from operator import add, sub
from itertools import repeat

class SparseSignal(dict):
    def __init__(self, *args, **kwargs):
        super(SparseSignal, self).__init__(*args, **kwargs)

    def join(self, other, join_func, default = 0):
        out_signal = SparseSignal()

        self_val, other_val = default, default
        last_val = default

        for key in sorted(set(self.keys()) | set(other.keys())):
            self_val = self.get(key, self_val)
            other_val = other.get(key, other_val)

            new_val = join_func(self_val, other_val)
            if new_val != last_val:
                out_signal[key] = new_val
                last_val = new_val

        return out_signal

    def __add__(self, other):
        return self.join(other, add)

    def __and__(self, other):
        return self.join(other, min)

    def __or__(self, other):
        return self.join(other, max)

    def __sub__(self, other):
        return self.join(other, lambda a, b: a - min(a, b))

    def join_nd(self, other, n, op, default = 0):
        #print "other: " +str(other)
        #print "n: " +str(n)
        #print "op: "+str(op)
        def _r(init, _):
            #print "init "
            #print init
            #print lambda a, b: a.join(b, init, SparseSignal())
            return lambda a, b: a.join(b, init, SparseSignal())

        return reduce(_r, repeat(None, n - 1), lambda a, b: a.join(b, op, default))(self, other)

    def normalize(self):
        return self + {}

    def area(self):
        last_t, last_v = None, None
        area = 0

        for t in sorted(self.keys()):
            if last_t != None and last_v != None:
                if isinstance(last_v, SparseSignal):
                    area += (t - last_t) * last_v.area()
                else:
                    area += (t - last_t) * last_v

            last_t, last_v = t, self[t]

        return area

    def generate_collar(self, size):
        return reduce(lambda init, key: init | SparseSignal({key - size: 1, key + size: 0}),
                      self.normalize().keys(),
                      SparseSignal()).normalize()

    def iterate_by_frame(self, start, stop, default = 0):
        if start > stop:
            raise ValueError("Stop must be greater than or equal to start")

        n = start
        last_val = default
        sorted_keys = sorted(self.keys(), reverse=True)
        while n <= stop:
            while len(sorted_keys) > 0 and n >= sorted_keys[-1]:
                last_val = self[sorted_keys.pop()]

            yield (n, last_val)
            n += 1

    # This iterator is really intended for discrete time signals, but
    # won't enforce
    def on_steps(self, value_predicate, stepsize = 1):
        if len(self) > 0:
            sorted_keys = sorted(self.keys(), reverse=True)
            last_key = sorted_keys[0]
            n = sorted_keys[-1]
            while n <= last_key:
                while len(sorted_keys) > 0 and n >= sorted_keys[-1]:
                    last_val = self[sorted_keys.pop()]

                if value_predicate(last_val):
                    yield (n, last_val)

                n += stepsize
