import json
import argparse


def boundingbox_merge(my_data):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", action="store", dest="fin_path")
    parser.add_argument("-o", "--output", action="store", dest="fout_path")
    args = parser.parse_args()
    with open(args.fin_path) as f:
        my_json = json.load(f)
    output_json = boundingbox_merge(my_json)
    with open(args.fout_path, 'w') as json_file:
        json.dump(output_json, json_file, indent=2, sort_keys=True)
