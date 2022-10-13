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
CUDA_VISIBLE_DEVICES=0,1,2 \
  bash tools/dist_train.sh configs/recognition/tsn/my_tsn_r50_video_1x1x8_100e_kinetics400_rgb.py 3 \
  --work-dir work_dirs/tsn_small_new \
  --validate --seed 123456789 --deterministic
