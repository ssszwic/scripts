#!/bin/bash
yolo_dataset_dir=/Dataset/ATD_3.4

# make dir
rm -r ${yolo_dataset_dir}/annotations
mkdir ${yolo_dataset_dir}/annotations

# generate json
python /home/sunli/work/szw/script/DataProcess/yolo2coco.py \
        --yolo_dir ${yolo_dataset_dir}/labels/train \
        --save_name ${yolo_dataset_dir}/annotations/train.json

python /home/sunli/work/szw/script/DataProcess/yolo2coco.py \
        --yolo_dir ${yolo_dataset_dir}/labels/val \
        --save_name ${yolo_dataset_dir}/annotations/val.json