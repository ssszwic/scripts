#!/bin/bash
big_img_dir=/home/sunli/work/szw/dataset/Data_DK
big_label_dir=/home/sunli/work/szw/dataset/Data_DK
img_save_dir=/home/sunli/work/szw/script/DataProcess/data/image
label_save_dir=/home/sunli/work/szw/script/DataProcess/data/label_json

images=$(ls ${big_img_dir} | grep 'png')
labels=$(ls ${big_img_dir} | grep 'json')

for path in $(ls ${big_img_dir} | grep '.png')
do
    python /home/sunli/work/szw/script/DataProcess/big_cut.py \
            --img_path ${big_img_dir}/${path} \
            --label_path ${big_label_dir}/${path/.png/.json} \
            --img_save_dir ${img_save_dir} \
            --label_save_dir ${label_save_dir} \
            --prob 0.5 &
done
echo "finish!"
