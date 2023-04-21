import os
import random
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sn
from glob import glob
from PIL import Image, ImageDraw
import argparse

category_all = [
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
    'helicopter',
    'specialPlane_1',
    'specialPlane_2',
    'specialPlane_3',
    'AircraftBuilding_1',
    'AircraftBuilding_2',
    'AircraftBuilding_3',
    'parkingApron_H',
    'parkingApron_C',
    'parkingApron_S',
    'parkingApron_R',
    'parkingApron_X',
]

def plot_labels(labels, names=(), save_dir=''):
    # plot dataset labels
    print('Plotting labels... ')
    c, b = labels[:, 0], labels[:, 1:].transpose()  # classes, boxes
    nc = int(c.max() + 1)  # number of classes
    x = pd.DataFrame(b.transpose(), columns=['x', 'y', 'width', 'height'])

    # seaborn correlogram
    sn.pairplot(x, corner=True, diag_kind='auto', kind='hist', diag_kws=dict(bins=50), plot_kws=dict(pmax=0.9))
    plt.savefig(os.path.join(save_dir, 'labels_correlogram.jpg'), dpi=200)
    plt.close()

    # matplotlib labels
    matplotlib.use('svg')  # faster
    ax = plt.subplots(2, 2, figsize=(8, 8), tight_layout=True)[1].ravel()
    y = ax[0].hist(c, bins=np.linspace(0, nc, nc + 1) - 0.5, rwidth=0.8)
    data = {'category':names, 'nums':y[0]}
    # 使输入的nc name和分析得到的nc数量一致
    if (len(data['category']) - len(data['nums'])) != 0:
        temp = data['category']
        temp = temp[0:-(len(data['category']) - len(data['nums']))]
        data['category'] = temp

    df0 = pd.DataFrame(data)
    df0.to_excel(os.path.join(save_dir, 'labels.xlsx'), na_rep=False)
    # [y[2].patches[i].set_color([x / 255 for x in colors(i)]) for i in range(nc)]  # update colors bug #3195
    ax[0].set_ylabel('instances')
    if 0 < len(names) < 30:
        ax[0].set_xticks(range(len(names)))
        ax[0].set_xticklabels(names, rotation=90, fontsize=10)
    else:
        ax[0].set_xlabel('classes')
    sn.histplot(x, x='x', y='y', ax=ax[2], bins=50, pmax=0.9)
    sn.histplot(x, x='width', y='height', ax=ax[3], bins=50, pmax=0.9)

    # rectangles
    labels[:, 1:3] = 0.5  # center
    labels[:, 1:] = xywh2xyxy(labels[:, 1:]) * 2000
    img = Image.fromarray(np.ones((2000, 2000, 3), dtype=np.uint8) * 255)
    for cls, *box in labels[:1000]:
        ImageDraw.Draw(img).rectangle(box, width=1, outline=colors[int(cls)])  # plot
    ax[1].imshow(img)
    ax[1].axis('off')

    for a in [0, 1, 2, 3]:
        for s in ['top', 'right', 'left', 'bottom']:
            ax[a].spines[s].set_visible(False)

    plt.savefig(os.path.join(save_dir, 'labels.jpg'), dpi=200)
    matplotlib.use('Agg')
    plt.close()

def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label_dir', type=str, required=True, help='label file dir')
    parser.add_argument('--save_dir', type=str, required=True, help='yolo label save dir')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_opt()
    label_dir = args.label_dir if args.label_dir[-1]!='/' else args.label_dir[0:-1]
    save_dir = args.save_dir if args.save_dir[-1]!='/' else args.save_dir[0:-1]
    if not os.path.isdir(save_dir): os.makedirs(save_dir)
    
    num_classes = len(category_all)  # 类别数
    colors = [(random.randint(0,255),random.randint(0,255),random.randint(0,255)) for _ in range(num_classes)]  # 每个类别生成一个随机颜
    all_files = glob(f"{label_dir}/*.txt")
    shapes = []  # 标注框
    ids = []  # 类别名的索引
    for file in all_files:
        if file.endswith('classes.txt'):
            continue
        with open(file, 'r') as f:
            for l in f.readlines():
                line = l.split()  # ['11' '0.724877' '0.309082' '0.073938' '0.086914']
                ids.append([int(line[0])])
                shapes.append(list(map(float, line[1:])))

    shapes = np.array(shapes)
    ids = np.array(ids)
    lbs = np.hstack((ids, shapes))
    # print(lbs)
    plot_labels(labels=lbs, names=np.array(category_all), save_dir=save_dir)