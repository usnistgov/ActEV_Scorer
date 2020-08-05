import argparse
import json

def create_parser():
    """Command line interface creation with arguments definition.
    Returns:
        argparse.ArgumentParser
    """
    input_help = ("help")

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_sys', help='SysOut JSON', type=str)
    parser.add_argument('-o', '--output_sys', help='Reduced SysOut JSON', type=str)
    parser.add_argument('-m', '--max_frames', help='The maximum number of frames of detected instances', type=int)
    parser.add_argument("-v", "--verbose", help="Display a message, otherwise report errors.", action="store_true")
    return parser

def get_dur(inst):
    """Returns video duration in frames."""
    for fil, sig in inst['localization'].items():
        ke = sorted([int(i) for i in sig.keys()], key = int)
        if (len(ke) != 2):
            print("Error: Instance has two ranges\n%s" % (str(inst)))
            exit(1)
        dur = ke[1] - ke[0]
        assert dur > 0, "Duration <= 0"
        return(dur)
    
if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    with open(args.input_sys) as json_file:
        data = json.load(json_file)

    ## Remove objects
    for inst in data['activities']:
        inst.pop('objects', None)

    ## Keep top max_frames of instances per activity. First make a list of the instances
    counts = {}
    for inst in data['activities']:
        act = inst['activity']
        dur = get_dur(inst)
        pconf = inst['presenceConf']
        if (act not in counts):
            counts[act] = { 'presconf': {} }
        if (pconf not in counts[act]['presconf'] ):
            counts[act]['presconf'][pconf] = []
        counts[act]['presconf'][pconf].append(dur)

    ### Report the counts
    for act, count in counts.items():
        count['num'] = 0
        count['dur_sum'] = 0
        spcl = sorted([float(i) for i in count['presconf'].keys()], reverse=True)
        count['min'] = spcl[-1]
        count['max'] = spcl[0]
        count['thresh'] = spcl[0] + 1
        count['thresh_num'] = 0
        count['thresh_dur'] = 0
        for pcl in spcl:
            count['num'] = count['num'] + len(count['presconf'][pcl])
            count['dur_sum'] = count['dur_sum'] + sum(count['presconf'][pcl])
            if (count['dur_sum'] < int(args.max_frames)):
                count['thresh'] = pcl
                count['thresh_num'] = count['num']
                count['thresh_dur'] = count['dur_sum']

    ### Rebuild the file
    act_cp = data['activities']
    data['activities'] = []
    for inst in act_cp:
        if (inst['presenceConf'] >= counts[inst['activity']]['thresh']):
            data['activities'].append(inst)

    ### Write the new JSON
    with open(args.output_sys, 'w') as outfile:
        json.dump(data, outfile)
