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
                return "FP"
        else:
            if self.sys == None:
                return "FN"
            else:
                return "TP"

    def iter_with_extended_properties(self):
        yield self.alignment
        for x in self:
            yield x
