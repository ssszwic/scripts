#!/bin/bash

# yolov5
model_path='/home/ssszw/Work/military_prj/RemoteSensing/model/yolov5.onnx'
input_name='images'
shape='f32:1x3x640x640'

# ssd
# model_path='/home/ssszw/Work/military_prj/RemoteSensing/model/ssd.onnx'
# input_name='input'
# shape='f32:1x3x500x500'

# faster_rcnn
# model_path='/home/ssszw/Work/military_prj/RemoteSensing/model/faster_rcnn.onnx'
# input_name='input'
# shape='f32:1x3x800x800'

python -m onnx_tool -i ${model_path} --mode profile --dynamic_shapes ${input_name}:${shape}

model             input_shape             Parameters          MACs(Flops = Mac * 2)
yolov5            (1, 3, 640, 640)        7,077,604           8,434,755,215       8G
ssd               (1, 3, 500, 500)        26,954,297          88,110,567,375      88G
faster_rcnn       (1, 3, 800, 800)        41,407,723          120,478,360,752     120G