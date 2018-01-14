def build_sed_time_overlap_filter(delta_t = 10):
    def _filter(r, s):
        s_bf, s_ef = s["localization"]["beginFrame"], s["localization"]["endFrame"]
        s_mid = s_bf + (s_ef - s_bf) / 2.0

        if s_mid > r["localization"]["beginFrame"] - delta_t and s_mid < r["localization"]["endFrame"] + delta_t:
            return True
        else:
            return False

    return _filter

def sed_time_congruence(r, s):
        return float(min(r["localization"]["endFrame"], s["localization"]["endFrame"]) -
                     max(r["localization"]["beginFrame"], s["localization"]["beginFrame"])) / max(1.0/25, r["localization"]["endFrame"] - r["localization"]["beginFrame"])

def build_sed_decscore_congruence(sys_instances):
    if len(sys_instances) == 1:
        def _congruence(r, s):
            return 1.0
    elif len(sys_instances) > 1:
        sys_dec_scores = [ s.decisionScore for s in sys_instances ]
        min_dec_score = min(sys_dec_scores)
        sys_dec_range = max(sys_dec_scores) - min_dec_score
        
        def _congruence(r, s):
            return float(s.decisionScore - min_dec_score) / sys_dec_range
    else:
        def _congruence(r, s):
            return None

    return _congruence
