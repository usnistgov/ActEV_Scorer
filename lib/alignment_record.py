# alignment_record.py
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

from collections import namedtuple

def alignment_partitioner(init, ar):
    cd, md, fa = init
    if ar.alignment == "CD":
        cd.append(ar)
    elif ar.alignment == "MD":
        md.append(ar)
    elif ar.alignment == "FA":
        fa.append(ar)

    return init

class AlignmentRecord(namedtuple("ActivityRecord", ["ref",
                                                    "sys",
                                                    "kernel_similarity",
                                                    "kernel_components"])):
    __slots__ = ()

    @property
    def alignment(self):
        if self.ref == None:
            if self.sys == None:
                return "TN"
            else:
                return "FA"
        else:
            if self.sys == None:
                return "MD"
            else:
                return "CD"

    @property
    def sys_decision_score(self):
        if self.sys == None:
            return None
        else:
            return self.sys.decisionScore

    def iter_with_extended_properties(self):
        yield self.alignment
        yield self.ref
        yield self.sys
        yield self.sys_decision_score
        yield self.kernel_similarity
        yield self.kernel_components
