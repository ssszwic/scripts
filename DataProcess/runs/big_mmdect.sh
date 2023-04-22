#!/bin/bash
img_path=/home/sunli/work/szw/dataset/Data_DK/new_big_1.png
img_save=/home/sunli/work/szw/scripts/DataProcess/data/dst/new_big_1_faster.png

small_dir=/home/sunli/work/szw/scripts/DataProcess/data/build
small_dst=/home/sunli/work/szw/scripts/DataProcess/data/build_dst_mm

model=faster-rcnn_atd_3.8/faster-rcnn_r50_fpn_1x_coco_atd.py
weights=faster-rcnn_atd_3.8/model.onnx

# model=ssd800_coco_atd_3.8/ssd800_coco_atd.py
# weights=ssd800_coco_atd_3.8/model.onnx

rm -r ${small_dir}
rm -r ${small_dst}

now=`date +'%Y-%m-%d %H:%M:%S'`
start_time=$(date --date="$now" +%s)

echo "------------------------1. cut------------------------"
python cut_compose.py \
        --op cut \
        --big_img_path ${img_path} \
        --cut_img_dir ${small_dir} \
        --width 800 \
        --height 800

echo "------------------------2. detect---------------------"
python /home/sunli/work/szw/mmdetection/tools/detect.py \
        --img_dir ${small_dir} \
        --model_cfg /home/sunli/work/szw/mmdetection/work_dirs/${model} \
        --weights /home/sunli/work/szw/mmdetection/work_dirs/${weights} \
        --save_dir ${small_dst}

echo "-----------------------3. compose---------------------"
python cut_compose.py \
        --op compose \
        --big_img_path ${img_save} \
        --cut_img_dir ${small_dst} \
        --width 800 \
        --height 800
        
echo "result: ${img_save}"
now=`date +'%Y-%m-%d %H:%M:%S'`
end_time=$(date --date="$now" +%s)
echo "used time:"$((end_time-start_time))"s"

# ssd 59s gpu 45
# faster rcnn 104s