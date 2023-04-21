from tqdm import tqdm
import random
import cv2
import json
import os
import glob
import math
from threading import Thread
import argparse

pre_labels = [
    'revetmentAircraft_1', 'revetmentAircraft_2', 'revetmentAircraft_3',
    'revetmentAircraft_4', 'revetmentAircraft_5', 'revetmentAircraft_6',
    'revetmentAircraft_7', 'revetmentAircraft_8'
]

# 在中心范围内随机选中一组坐标
def select_position(x_min, y_min, x_max, y_max, ratio=0.3):
    x_lenth = (x_max - x_min) * ratio
    y_lenth = (y_max - y_min) * ratio

    xx_min = round(((x_max + x_min) / 2) - x_lenth / 2)
    xx_max = round(((x_max + x_min) / 2) + x_lenth / 2)
    yy_min = round(((y_max + y_min) / 2) - y_lenth / 2)
    yy_max = round(((y_max + y_min) / 2) + y_lenth / 2)

    x = random.randint(xx_min, xx_max)
    y = random.randint(yy_min, yy_max)

    return [x, y]

# 计算两个坐标的距离
def distance(posi1, posi2):
    dis_x2 = (posi1[0] - posi2[0])**2
    dis_y2 = (posi1[1] - posi2[1])**2
    dis = math.sqrt(dis_x2 + dis_y2)
    return dis

# 像素相加，考虑溢出
def pix_add(pix, num):
    if (pix + num) > 255:
        return 255
    elif (pix + num) < 0:
        return 0
    else:
        return pix + num

def max_distance(posi, x, y, F1, F2, a):
    if x == posi[0]:
        x_ratio = 0
        y_ratio = 1
    else:
        x_ratio = 1
        y_ratio = (y - posi[1]) / (x - posi[0])
    while True:
        if distance([x, y], F1) + distance([x, y], F2) > 2 * a:
            break
        else:
            x = x + 0.1 * x_ratio
            y = y + 0.1 * y_ratio

    x = x - x_ratio * 0.1
    y = y - y_ratio * 0.1
    return distance([x, y], F1) + distance([x, y], F2)

# 根据椭圆离心率和面积计算椭圆信息
# a**2 = b**2 + c**2
# c/a = e
# pi*a*b = area
# 联立求解
def calculate_ellipses(area, e):
    a = (((area / math.pi) ** 2) / (1 - e ** 2)) ** (1/4)
    b = area / (math.pi * a)
    c = e * a
    return a, b, c

def plot_hole(img, posi, min_e=0.55, max_e=0.7, min_area=78, max_area=200):
    # 1. 确定椭圆离心率
    e = random.uniform(min_e, max_e)

    # 2. 确定椭圆面积
    area = random.uniform(min_area, max_area)

    # 3. 确定椭圆参数
    a, b, c = calculate_ellipses(area, e)

    # 4. 确定焦点和落弹点的相对距离
    r = random.uniform(-c*1/3, c*1/3)

    # 5. 确定长轴方向
    theta = random.uniform(0, math.pi)

    # 5. 计算焦点位置
    F1 = [0, 0]
    F2 = [0, 0]
    F1[0] = posi[0] + (-c - r) * math.cos(theta)
    F1[1] = posi[1] + (-c - r) * math.sin(theta)
    F2[0] = posi[0] + (c - r) * math.cos(theta)
    F2[1] = posi[1] + (c - r) * math.sin(theta)

    # 列出弹坑周围的像素坐标
    pix_range = 20
    xl = [i + posi[0] for i in range(-pix_range, pix_range+1)
        if (i + posi[0]) >= 0 and (i + posi[0]) <= 799]
    yl = [i + posi[1] for i in range(-pix_range, pix_range+1)
        if (i + posi[1]) >= 0 and (i + posi[1]) <= 799]

    # 依次对每个像素进行处理
    for x in xl:
        for y in yl:
            # 像素点在椭圆内
            if distance([x, y], F1) + distance([x, y], F2) < 2 * a:
                # 直接访问坐标系为转置
                pix_src = img[y, x]
                pix_new = [0, 0, 0]

                # 距离爆炸点越近颜色越深，线性变化
                dis = distance([x, y], posi)
                if dis < 0:
                    img[y, x] = pix_new
                else:
                    max_dis = max_distance(posi, x, y, F1, F2, a)
                    pix_new[0] = pix_add(pix_src[0] * (0.2 + dis / max_dis), pix_new[0])
                    pix_new[1] = pix_add(pix_src[1] * (0.2 + dis / max_dis), pix_new[1])
                    pix_new[2] = pix_add(pix_src[2] * (0.2 + dis / max_dis), pix_new[2])
                    img[y, x] = pix_new
            elif distance([x, y], F1) + distance([x, y], F2) < 2 * a + 2:
                pix_src = img[y, x]
                pix_new = [0, 0, 0]
                pix_new[0] = pix_add(pix_src[0], -5)
                pix_new[1] = pix_add(pix_src[1], -5)
                pix_new[2] = pix_add(pix_src[2], -5)
                img[y, x] = pix_new
            elif distance([x, y], F1) + distance([x, y], F2) < 2 * a + 5:
                pix_src = img[y, x]
                pix_new = [0, 0, 0]
                pix_new[0] = pix_add(pix_src[0], 0)
                pix_new[1] = pix_add(pix_src[1], 0)
                pix_new[2] = pix_add(pix_src[2], 0)
                img[y, x] = pix_new
            elif distance([x, y], F1) + distance([x, y], F2) < 2 * a + 8:
                pix_src = img[y, x]
                pix_new = [0, 0, 0]
                pix_new[0] = pix_add(pix_src[0], 5)
                pix_new[1] = pix_add(pix_src[1], 5)
                pix_new[2] = pix_add(pix_src[2], 5)
                img[y, x] = pix_new
 
    # 局部高斯模糊
    x_min = xl[0]
    x_max = xl[-1]
    y_min = yl[0]
    y_max = yl[-1]
    img_gauss = cv2.GaussianBlur(img[y_min:y_max, x_min:x_max], (3, 3), 1)
    img[y_min:y_max, x_min:x_max] = img_gauss

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

def run(img_path, label_path, img_save_path, label_save_path):
    labels, positions = read_label(label_path)
    img = cv2.imread(img_path)

    new_positions = []

    for position, label in zip(positions, labels):
        if label in pre_labels:
            if random.random() < damage_ratio:
                # 制作弹坑
                re_xmin = min(position[0][0], position[1][0])
                re_xmax = max(position[0][0], position[1][0])
                re_ymin = min(position[0][1], position[1][1])
                re_ymax = max(position[0][1], position[1][1])
                assert(re_xmin < re_xmax)
                assert(re_ymin < re_ymax)
                posi = select_position(re_xmin, re_ymin, re_xmax, re_ymax, ratio=0.2)
                plot_hole(img, posi)
                xmin = posi[0] - width
                xmax = posi[0] + width
                ymin = posi[1] - width
                ymax = posi[1] + width
                new_positions.append([[xmin, ymin], [xmax, ymax]])
    # add new label
    for j in range(len(new_positions)):
        labels.append('Damage_revetmentAircraft')
    positions.extend(new_positions)
    # save label and image
    cv2.imwrite(img_save_path, img)
    save_label(label_save_path, labels, positions, [800, 800])

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir', type=str, required=True, help='img file dir')
    parser.add_argument('--label_dir', type=str, required=True, help='json label dir')
    parser.add_argument('--img_save_dir', type=str, required=True, help='img save dir')
    parser.add_argument('--label_save_dir', type=str, required=True, help='label save dir')
    parser.add_argument('--prob', type=float, default=0.5, help='probability of plot hole for every object')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_opt()
    img_dir = args.img_dir
    label_dir = args.label_dir
    img_save_dir = args.img_save_dir
    label_save_dir = args.label_save_dir
    damage_ratio = args.prob
    if not os.path.isdir(img_save_dir): os.makedirs(img_save_dir)
    if not os.path.isdir(label_save_dir): os.makedirs(label_save_dir)
    
    label_paths = glob.glob(f'{label_dir}/*.json')
    base_names = get_base_name(label_paths)
    # 正方形框边长的一半
    width = 10
    # 机堡毁伤概率
    damage_ratio = 0.5

    for i in tqdm(range(len(label_paths))):
        # 单线程
        # run(f"{img_dir}/{base_names[i]}.png", 
        #     f"{label_dir}/{base_names[i]}.json",
        #     f"{img_save_dir}/{base_names[i]}.png",
        #     f"{label_save_dir}/{base_names[i]}.json")
        # 多线程
        Thread(target=run, 
               args=(f"{img_dir}/{base_names[i]}.png",
                     f"{label_dir}/{base_names[i]}.json",
                     f"{img_save_dir}/{base_names[i]}.png",
                     f"{label_save_dir}/{base_names[i]}.json")).start()




