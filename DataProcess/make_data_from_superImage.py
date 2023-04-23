import cv2
import json
import random
import os
from tqdm import tqdm
import argparse

# new_big_1     台湾台东空军基地（数据）
# new_big_2     小松机场（数据）
# new_big_3     新田原机场（数据）
# new_big_4     滨松机场（数据）
# new_big_5     澳大利亚柯廷空军基地（数据）
# new_big_6     筑城机场（数据）
# new_big_7     韩国大邱基地（数据）
# new_big_8     澳大利亚威廉城空军基地（数据）
# new_big_9     北卡罗来纳州新河陆战队航空站（数据）
# new_big_10    日本横田空军基地（数据）

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

def read_label(file_name, type='json'):
    """
    读取label信息
    :param file_name: 标签文件的路径
    :param type: 标签文件的类型,目前只支持labelme生成的json文件爱你
    :return labels: 标签文件中所有标签的列表,字符串格式
    :return points: 标签文件中每个框的位置,[[[xmin, ymin], [xmax, ymax]], [[xmin, ymin], [xmax, ymax]]...]
    """
    labels, points = [], []
    with open(file_name, 'r') as fr:
            content = json.loads(fr.read())
            for shape in content['shapes']:
                labels.append(shape['label'])
                # round
                point = shape['points']
                for i in range(len(point)):
                    for j in range(len(point[0])):
                        point[i][j] = int(round(point[i][j]))
                points.append(shape['points'])
    return labels, points

def save_label(save_path, labels, points, imageSize, type='json'):
    """
    将label信息保存为josn格式的标签文件
    :param save_name: 标签文件的路径
    :param labels: 标签文件中所有标签的列表,字符串格式
    :param points: 标签文件中每个框的位置 [[[xmin, ymin], [xmax, ymax]], [[xmin, ymin], [xmax, ymax]]...]
    :param type: 标签文件的类型,目前只支持labelme生成的json文件
    :param imageSize: 对应图像的宽度和高度,作为标签信息的一部分 [imageWidth, imageHeight]
    """
    shapes = []
    for label, point in zip(labels, points):
         shapes.append({'label': label, 'points': point})
    content = {'shapes': shapes, 'imageHeight': imageSize[0], 'imageWidth': imageSize[1]}
    with open(save_path, 'w', newline='\n') as fw:
        fw.write(json.dumps(content, indent=2))

def random_boxes(point, box_num, img_size, box_size):
    """
    从图像中随机选择一定数量的box,要求目标在box内
    :param point: 主要目标的位置框 [xmin, ymin, xmax, ymax]
    :param box_num: 产生框的数量
    :param img_size: 图像的尺寸 (image_width, image_height)
    :param box_size: box的尺寸 (box_width, box_height)
    :return boxes: 目标框 [[xmin, ymin, xmax, ymax], [xmin, ymin, xmax, ymax]...]
    """
    boxes = []
    object_width = point[1][0]-point[0][0]
    object_height = point[1][1]-point[0][1]
    for i in range(box_num):
        # 随机化object在box中的位置坐标
        xmin = random.randint(1, box_size[0]-object_width-2)
        ymin = random.randint(1, box_size[1]-object_height-2)
        # 根据object在大图中的坐标确定box
        box_xmin = point[0][0] - xmin
        box_ymin = point[0][1] - ymin
        box_xmax = box_xmin + box_size[0]
        box_ymax = box_ymin + box_size[1]
        # 防止box超出图像边界
        box_xmin = 0 if box_xmin < 0 else box_xmin
        box_ymin = 0 if box_ymin < 0 else box_ymin
        box_xmin = img_size[0] - box_size[0] if (box_xmin + box_size[0]) > img_size[0] else box_xmin
        box_ymin = img_size[1] - box_size[1] if (box_ymin + box_size[1]) > img_size[1] else box_ymin
        box_xmax = box_xmin + box_size[0]
        box_ymax = box_ymin + box_size[1]
        boxes.append([[box_xmin, box_ymin], [box_xmax, box_ymax]])
    return boxes
    
def match_labels(box, labels, points):
    """
    从所有label中选出在box内的label
    :param box: 选中的图像中的box区域的坐标 [[xmin, ymin], [xmax, ymax]]
    :param labels: object的目标标签 [label1, label2, ...]
    :param points: object的目标位置 [[[xmin, ymin], [xmax, ymax]], [[xmin, ymin], [xmax, ymax]]...]
    :return label_in_box: 在box中的label列表
    :return point_in_box: 在box中的目标框列表
    """
    label_in_box, point_in_box = [], []
    for label, point in zip(labels, points):
        # 判断目标框在box范围内
        if point[0][0] >= box[0][0] and point[0][1] >= box[0][1] and \
                point[1][0] <= box[1][0] and point[1][1] <= box[1][1]:
            new_point = [[0, 0], [0, 0]]
            new_point[0][0] = point[0][0] - box[0][0]
            new_point[0][1] = point[0][1] - box[0][1]
            new_point[1][0] = point[1][0] - box[0][0]
            new_point[1][1] = point[1][1] - box[0][1]
            point_in_box.append(new_point)
            label_in_box.append(label)
    return label_in_box, point_in_box

def check_points(all_points):
    """
    对point的数据进行检查,确保point[0]是box的左上角
    :param all_points: 所有object的box,对于单个box,格式为 [[xmin, ymin], [xmax, ymax]] or [[xmax, ymax], [xmin, ymin]]
    :return all_points: 所有object的box,确保point[0]是box的左上角
    """
    new_points = []
    for point in all_points:
        if point[0][0] > point[1][0]:
            new_points.append([point[1], point[0]])
        else:
            new_points.append(point)
    return new_points

def run(big_img_path,       # 大图的路径
        big_label_path,     # 大图标签的路径
        img_save_dir,       # 切割后图片的保存路径
        label_save_dir,     # 切割后标签的保存路径
        img_width=800,      # 切割小图的宽度
        img_height=800,     # 切割小图的高度
        box_num=4,          # 大图中每个目标作为主要目标的次数
        damage_air_pro=0.2  # 每个弹坑作为主要目标的概率
        ):
    
    if not os.path.isdir(img_save_dir): os.makedirs(img_save_dir)
    if not os.path.isdir(label_save_dir): os.makedirs(label_save_dir)

    # 1. 读取图像和标签 ####################################################################
    img_src = cv2.imread(big_img_path)
    big_img_height, big_img_width = img_src.shape[0], img_src.shape[1]
    all_labels, all_points = read_label(big_label_path)
    # 对每个points进行排序，确保point[0]是box的左上角
    all_points = check_points(all_points)

    # 2. 获取所有box #######################################################################
    all_boxes = []
    for label, point in zip(all_labels, all_points):
        # 2.1 选择主要目标，按照概率选择弹坑作为主要目标
        if label == 'Damage_airstript' and random.randint(1, 100000) > damage_air_pro * 100000:
            continue
        # 2.2 根据主要目标选择box，使主要目标在框中随机分布，目标框的个数由 box_num 指定, 其中弹坑只出现一次
        if label == 'Damage_airstript':
            boxes = random_boxes(point, 1, [big_img_width, big_img_height], [img_width, img_height])
        else:
            boxes = random_boxes(point, box_num, [big_img_width, big_img_height], [img_width, img_height])
        all_boxes += boxes

    # 3. 切割图像和保存标签 ##################################################################
    for i in tqdm(range(len(all_boxes))):
        # 3.1 得到box内所有的目标 
        label_in_box, point_in_box = match_labels(all_boxes[i], all_labels, all_points)
        # 3.2 保存标签
        name = get_base_name(big_img_path)
        save_label(f'{label_save_dir}/{name}_{i}.json', label_in_box, point_in_box, [img_width, img_height], type='json')
        # 3.2 切割保存图像
        img_cut = img_src[all_boxes[i][0][1]:all_boxes[i][1][1], all_boxes[i][0][0]:all_boxes[i][1][0]]
        cv2.imwrite(f'{img_save_dir}/{name}_{i}.png', img_cut)

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_path', type=str, required=True, help='big image path')
    parser.add_argument('--label_path', type=str, required=True, help='big label path')
    parser.add_argument('--img_save_dir', type=str, required=True, help='image save dir')
    parser.add_argument('--label_save_dir', type=str, required=True, help='label save dir')
    parser.add_argument('--width', type=int, default=800, help='The width of small image')
    parser.add_argument('--height', type=int, default=800, help='The height of small image')
    parser.add_argument('--box_num', type=int, default=4, help='The num of object')
    parser.add_argument('--prob', type=float, default=0.2, help='The probability of a bullet as an object')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_opt()
    big_img_path    = args.img_path if args.img_path[-1]!='/' else args.img_path[0:-1]
    big_label_path  = args.label_path if args.label_path[-1]!='/' else args.label_path[0:-1]
    img_save_dir    = args.img_save_dir if args.img_save_dir[-1]!='/' else args.img_save_dir[0:-1]
    label_save_dir  = args.label_save_dir if args.label_save_dir[-1]!='/' else args.label_save_dir[0:-1]
    run(big_img_path, big_label_path, img_save_dir, label_save_dir, args.width, args.height, args.box_num, args.prob)