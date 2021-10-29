# actev18_aod.py
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

import sys
import os
import subprocess
from functools import reduce
import dill
from concurrent.futures import ProcessPoolExecutor
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
sys.path.append(lib_path)

from operator import add

from metrics import *
from alignment_record import *
from actev_kernel_components import *
from sed_kernel_components import *
from alignment import *
from helpers import *
from srl_aod_v1 import *


class SRL_AOD_V2(SRL_AOD_V1):
    def __init__(self, scoring_parameters, file_index, activity_index, command):
        default_scoring_parameters = { "activity.epsilon_temporal_congruence": 1.0e-8,
                                       "activity.epsilon_presenceconf_congruence": 1.0e-6,
                                       "activity.temporal_overlap_delta": 0.2,
                                       "activity.p_miss_at_rfa_targets": [ 1, 0.2, 0.15, 0.1, 0.03, 0.01 ],
                                       "activity.n_mide_at_rfa_targets": [ 1, 0.2, 0.15, 0.1, 0.03, 0.01 ],
                                       "nmide.ns_collar_size": 0,
                                       "nmide.cost_miss": 1,
                                       "nmide.cost_fa": 1,
                                       "activity.epsilon_object_congruence": 1.0e-10,
                                       "activity.object_congruence_delta": 0.0,
                                       "wpmiss.numerator": 8,
                                       "wpmiss.denominator": 10,
                                       "object.epsilon_object-overlap_congruence": 1.0e-8,
                                       "object.epsilon_presenceconf_congruence": 1.0e-6,
                                       "object.spatial_overlap_delta": 0.5,
                                       "object.p_miss_at_rfa_targets": [ 0.5, 0.2, 0.1, 0.033 ],
                                       "mode.cost_miss": 1,
                                       "mode.cost_fa": 1,
                                       "scoring_protocol": "srl_aod_v2",
                                       "command": str(command),
                                       "git.commit": subprocess.check_output(["git", "--git-dir="+ os.path.join(lib_path, "../")+".git", "show", "--oneline", "-s", "--no-abbrev-commit","--pretty=format:%H--%aI"]).strip()}
        scoring_parameters = merge_dicts(default_scoring_parameters, scoring_parameters)
        super(SRL_AOD_V2, self).__init__(scoring_parameters, file_index, activity_index, command)
