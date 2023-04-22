#!/bin/bash
img_path=/home/sunli/work/szw/dataset/Data_DK/new_big_1.png
img_save=/home/sunli/work/szw/scripts/DataProcess/data/dst/new_big_1_yolo.png
weight_path=/home/sunli/work/szw/yolov5/runs/train/yolov5s-ATD_3.8/weights/best.pt

small_dir=/home/sunli/work/szw/scripts/DataProcess/data/build
small_dst=/home/sunli/work/szw/scripts/DataProcess/data/build_dst_yolo

rm -r ${small_dir}
rm -r ${small_dst}

now=`date +'%Y-%m-%d %H:%M:%S'`
start_time=$(date --date="$now" +%s);

echo "------------------------1. cut------------------------"
python cut_compose.py \
        --op cut \
        --big_img_path ${img_path} \
        --cut_img_dir ${small_dir}

echo "------------------------2. detect---------------------"
python /home/sunli/work/szw/yolov5/detect.py \
        --source ${small_dir} \
        --weights ${weight_path} \
        --project ${small_dst} \
        --name '' \
        --imgsz 800 \
        --device 0
        
echo "-----------------------3. compose---------------------"
python cut_compose.py \
        --op compose \
        --big_img_path ${img_save} \
        --cut_img_dir ${small_dst}

echo "result: ${img_save}"
now=`date +'%Y-%m-%d %H:%M:%S'`
end_time=$(date --date="$now" +%s)
echo "used time:"$((end_time-start_time))"s"

# cpu: 35s  gpu: 28