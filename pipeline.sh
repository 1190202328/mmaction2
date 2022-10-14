#!/usr/bin/env bash

## shellcheck disable=SC2164
#cd ./data_process
#
## 切片并检查
#python video_clip.py
#
## shellcheck disable=SC2103
#cd ..

# 训练
CUDA_VISIBLE_DEVICES=0,1 \
  bash tools/dist_train.sh configs/recognition/slowfast/my_slowfast_r50_video_4x16x1_256e_kinetics400_rgb.py 2 \
  --work-dir work_dirs/slowfast \
  --validate --seed 123456789 --deterministic
