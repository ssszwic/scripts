#!/bin/bash
rm -r /home/sunli/work/szw/script/DataProcess/data/image
rm -r /home/sunli/work/szw/script/DataProcess/data/label_json
rm -r /home/sunli/work/szw/script/DataProcess/data/label_yolo
./batch_big_cut.sh

python json2yolo.py \
    --json_dir /home/sunli/work/szw/script/DataProcess/data/label_json \
    --save_dir /home/sunli/work/szw/script/DataProcess/data/label_yolo

python analysis_yolo.py \
    --label_dir /home/sunli/work/szw/script/DataProcess/data/label_yolo \
    --save_dir /home/sunli/work/szw/script/DataProcess/data/temp \
    --more_nc