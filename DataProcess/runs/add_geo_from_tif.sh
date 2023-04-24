#!/bin/bash
cd /home/ssszw/Work/military_prj/images/test_ps/post
names=$(ls)
for name in $names
do
echo ${name}
python /home/ssszw/Work/scripts/DataProcess/add_geo_from_tif.py \
        --img_path /home/ssszw/Work/military_prj/images/test_ps/post/${name} \
        --src_path /home/ssszw/Work/military_prj/images/test_ps/pre_tif/${name} \
        --save_path /home/ssszw/Work/military_prj/images/test_ps/post_tif/${name}
done