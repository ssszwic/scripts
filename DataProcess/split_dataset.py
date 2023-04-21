import os
import random
import argparse
import shutil

def movetxt(inpath,outpath,ref):
    f=open(ref)
    line = f.readline()
    while line:
        line = line.strip('\n')
        full_path = os.path.join(inpath, line)
        des_path = os.path.join(outpath, line)
        source = full_path + '.txt'
        aim = des_path + '.txt'
        shutil.copy(source, aim)
        line = f.readline()
    f.close()
    return 0

def movepng(inpath,outpath,ref):
    f=open(ref)
    line = f.readline()
    while line:
        line = line.strip('\n')
        full_path = os.path.join(inpath, line)
        des_path = os.path.join(outpath, line)
        source = full_path + '.png'
        aim = des_path + '.png'
        shutil.copy(source, aim)
        line = f.readline()
    f.close()
    return 0

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label_dir', type=str, required=True, help='yolo txt file dir')
    parser.add_argument('--img_dir', type=str, required=True, help='img file dir')
    parser.add_argument('--save_dir', type=str, required=True, help='save dir')
    parser.add_argument('--trainval', type=float, default=1, help='proportion of train and val to total dataset')
    parser.add_argument('--train', type=float, default=0.9, help='proportion of train to train and val')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_opt()
    label_dir = args.label_dir if args.label_dir[-1] != '/' else args.label_dir[0:-1]
    img_dir = args.img_dir if args.img_dir[-1] != '/' else args.img_dir[0:-1]
    save_dir = args.save_dir if args.save_dir[-1] != '/' else args.save_dir[0:-1]

    trainval_percent = args.trainval   #  代表train+val占的比例，若为1，则没有划分测试集
    train_percent = args.train    #   代表train占train+val的比例

    txtsavepath = "./temp"
    total_json = os.listdir(label_dir)
    if not os.path.exists(txtsavepath):
        os.makedirs(txtsavepath)

    num = len(total_json)
    list_index = range(num)
    tv = int(num * trainval_percent)
    tr = int(tv * train_percent)
    trainval = random.sample(list_index, tv)
    train = random.sample(trainval, tr)

    file_trainval = open(txtsavepath + '/trainval.txt', 'w')
    file_test = open(txtsavepath + '/test.txt', 'w')
    file_train = open(txtsavepath + '/train.txt', 'w')
    file_val = open(txtsavepath + '/val.txt', 'w')

    for i in list_index:
        name = total_json[i][:-4] + '\n'
        if i in trainval:
            file_trainval.write(name)
            if i in train:
                file_train.write(name)
            else:
                file_val.write(name)
        else:
            file_test.write(name)

    file_trainval.close()
    file_train.close()
    file_val.close()
    file_test.close()

    print('数据集比例划分成功')

    #参考路径
    train_ref="./temp/train.txt"
    val_ref="./temp/val.txt"
    test_ref="./temp/test.txt"

    #图片分类
    img_train=f"{save_dir}/images/train/"
    img_val=f"{save_dir}/images/val/"
    img_test=f"{save_dir}/images/test/"
    #
    if not os.path.exists(img_train): os.makedirs(img_train)
    if not os.path.exists(img_val): os.makedirs(img_val)
    if not os.path.exists(img_test): os.makedirs(img_test)

    movepng(img_dir,img_train,train_ref)   # 将图片分入训练集中
    movepng(img_dir,img_val,val_ref)   #将图片分入验证集中
    movepng(img_dir,img_test,test_ref)   #将图片分入测试集中

    #标签分类
    lab_train=f'{save_dir}/labels/train/'
    lab_val=f'{save_dir}/labels/val/'
    lab_test=f'{save_dir}/labels/test/'
    #

    if not os.path.exists(lab_train): os.makedirs(lab_train)
    if not os.path.exists(lab_val): os.makedirs(lab_val)
    if not os.path.exists(lab_test): os.makedirs(lab_test)

    movetxt(label_dir,lab_train,train_ref)  # 将标签分入训练集中
    movetxt(label_dir,lab_val,val_ref)  # 将标签分入验证集中
    movetxt(label_dir,lab_test,test_ref)  # 将标签分入测试集中

