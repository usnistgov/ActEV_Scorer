def group_by_func(key_func, items, map_func = None):
    def _r(h, x):
        h.setdefault(key_func(x), []).append(x if map_func == None else map_func(x))
        return h

    return reduce(_r, items, {})

def dict_to_records(d, value_map = None):
    def _r(init, kv):
        k, v = kv
        for _v in v:
            init.append([k] + (_v if value_map == None else value_map(_v)))

        return init

    return reduce(_r, d.iteritems(), [])

def merge_dicts(a, b, conflict_func = None):
    def _r(init, k):
        if k in a:
            if k in b:
                init[k] = conflict_func(a[k], b[k]) if conflict_func else b[k]
            else:
                init[k] = a[k]
        else:
            init[k] = b[k]

        return init
    
    return reduce(_r, a.viewkeys() | b.viewkeys(), {})
