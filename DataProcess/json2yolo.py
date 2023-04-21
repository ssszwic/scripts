import json
import glob
import os
from tqdm import tqdm
import argparse

label_dict = {
    'revetmentAircraft_1': 0,
    'revetmentAircraft_2': 1,
    'revetmentAircraft_3': 2,
    'revetmentAircraft_4': 3,
    'revetmentAircraft_5': 4,
    'revetmentAircraft_6': 5,
    'revetmentAircraft_7': 6,
    'revetmentAircraft_8': 7,
    'specialAircraft': 8,
    'oilTank': 9,
    'fighter': 10,
    'Damage_revetmentAircraft': 11,
    'Damage_airstript': 12,
    'helicopter': 13,
    'specialPlane_1': 14,
    'specialPlane_2': 15,
    'specialPlane_3': 16,
    'AircraftBuilding_1': 17,
    'AircraftBuilding_2': 18,
    'AircraftBuilding_3': 19,
    'parkingApron_H': 20,
    'parkingApron_C': 21,
    'parkingApron_S': 22,
    'parkingApron_R': 23,
    'parkingApron_X': 24,
}

def get_base_name(full_names):
    """
    去掉前缀和后缀，支持列表和变量
    :param full_names: 文件的全名 '/DataProcess/big_cut.py'
    :return name: 文件的基础名 'big_cut'
    """
    if isinstance(full_names, list):
        names = []
        for full_name in full_names:
            _, long_name = os.path.split(full_name)
            name, _, = os.path.splitext(long_name)
            names.append(name)
        return names
    else:
        _, long_name = os.path.split(full_names)
        name, _, = os.path.splitext(long_name)
        return name

def read_json(file_name):
    """
    读取label信息
    :param file_name: 标签文件的路径
    :param type: 标签文件的类型,目前只支持labelme生成的json文件
    :return labels: 标签文件中所有标签的列表,字符串格式
    :return points: 标签文件中每个框的位置,[[[xmin, ymin], [xmax, ymax]], [[xmin, ymin], [xmax, ymax]]...]
    """
    labels, points = [], []
    with open(file_name, 'r') as fr:
            content = json.loads(fr.read())
            width = content['imageWidth']
            height = content['imageHeight']
            for shape in content['shapes']:
                labels.append(shape['label'])
                # round
                point = shape['points']
                for i in range(len(point)):
                    for j in range(len(point[0])):
                        point[i][j] = int(round(point[i][j]))
                points.append(shape['points'])
    return labels, points, width, height

def run(json_dir, save_dir):
    if not os.path.isdir(save_dir): os.makedirs(save_dir)
    names = glob.glob(json_dir + '/*.json')
    base_names = get_base_name(names)
    for i in tqdm(range(len(names))):
        labels, points, width, height = read_json(names[i])
        with open(f"{save_dir}/{base_names[i]}.txt", 'w') as fw:
            for label, point in zip(labels, points):
                # convert
                point[0][0] = 799 if point[0][0] > 799 else point[0][0]
                point[0][1] = 799 if point[0][1] > 799 else point[0][1]
                point[1][0] = 799 if point[1][0] > 799 else point[1][0]
                point[1][1] = 799 if point[1][1] > 799 else point[1][1]
                center_x = ((point[0][0] + point[1][0]) / 2 - 1) / width
                center_y = ((point[0][1] + point[1][1]) / 2 - 1) / height
                object_width = abs(point[1][0] - point[0][0]) / width
                object_height = abs(point[1][1] - point[0][1]) / height
                fw.write(f"{label_dict[label]} {center_x} {center_y} {object_width} {object_height}\n")

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_dir', type=str, required=True, help='json file dir')
    parser.add_argument('--save_dir', type=str, required=True, help='yolo label save dir')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_opt()
    json_dir = args.json_dir if args.json_dir[-1]!='/' else args.json_dir[0:-1]
    save_dir = args.save_dir if args.save_dir[-1]!='/' else args.save_dir[0:-1]
    run(json_dir, save_dir)