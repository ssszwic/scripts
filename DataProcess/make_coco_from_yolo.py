import glob
import os
from tqdm import tqdm
import json
import argparse

# {
#     "images": [image],
#     "annotations": [annotation],
#     "categories": [category]
# }


# image = {
#     "id": int,
#     "width": int,
#     "height": int,
#     "file_name": str,
# }

# annotation = {
#     "id": int,
#     "image_id": int,
#     "category_id": int,
#     "segmentation": RLE or [polygon],
#     "area": float,
#     "bbox": [x,y,width,height], # (x, y) 为 bbox 左上角的坐标
#     "iscrowd": 0 or 1,
# }

# categories = [{
#     "id": int,
#     "name": str,
#     "supercategory": str,
# }]

class_list = [
    'revetmentAircraft_1',
    'revetmentAircraft_2',
    'revetmentAircraft_3',
    'revetmentAircraft_4',
    'revetmentAircraft_5',
    'revetmentAircraft_6',
    'revetmentAircraft_7',
    'revetmentAircraft_8',
    'specialAircraft',
    'oilTank',
    'fighter',
    'Damage_revetmentAircraft',
    'Damage_airstript',
    # 'helicopter',
    # 'specialPlane_1',
    # 'specialPlane_2',
    # 'specialPlane_3',
    # 'AircraftBuilding_1',
    # 'AircraftBuilding_2',
    # 'AircraftBuilding_3',
    # 'parkingApron_H',
    # 'parkingApron_C',
    # 'parkingApron_S',
    # 'parkingApron_R',
    # 'parkingApron_X'
]

img_height = 800
img_width = 800


def read_yolo(label_path):
    labels = []
    with open(label_path, "r") as f:
        # 读取每一行label，并按空格划分数据
        datas = [x.split() for x in f.read().splitlines()]
        for data in datas:
            id = int(data[0])
            cx = float(data[1]) * img_width
            cy = float(data[2]) * img_height
            w = float(data[3]) * img_width
            h = float(data[4]) * img_height
            x = round(cx - w / 2)
            y = round(cy - h / 2)
            w = round(w)
            h = round(h)
            area = w * h
            labels.append([id, x, y, w, h, area])
    return labels

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


def generate_coco(label_dir, save_name):
    images = []
    annotations = []
    categories = []
    # make categories #######################################################
    for i, class_name in enumerate(class_list):
        categorie = {'supercategory': None, 'id': i, 'name': class_name}
        categories.append(categorie)
    
    label_paths = glob.glob(f'{label_dir}/*.txt')
    base_names = get_base_name(label_paths)
    anno_index = 0
    for i in tqdm(range(len(label_paths))):
        # make image ############################################################
        image = {
                'file_name': f'{base_names[i]}.png',
                'height': img_height,
                'width': img_width,
                'id': i
                }
        images.append(image)
        labels = read_yolo(label_paths[i])
        for j, label in enumerate(labels):
            # make annotation #####################################################
            annotation = {
                        'image_id': i,
                        'bbox': label[1:-1],
                        'category_id': label[0],
                        'id': anno_index,
                        "segmentation": 'null',
                        "area": label[-1],
                        "iscrowd": 0,
                        }
            anno_index += 1
            annotations.append(annotation)
    content = {
                "images": images, 
                "annotations": annotations, 
                "categories": categories,
                }
    
    # write json
    with open(save_name, 'w', newline='\n') as f:
        f.write(json.dumps(content, indent=2))

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--yolo_dir', type=str, required=True, help='yolo txt file dir')
    parser.add_argument('--save_name', type=str, required=True, help='yolo label save dir')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_opt()
    yolo_dir = args.yolo_dir if args.yolo_dir[-1] != '/' else args.yolo_dir[0:-1]
    generate_coco(yolo_dir, args.save_name)