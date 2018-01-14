# Since JSON doesn't like integers as property list keys, we have to
# do that conversion.  This method assumes the localization parameter
# is a nested dictionary of the form { "<filename>": { "<frame_num>":
# value } }
def _localization_key_converter(localization):
    return { k: { int(_k): _v for _k, _v in v.iteritems() }
             for k, v in localization.iteritems() }

class ActivityInstance():
    def __init__(self, dictionary):
        self.activity = dictionary["activity"]
        self.activityID = dictionary["activityID"]
        self.decisionScore = dictionary.get("decisionScore", None)
        self.localization = _localization_key_converter(dictionary["localization"])
        if dictionary.has_key("objects"):
            self.objects = [ ObjectInstance(o) for o in dictionary["objects"] ]
        else:
            self.objects = None

    def __str__(self):
        if self.decisionScore == None:
            return "{}:{}".format(self.activity, self.activityID)
        else:
            return "{}:{}@{}".format(self.activity, self.activityID, self.decisionScore)

class ObjectInstance():
    def __init__(self, dictionary):
        self.objectType = dictionary["objectType"]
        self.objectID = dictionary["objectID"]
        self.localization = _localization_key_converter(dictionary["localization"])
