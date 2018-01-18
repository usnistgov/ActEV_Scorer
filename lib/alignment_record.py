from collections import namedtuple

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
