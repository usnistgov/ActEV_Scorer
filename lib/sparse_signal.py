from operator import add, sub

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
        return self.join(self & other, sub)

    def normalize(self):
        return self + {}

    def area(self):
        last_t, last_v = None, None
        area = 0

        for t in sorted(self.keys()):
            if last_t != None and last_v != None:
                area += (t - last_t) * last_v
            last_t, last_v = t, self[t]

        return area

    def generate_collar(self, size):
        return reduce(lambda init, key: init | SparseSignal({key - size: 1, key + size: 0}),
                      self.normalize().keys(),
                      SparseSignal()).normalize()

