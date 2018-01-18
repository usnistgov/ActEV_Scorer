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
