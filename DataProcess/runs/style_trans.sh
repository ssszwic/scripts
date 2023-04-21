#!/bin/bash
img_dir=/home/sunli/work/szw/script/DataProcess/data/image
dst_dir=/home/sunli/work/szw/script/DataProcess/data/image_winter
step=800

cd /home/sunli/work/szw/pytorch-CycleGAN-and-pix2pix
python  test.py \
            --dataroot ${img_dir} \
            --name summer2winter_yosemite \
            --load_size ${step} \
            --crop_size ${step} \
            --model test \
            --no_dropout \
            --num_test 100000 \
            --results_dir ${dst_dir}

# cd /home/ssszw/Work/DataProcess/
# # delate real
# rm ./build/summer2winter_yosemite/test_latest/images/*real*+
# # deal 'fake'
# rename -v 's/_fake//' ./build/summer2winter_yosemite/test_latest/images/*
# # compose image
# python cut_compose.py --op compose \
#                     --big_img_path ${big_img_dst} \
#                     --cut_dir_path ./build/summer2winter_yosemite/test_latest/images
