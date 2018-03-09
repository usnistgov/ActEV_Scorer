# sed_kernel_components.py
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

def build_sed_presenceconf_congruence(sys_instances):
    if len(sys_instances) == 1:
        def _congruence(r, s):
            return 1.0
    elif len(sys_instances) > 1:
        sys_presence_confs = [ s.presenceConf for s in sys_instances ]
        min_presence_conf = min(sys_presence_confs)
        sys_conf_range = max(sys_presence_confs) - min_presence_conf

        if sys_conf_range == 0:
            def _congruence(r, s):
                return 1.0
        else:
            def _congruence(r, s):
                return float(s.presenceConf - min_presence_conf) / sys_conf_range
    else:
        def _congruence(r, s):
            return None

    return _congruence
