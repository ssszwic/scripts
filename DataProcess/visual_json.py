import cv2
from tqdm import tqdm
import argparse
import glob
import os
import json

# 读取json文件中每个object的name的position
def read_json(file_dir):
    __positions, __names = [], []
    with open(file_dir, 'r') as fr:
            content = json.loads(fr.read())
            for shape in content['shapes']:
                __names.append(shape['label'])
                # round
                point = shape['points']
                for i in range(len(point)):
                    for j in range(len(point[0])):
                        point[i][j] = int(round(point[i][j]))
                __positions.append([point[0][0], point[0][1], point[1][0], point[1][1]])
    return __positions, __names

def plot(img_dir, positions, class_names):
    __img = cv2.imread(img_dir)
    for i in range(len(positions)):
        cv2.rectangle(__img, (positions[i][0], positions[i][1]),
                      (positions[i][2], positions[i][3]),
                      (0, 0, 255), thickness=1)
        cv2.putText(__img, class_names[i], (positions[i][0], positions[i][1]),
                    cv2.FONT_HERSHEY_COMPLEX, 0.8,
                    (0, 0, 255), thickness=1)
    return __img

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir', type=str, required=True, help='img file dir')
    parser.add_argument('--label_dir', type=str, required=True, help='json label dir')
    parser.add_argument('--save_dir', type=str, required=True, help='save dir')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_opt()
    img_dir = args.img_dir
    label_dir = args.label_dir
    save_dir = args.save_dir if args.save_dir[-1]!='/' else args.save_dir[0:-1]
    
    if not os.path.isdir(save_dir): os.makedirs(save_dir)
    # get image name
    img_paths = glob.glob(img_dir + '/*.png')
    names = []
    for img_path in img_paths:
        _, full_name = os.path.split(img_path)
        name, _, = os.path.splitext(full_name)
        names.append(name)

    for i in tqdm(range(len(names))):
        positions, class_names = read_json(f'{label_dir}/{names[i]}.json')
        img = plot(img_dir + '/' + names[i] + '.png', positions, class_names)
        cv2.imwrite(save_dir + '/' + names[i] + '.png', img)

    print('save dir: ', save_dir)
