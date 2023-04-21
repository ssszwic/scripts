# SCRIPTS
## 1. 数据集分析与可视化
---
### 1.1 analysis_yolo
分析yolov5格式数据集中的标签数量，box分布等，并绘制图像保存为表格
**需要改动标签名字以适用不同的数据集**
``` bash
python analysis_yolo.py \
        --label_dir ./lable_dir \   # label文件所在的文件夹
        --save_dir ./save_dir       # 分析结果保存位置
```
---
### 1.2 visual_yolo
yolov5格式数据集的可视化，将框画在对应的目标上保存成图片
**需要改动标签名字以适用不同的数据集**
```bash
python visual_yolo \
        --img_dir ./images \    # 图像文件所在的位置
        --label_dir ./labels \  # 标签文件所在的位置
        --save_dir ./result     # 绘制后图像保存的位置
```
---
### 1.3 visual_json
json格式(由labelme保存的标签文件格式)数据集的可视化，将框画在对应的目标上保存成图片
```bash
python visual_yolo \
        --img_dir ./images \    # 图像文件所在的位置
        --label_dir ./labels \  # 标签文件所在的位置
        --save_dir ./result     # 绘制后图像保存的位置
```
---
## 2. 数据集制作与转换
---
### 2.1 make_data_from_superImage
对大图进行切割，输入大图图像以及对应的标签文件，形成标签格式为json的数据集
1. 对非弹坑目标进行遍历，依次作为主要目标，对弹坑目标进行概率判断，即每个弹坑有一定的概率作为主要目标
2. 根据主要目标的位置进行小图切割，确保将主要目标包含，并且具有随机性
3. 搜索小图范围内的所有目标，保存为json文件
4. 保存图片
``` bash
python make_data_from_superImage.py \  
        --img_path ./big.png \          # 超大图像的路径
        --label_path ./big.json \       # 超大图像对应标签的路径
        --img_save_dir ./images \       # 生成数据集的图片保存位置
        --label_save_dir ./labels \     # 生成数据集的标签保存位置
        --width 800 \                   # 切割后小图的宽度
        --height 800 \                  # 切割后小图的高度
        --box_num 4 \                   # 根据每个主要目标生成的小图数量，默认为4
        --prob 0.2 \                    # 每个弹坑被选为主要目标的概率，默认为0.02
```
---
### 2.2 json2yolo
将labelme生成的json格式转换为yolov5格式
**需要改动标签名字以适用不同的数据集**
``` bash
python json2yolo.py \
        --json_dir ./label_json \       # json文件所在的位置
        --save_dir ./label_yolo         # 生成yolo标签文件的保存位置
```
---
### 2.3 split_dataset
划分yolov5格式的训练集和验证集
``` bash
python split_dataset.py \
        --label_dir ./label_json \      # yolo标签文件的位置
        --img_dir ./img \               # 图片的位置
        --save_dir ./dataset \          # 生成数据集的保存位置
        --trainval 1 \                  # 训练集和验证集占总数据的比例，其余为测试集
        --train 0.9                     # 训练集占训练集和验证集的比例，其余为验证集
```
### 2.4 make_coco_from_yolo
将yolov5格式的数据标签转为为coco格式，coco格式是将所有train或val的lable信息放到一个json文件中
**需要改动标签名字以适用不同的数据集**
``` bash
python make_coco_from_yolo.py \
        --yolo_dir ./label/train \      # yolov5格式lable文件夹所在的位置
        --save_name ./train.json        # 生成json文件的保存位置
```
---
### 2.5 label_replace_yolo
对YOLOV5格式的数据集的标签进行替换、删除等处理
其中label_dict的类型为字典，其中字典的key表示原label中的标签，对应的value表示替换后label中的标签，若value为-1，则表示删除该标签，key中没有提到的标签维持原样
``` bash
python label_replace_yolo.py \
        --label_dict "{0: 1, 1: -1}" \  # 替换方式，将0标签替换为1,删除原有的1标签
        --label_dir ./label_src \       # 待处理标签的位置
        --save_dir ./label_dst          # 处理后标签的保存位置
```
---
## 3. Other
---
### 3.1 cut_compose
超大图像与小图之间的转换，将超大图像切割成小图或将小图拼接为超大图像
在切到边缘时图片大小可能小于要求的大小
``` bash
python cut_compose.py \
        --op cut \                  # 操作 cut:大图切割为小图 compose:小图拼接为大图
        --big_img_path ./big.png \  # 超大图像的路径
        --cut_img_dir ./image \     # 小图的位置
        --width 800 \               # 小图的宽度
        --height 800                # 小图的高度
```
---
### 3.2 plot_hole
在某些目标上随机画洞，需要图像和对应的json格式(labelme默认保存格式)的标签
```bash
python plot_hole.py \                         
        --img_dir ./image \                     # 源图像的位置
        --label_dir ./label_json \              # 源图像对应的json标签的位置
        --img_save_dir ./image_hole \           # 处理后图像的保存位置
        --label_save_dir ./label_hole_json \    # 处理和标签的保存位置
        --prob 0.5                              # 对每个目标描坑的概率
```
---
### 3.3 read_tif
读取tif文件，打印仿射变换矩阵
```bash
python read_tif.py \                         
        --path ./test.tif       # tif文件路径或者tif文件所在的文件夹
```
---