# activity_instance.py
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

from sparse_signal import SparseSignal as S

# Since JSON doesn't like integers as property list keys, we have to
# do that conversion.  This method assumes the localization parameter
# is a nested dictionary of the form { "<filename>": { "<frame_num>":
# value } }
def _localization_key_converter(localization, value_mapper = lambda x: x):
    return { k: { int(_k): value_mapper(_v) for _k, _v in v.iteritems() }
             for k, v in localization.iteritems() }

def _bounding_box_to_signal(bounding_box):
    x, y, w, h = map(lambda e: bounding_box[e], ("x", "y", "w", "h"))
    return S({x: S({y: 1, y + h: 0}), x + w: S()})

def _build_object_frame_wconf_mapper(obj_type, obj_id):
    def _object_frame_wconf_mapper(obj):
        if len(obj) == 0:
            return ObjectLocalizationFrame.empty()
        else:
            return ObjectLocalizationFrame(obj["boundingBox"], obj.get("presenceConf", None), obj_type, obj_id)

    return _object_frame_wconf_mapper

class ActivityInstance():
    def __init__(self, dictionary, load_objects = False):
        self.activity = dictionary["activity"]
        self.activityID = dictionary["activityID"]
        self.presenceConf = dictionary.get("presenceConf", None)
        self.localization = _localization_key_converter(dictionary["localization"])
        if load_objects and dictionary.has_key("objects"):
            self.objects = [ ObjectInstance(o) for o in dictionary["objects"] ]
        else:
            self.objects = None

    def __str__(self):
        return str(self.activityID)

class ObjectInstance():
    def __init__(self, dictionary):
        self.objectType = dictionary["objectType"]
        self.objectID = dictionary["objectID"]
        self.localization = _localization_key_converter(dictionary["localization"], _build_object_frame_wconf_mapper(self.objectType, self.objectID))

class ObjectLocalizationFrame():
    def __init__(self, bounding_box, conf, obj_type, obj_id):
        self.spatial_signal = _bounding_box_to_signal(bounding_box) if bounding_box else S()
        self.presenceConf = conf
        self.objectType = obj_type
        self.objectID = obj_id

    def __str__(self):
        return str(self.objectID)

    @classmethod
    def empty(cls):
        return cls(None, None, None, None)
