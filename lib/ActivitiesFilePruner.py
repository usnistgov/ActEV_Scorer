import json


def prune(sysout: str, percentage: int, fi: dict, log) -> dict:
    """
    Prune a system output. Keeps `percentage` % of the selected frames.
    Use the file-index `fi` to know the total frame number.
    Return the pruned sysout.
    """
    max_frames = 0
    for _fn, data in fi.items():
        f_n = [int(i) for i in sorted(list(data['selected'].keys()))]
        max_frames += f_n[1] - f_n[0] + 1
    max_frames = int(max_frames * percentage)

    with open(sysout) as json_file:
        data = json.load(json_file)

    # Remove objects and find minmax
    min_p = 1
    max_p = 0
    for inst in data['activities']:
        inst.pop('objects', None)
        if inst['presenceConf'] < min_p:
            min_p = inst['presenceConf']
        if inst['presenceConf'] > max_p:
            max_p = inst['presenceConf']

    def _get_dur(inst):
        """Returns activity instance duration in frames."""
        for fil, sig in inst['localization'].items():
            ke = sorted([int(i) for i in sig.keys()], key=int)
            if (len(ke) != 2):
                log(0, "Error: Instance has two ranges\n%s" % (str(inst)))
                exit(1)
            dur = ke[1] - ke[0]
            assert dur > 0, "Duration <= 0"
            return(dur)

    # Keep  of instances per activity. First make a list of the instances
    counts = {}
    for inst in data['activities']:
        act = inst['activity']
        dur = _get_dur(inst)
        pconf = inst['presenceConf']
        if (act not in counts):
            counts[act] = {'presconf': {}}
        if (pconf not in counts[act]['presconf']):
            counts[act]['presconf'][pconf] = []
        counts[act]['presconf'][pconf].append(dur)

    # Report the counts
    for _act, count in counts.items():
        count['num'] = 0
        count['dur_sum'] = 0
        spcl = sorted(
            [float(i) for i in count['presconf'].keys()], reverse=True)
        count['min'] = spcl[-1]
        count['max'] = spcl[0]
        count['thresh'] = spcl[0] + 1
        for pcl in spcl:
            count['num'] = count['num'] + len(count['presconf'][pcl])
            count['dur_sum'] = count['dur_sum'] + sum(count['presconf'][pcl])
            if (count['dur_sum'] < max_frames):
                count['thresh'] = pcl
                count['thresh_num'] = count['num']
                count['thresh_dur'] = count['dur_sum']
        log(1, "{} reduction={:f} tot_n={:d} thresh(num,dur,presc)=({:d},{:d},{:f}) presC(min,dur_sum,max)=({:f},{:d},{:f})".format(
            _act, ((count['num'] - count['thresh_num']) / count['num']),
            count['num'], count['thresh_num'], count['thresh_dur'],
            count['thresh'], count['min'], count['dur_sum'],
            count['max']))

    # Rebuild the file
    act_cp = data['activities']
    data['activities'] = []
    for inst in act_cp:
        if (inst['presenceConf'] >= counts[inst['activity']]['thresh']):
            data['activities'].append(inst)

    return [data, [min_p, max_p]]
