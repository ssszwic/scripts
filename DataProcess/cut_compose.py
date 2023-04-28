import cv2
import os
import glob
import numpy as np
import argparse

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

def cut(big_img_path, cut_path, size):
    if not os.path.isdir(cut_path): os.makedirs(cut_path)
    big_img = cv2.imread(big_img_path)
    big_height, big_width = big_img.shape[0], big_img.shape[1]
    height, width = size[1], size[0]
    name_row, name_col = 0, 0

    # shape: [height, width, channel]
    h = 0
    name_row = 0
    while 1:
        if h + height >= big_height:
            w = 0
            name_col = 0
            while 1:
                if w + width >= big_width:
                    img = big_img[h:big_height, w:big_width]
                    cv2.imwrite(cut_path + '/' + str(name_row) + '_' + str(name_col) + '.png', img)
                    name_col += 1
                    break
                else:
                    img = big_img[h:big_height, w:w+width]
                    cv2.imwrite(cut_path + '/' + str(name_row) + '_' + str(name_col) + '.png', img)
                    name_col += 1
                    w += width
            break
        else:
            w = 0
            name_col = 0
            while 1:
                if w + width >= big_width:
                    img = big_img[h:h+height, w:big_width]
                    cv2.imwrite(cut_path + '/' + str(name_row) + '_' + str(name_col) + '.png', img)
                    name_col += 1
                    break
                else:
                    img = big_img[h:h+height, w:w+width]
                    cv2.imwrite(cut_path + '/' + str(name_row) + '_' + str(name_col) + '.png', img)
                    name_col += 1
                    w += width
            h += height
            name_row += 1

def compose(big_img_path, cut_path):
    file_list = glob.glob(cut_path + '/*')
    base_list = get_base_name(file_list)
    rows, cols = [], []
    # get max index
    for base_name in base_list:
        [row, col] = base_name.split('_')
        row, col = int(row), int(col)
        rows.append(row)
        cols.append(col)
    row_max = max(rows)
    col_max = max(cols)

    # concatenate
    for name_row in range(row_max + 1):
        for name_col in range(col_max + 1):
            img = cv2.imread(cut_path + '/' + str(name_row) + '_' + str(name_col) + '.png')
            img_col = img if name_col == 0 else np.concatenate((img_col, img), axis = 1)
        big_img = img_col if name_row == 0 else np.concatenate((big_img, img_col), axis = 0)
    
    # save big image
    cv2.imwrite(big_img_path, big_img)

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--op', type=str, required=True, help='cut or compose')
    parser.add_argument('--big_img_path', type=str, required=True, help='big image path')
    parser.add_argument('--cut_img_dir', type=str, required=True, help='cut image dir')
    parser.add_argument('--width', type=int, default=800, help='width step')
    parser.add_argument('--height', type=int, default=800, help='height step')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_opt()
    big_img_path = args.big_img_path if args.big_img_path[-1] != '/' else args.big_img_path[0:-1]
    cut_img_dir = args.cut_img_dir if args.cut_img_dir[-1] != '/' else args.cut_img_dir[0:-1]
    father_dir, _ = os.path.split(big_img_path)
    if not os.path.isdir(father_dir): os.makedirs(father_dir)
    if args.op == 'cut':
        cut(big_img_path, cut_img_dir, (args.width, args.height))
    elif args.op == 'compose':
        compose(big_img_path, cut_img_dir)
    else:
        print("op error! must be 'cut' or 'compose'")
