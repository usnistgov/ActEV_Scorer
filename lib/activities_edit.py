import json
import argparse
import sys
import os
import pandas as pd
lib_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../../lib")
sys.path.append(lib_path)
from sparse_signal import SparseSignal as ss
import metrics


def boundingbox_merge(my_data, aggre_type):
    if aggre_type == 'activity':
        for i in range(0, len(my_data['activities'])):
            loc_id = list(my_data['activities'][i]['localization'].keys())[0]
            start_end_frames = [int(i) for i in my_data['activities'][i]['localization'][loc_id].keys()]
            start_end_frames.sort()
            start_frame = start_end_frames[0]
            end_frame = start_end_frames[1]
            width_set = set()
            height_set = set()
            x_set = set()
            y_set = set()
            for j in range(0, len(my_data['activities'][i]['objects'])):
                sig_frames = my_data['activities'][i]['objects'][j]['localization'][loc_id].keys()
                for k in sig_frames:
                    frame_info = my_data['activities'][i]['objects'][j]['localization'][loc_id][k]
                    if frame_info != {}:
                        bb_info = frame_info['boundingBox']
                        width_set.add(int(bb_info['w'])+int(bb_info['x']))
                        height_set.add(int(bb_info['h'])+int(bb_info['y']))
                        x_set.add(int(bb_info['x']))
                        y_set.add(int(bb_info['y']))

            # grab proper bounding box values
            if len(my_data['activities'][i]['objects']) > 0:
                min_x = min(x_set)
                min_y = min(y_set)
                max_w = max(width_set)
                max_h = max(height_set)
                max_w = max_w - min_x
                max_h = max_h - min_y

                # rebuild the json entry
                my_data['activities'][i]['objects'][0]['localization'][loc_id] =\
                    {str(start_frame): {'boundingBox': {'h': max_h, 'w': max_w, 'x': min_x, 'y': min_y}},
                     str(end_frame): {}}
                my_data['activities'][i]['objects'][0]['objectType'] = 'Other'

                # Destroy stray objects
                while len(my_data['activities'][i]['objects']) > 1:
                    my_data['activities'][i]['objects'].pop(1)

        return my_data
    elif aggre_type == 'frame':
        for i in range(0, len(my_data['activities'])):
            loc_id = list(my_data['activities'][i]['localization'].keys())[0]
            start_end_frames = [int(i) for i in my_data['activities'][i]['localization'][loc_id].keys()]
            start_end_frames.sort()
            start_frame = start_end_frames[0]
            end_frame = start_end_frames[1]

            if len(my_data['activities'][i]['objects']) > 1:
                object_dict_list = {}
                for j in range(0, len(my_data['activities'][i]['objects'])):
                    object_dict_list[j] = {}
                    for k in range(start_frame, end_frame):
                        if str(k) in my_data['activities'][i]['objects'][j]['localization'][loc_id]:
                            if 'boundingBox' in my_data['activities'][i]['objects'][j]['localization'][loc_id][str(k)]:
                                object_dict_list[j][k] = my_data['activities'][i]['objects'][j]['localization'][loc_id][str(k)]['boundingBox']
                            else:
                                object_dict_list[j][k] = {}
                        elif k == start_frame and str(k) not in my_data['activities'][i]['objects'][j]['localization'][loc_id]:
                            object_dict_list[j][k] = {}
                        elif k > start_frame:
                            object_dict_list[j][k] = object_dict_list[j][k-1]

                # Build combined frames from all objects
                frames_dict = {}
                last_active_frame = {}
                for m in range(start_frame, end_frame):
                    width_set = set()
                    height_set = set()
                    x_set = set()
                    y_set = set()
                    for n in range(0, len(object_dict_list)):
                        if object_dict_list[n][m] != {}:
                            width_set.add(int(object_dict_list[n][m]['w']) + int(object_dict_list[n][m]['x']))
                            height_set.add(int(object_dict_list[n][m]['h']) + int(object_dict_list[n][m]['y']))
                            x_set.add(int(object_dict_list[n][m]['x']))
                            y_set.add(int(object_dict_list[n][m]['y']))
                    if x_set:
                        min_x = min(x_set)
                        min_y = min(y_set)
                        max_w = max(width_set)
                        max_h = max(height_set)
                        max_w = max_w - min_x
                        max_h = max_h - min_y
                        frame_entry = {'boundingBox': {'h': max_h, 'w': max_w, 'x': min_x, 'y': min_y}}
                        if last_active_frame != frame_entry:
                            frames_dict[str(m)] = frame_entry
                            last_active_frame = frame_entry
                frames_dict[str(end_frame)] = {}
                my_data['activities'][i]['objects'][0]['localization'][loc_id] = frames_dict

            if len(my_data['activities'][i]['objects']) > 0:
                my_data['activities'][i]['objects'][0]['objectType'] = 'Other'

                # Destroy stray objects
                while len(my_data['activities'][i]['objects']) > 1:
                    my_data['activities'][i]['objects'].pop(1)

        return my_data
    elif aggre_type == 'unique':
        my_df = pd.DataFrame(columns=['activity', 'activityID', 'clipID'])
        my_data = my_json
        my_key_dict = dict()
        for i in range(0, len(my_data['activities'])):
            video_key = list(my_data['activities'][i]['localization'].keys())[0]
            norm_frames = list(my_data['activities'][i]['localization'][video_key])
            norm_frames.sort()
            norm_frames = [int(i) for i in norm_frames]
            temporal_padding = min(150, max((norm_frames[1]-norm_frames[0]), 60))
            active_frames = dict()
            if norm_frames[0] - temporal_padding < 0:
                active_frames['0'] = 1
            else:
                active_frames[str(norm_frames[0]-temporal_padding)] = 1
            active_frames[str(norm_frames[1]+temporal_padding)] = 0
            active_frames = ss(active_frames)
            activity = my_data['activities'][i]['activity']
            if activity in my_key_dict:
                my_key_dict[activity] = my_key_dict[activity] + active_frames
            else:
                my_key_dict[activity] = active_frames
        for j in range(0, len(my_data['activities'])):
            video_key = list(my_data['activities'][j]['localization'].keys())[0]
            norm_frames = list(my_data['activities'][j]['localization'][video_key])
            norm_frames.sort()
            norm_frames = [int(i) for i in norm_frames]
            temporal_padding = min(150, max((norm_frames[1] - norm_frames[0]), 60))
            active_frames = dict()
            if norm_frames[0] - temporal_padding < 0:
                active_frames['0'] = 1
            else:
                active_frames[str(norm_frames[0] - temporal_padding)] = 1
            active_frames[str(norm_frames[1] + temporal_padding)] = 0
            active_frames = list(active_frames)
            activity = my_data['activities'][j]['activity']
            activ_keys = list(my_key_dict[activity].keys())
            activ_keys = [int(i) for i in activ_keys]
            activ_keys.sort()
            activ_bool_list = [int(active_frames[1]) > i > int(active_frames[0]) for i in activ_keys]
            if all(flg is False for flg in activ_bool_list) and \
                    my_key_dict[activity][active_frames[0]] == 1 and \
                    my_key_dict[activity][active_frames[1]] == 0:
                act_id = my_data['activities'][j]['activityID']
                my_df = my_df.append({'activity': activity, 'activityID': act_id, 'clipID': video_key},
                               ignore_index=True)
        return my_df



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", action="store", dest="fin_path")
    parser.add_argument("-o", "--output", action="store", dest="fout_path")
    parser.add_argument("-t", "--type", action="store", dest="aggregation_type")
    args = parser.parse_args()

    with open(args.fin_path) as f:
        my_json = json.load(f)
    aggre_type = args.aggregation_type
    if aggre_type not in ['frame', 'activity', 'unique']:
        aggre_type = 'frame'
    if aggre_type in ['frame', 'activity']:
        output_json = boundingbox_merge(my_json, aggre_type)
        with open(args.fout_path, 'w') as json_file:
            json.dump(output_json, json_file, indent=2, sort_keys=True)
    if aggre_type in ['unique']:
        output_csv = boundingbox_merge(my_json, aggre_type)
        output_csv.to_csv(path_or_buf=args.fout_path)

