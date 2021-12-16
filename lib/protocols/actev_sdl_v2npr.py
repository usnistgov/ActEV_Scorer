# actev_sdl_v2.py
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
import dill
from concurrent.futures import ProcessPoolExecutor

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
sys.path.append(lib_path)

from metrics import *
from alignment_record import *
from actev_kernel_components import *
from sed_kernel_components import *
from alignment import *
from helpers import *
from default import *
from actev_sdl_v2 import *

class ActEV_SDL_V2NPR(ActEV_SDL_V2):
    @classmethod
    def get_schema_fn(cls):
        return "actev_sdl_v2npr_schema.json"

    def __init__(self, scoring_parameters, file_index, activity_index, command):
        default_scoring_parameters = { "activity.epsilon_presenceconf_congruence": 1.0,
                                       "activity.temporal_overlap_delta": 0.5,
                                       "activity.p_miss_at_rfa_targets":   [ 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.50, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01 ],
                                       "activity.auc_at_fa_targets":       [ 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.50, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01 ],
                                       "activity.w_p_miss_at_rfa_targets": [ 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.50, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01 ],
                                       "activity.n_mide_at_rfa_targets":   [ 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.50, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01 ],
                                       "activity.fa_at_rfa_targets":       [ 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.50, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01 ],
                                       "nmide.ns_collar_size": 0,
                                       "nmide.cost_miss": 1,
                                       "nmide.cost_fa": 1,
                                       "wpmiss.numerator": 8,
                                       "wpmiss.denominator": 10,
                                       "fa.ns_collar_size": 0,
                                       "scoring_protocol": "actev_sdl_v2npr",
                                       "command": str(command),
                                       "git.commit": subprocess.check_output(["git", "--git-dir="+ os.path.join(lib_path, "../")+".git", "show", "--oneline", "-s", "--no-abbrev-commit","--pretty=format:%H--%aI"]).strip()} #.split(" ")[0]} #git show --oneline -s --no-abbrev-commit --pretty=format:%H--%aI

        scoring_parameters = merge_dicts(default_scoring_parameters, scoring_parameters)
        super(ActEV_SDL_V2, self).__init__(scoring_parameters, file_index, activity_index, command)

        self.file_framedur_lookup = { k: S({ int(_k): _v for _k, _v in v["selected"].items() }).area() for k, v in file_index.items() }
        self.total_file_duration_minutes = sum([ float(frames) / file_index[k]["framerate"] for k, frames in self.file_framedur_lookup.items()]) / float(60)
        self.file_framerate = [file_index[k]["framerate"] for k, v in file_index.items()][0]
