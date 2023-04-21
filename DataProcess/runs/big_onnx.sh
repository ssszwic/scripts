#!/bin/bash
img_path=/home/sunli/work/szw/dataset/Data_DK/new_big_6.png
img_save=/home/sunli/work/szw/script/DataProcess/data/dst/new_big_6.png
weight_path=/home/sunli/work/szw/yolov5/runs/train/yolov5s-ATD_3.5/weights/best.onnx

rm -r /home/sunli/work/szw/military/small_predict/test
rm -r /home/sunli/work/szw/script/DataProcess/build

echo "------------------------cut------------------------"
python cut_compose.py \
        --op cut \
        --big_img_path ${img_path} \
        --cut_dir_path /home/sunli/work/szw/script/DataProcess/build

echo "------------------------detect---------------------"
python /home/sunli/work/szw/military/small_predict/onnx_predict.py \
        --img_dir /home/sunli/work/szw/script/DataProcess/build \
        --save_dir /home/sunli/work/szw/military/small_predict/test \
        --weights ${weight_path} \
        --iou_thres 0.8

echo "-----------------------compose---------------------"
python cut_compose.py \
        --op compose \
        --big_img_path ${img_save} \
        --cut_dir_path /home/sunli/work/szw/military/small_predict/test

echo "result: ${img_save}"
