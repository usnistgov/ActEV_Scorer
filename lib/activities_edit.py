import json
import argparse
import copy


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", action="store", dest="fin_path")
    parser.add_argument("-o", "--output", action="store", dest="fout_path")
    parser.add_argument("-t", "--type", action="store", dest="aggregation_type")
    args = parser.parse_args()
    with open(args.fin_path) as f:
        my_json = json.load(f)
    aggre_type = args.aggregation_type
    if aggre_type not in ['frame', 'activity']:
        aggre_type = 'frame'
    output_json = boundingbox_merge(my_json, aggre_type)
    with open(args.fout_path, 'w') as json_file:
        json.dump(output_json, json_file, indent=2, sort_keys=True)
