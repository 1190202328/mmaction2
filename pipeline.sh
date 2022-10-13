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
  bash tools/dist_train.sh configs/recognition/tsm/my_tsm_r50_video_1x1x8_50e_kinetics400_rgb.py 2 \
  --work-dir work_dirs/tsm \
  --validate --seed 123456789 --deterministic
