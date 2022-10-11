import os
import sys
from pprint import pprint
import subprocess

import cv2
import imageio
import mmcv
from decord import VideoReader

parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)
import pandas as pd
import random
from functools import partial
from multiprocessing import Manager, Pool, cpu_count
import time
from moviepy.video.io.VideoFileClip import VideoFileClip

random.seed(123456789)
from tqdm import tqdm

from data_process.analysis import get_map_dict


def video_clip(source_dir='/home/jjiang/data/train_test_video', output_dir='/home/jjiang/data/zoo_clip'):
    background_per_video = 3
    min_duration = 5
    max_duration = 30
    background_idx = 0
    clip_overlap_ratio = 0.3
    if os.path.exists(output_dir):
        raise Exception(f'{output_dir} 已经存在！')
    else:
        os.makedirs(output_dir)
        os.makedirs(f'{output_dir}/videos')
    to_do_cmds = []

    total_class_clustered_dict, human_dict, total_class_human_changed = get_map_dict()
    label_dict = {total_class_human_changed[i]: i for i in range(len(total_class_human_changed))}
    label_dict['background'] = len(label_dict)

    for train_or_test in os.listdir(source_dir):
        if train_or_test == 'train':
            annotation_output_path = f'{output_dir}/train.list'
        else:
            annotation_output_path = f'{output_dir}/val.list'
        annotation_all = ''
        directory = f'{source_dir}/{train_or_test}'
        paths = sorted(os.listdir(directory))
        for i in tqdm(range(len(paths))):
            path = paths[i]
            if path.endswith('.mp4'):
                continue
            if path.endswith("'"):
                print(path)
                raise Exception
            path, suffix = os.path.splitext(path)

            source_video_path = f'{directory}/{path}.mp4'
            source_annotation_path = f'{directory}/{path}{suffix}'
            file_name = path.split('/')[-1]

            try:
                data = pd.read_excel(source_annotation_path, sheet_name='Sheet1')
            except ValueError:
                data = pd.read_excel(source_annotation_path, sheet_name='16755414')

            try:
                start_local = data['start'].tolist()
                end_local = data['end'].tolist()
                data_local = data['label'].tolist()
            except KeyError:
                if file_name == 'F3694小天鹅房车':
                    start_local = data['video_name'].tolist()
                    end_local = data['duration_s'].tolist()
                    data_local = data['duration_frame'].tolist()
                else:
                    print(f'{source_annotation_path}')
                    raise Exception
            try:
                total_time = get_video_duration(source_video_path)
            except ValueError:
                continue
            # 统计gaps
            total_gaps = len(start_local)
            gaps = []
            for segment_idx in range(total_gaps):
                gaps.append([start_local[segment_idx], end_local[segment_idx]])
            gaps = sorted(gaps, key=lambda x: x[0])
            background_num = 0
            local_segments = []
            # 加入背景
            if not os.path.exists(f'{output_dir}/videos/background'):
                os.makedirs(f'{output_dir}/videos/background')
            for segment_idx in range(total_gaps - 1):
                duration_background = random.randint(min_duration, max_duration)
                background_start = gaps[segment_idx][1]
                if background_start + duration_background > gaps[segment_idx + 1][0]:
                    continue
                # 超时了
                if background_start + duration_background > total_time:
                    continue

                output_video_name = f'background/background_{background_idx}.mp4'
                copy_path = f'{output_dir}/videos/{output_video_name}'
                # ff = f'ffmpeg -ss {background_start} -i {source_video_path} -t {duration_background} -c copy {copy_path}'

                # ff = f'ffmpeg -i {source_video_path} -ss {background_start} -to {background_start + duration_background} -an {copy_path}'
                # os.system(ff)
                local_segments.append([source_video_path, background_start, duration_background, copy_path])

                annotation_all += f'{output_video_name} {label_dict["background"]}\n'

                background_num += 1
                background_idx += 1
                if background_num >= background_per_video:
                    break

            for segment_idx in range(len(start_local)):
                start_time = start_local[segment_idx]
                end_time = end_local[segment_idx]
                duration = end_time - start_time
                label = data_local[segment_idx]

                if type(label) != str:
                    continue
                new_label = label.strip().lower()
                try:
                    new_label = total_class_clustered_dict[new_label] if total_class_clustered_dict[
                                                                             new_label] != "" else new_label
                    new_label = human_dict[new_label]
                except KeyError:
                    print(f'KeyError {new_label}')
                if new_label in total_class_human_changed and duration > 0:
                    local_idx = 0
                    while duration > max_duration:
                        output_video_name = f'{new_label}/{file_name}_{segment_idx}_{local_idx}.mp4'
                        output_video_name_without_blank = ''.join(output_video_name.split(' '))
                        output_video_name = output_video_name_without_blank
                        copy_path = f'{output_dir}/videos/{output_video_name}'

                        if not os.path.exists(f'{output_dir}/videos/{new_label}'):
                            os.makedirs(f'{output_dir}/videos/{new_label}')
                        # 超时了
                        if start_time + max_duration > total_time:
                            break
                        # ff = f'ffmpeg -ss {start_time} -i {source_video_path} -t {max_duration} -c copy {copy_path}'
                        # ff = f'ffmpeg -i {source_video_path} -ss {start_time} -to {start_time + max_duration} -an {copy_path}'
                        # os.system(ff)
                        local_segments.append([source_video_path, start_time, max_duration, copy_path])

                        annotation_all += f'{output_video_name} {label_dict[new_label]}\n'

                        start_time += int(max_duration * (1 - clip_overlap_ratio))
                        duration -= int(max_duration * (1 - clip_overlap_ratio))
                        local_idx += 1
                    # 最后一个小片段
                    if start_time + duration <= total_time:
                        output_video_name = f'{new_label}/{file_name}_{segment_idx}_{local_idx}.mp4'
                        output_video_name_without_blank = ''.join(output_video_name.split(' '))
                        output_video_name = output_video_name_without_blank
                        copy_path = f'{output_dir}/videos/{output_video_name}'

                        if not os.path.exists(f'{output_dir}/videos/{new_label}'):
                            os.makedirs(f'{output_dir}/videos/{new_label}')

                        # ff = f'ffmpeg -ss {start_time} -i {source_video_path} -t {duration} -c copy {copy_path}'
                        # ff = f'ffmpeg -i {source_video_path} -ss {start_time} -to {start_time + duration} -an {copy_path}'
                        # os.system(ff)
                        local_segments.append([source_video_path, start_time, duration, copy_path])

                        annotation_all += f'{output_video_name} {label_dict[new_label]}\n'
            to_do_cmds.append(local_segments)

        with open(annotation_output_path, mode='w', encoding='utf-8') as f:
            f.write(annotation_all)

    pool = Pool(int((cpu_count() - 1)))
    worker_fn = partial(do_cmd, to_do_cmds)
    ids = range(len(to_do_cmds))

    prog_bar = mmcv.ProgressBar(len(to_do_cmds))
    for _ in pool.imap_unordered(worker_fn, ids):
        prog_bar.update()
    # start checking
    pool.close()
    pool.join()
    print('all down!')


def do_cmd(cmds, idx):
    try:
        print(f'正在处理{cmds[idx][0][0]} ！')
    except IndexError:
        print('这个视频不需要切片！')
        return
    video = VideoFileClip(cmds[idx][0][0], audio=False)  # 去掉视频的音频
    video = video.without_audio()  # 去掉视频的音频
    for i in range(len(cmds[idx])):
        try:
            clip = video.subclip(cmds[idx][i][1], cmds[idx][i][1] + cmds[idx][i][2])  # 执行剪切操作
            clip.to_videofile(cmds[idx][i][3], fps=25, logger=None, remove_temp=True, audio=False, threads=2)  # 输出文件
        except ValueError:
            print('视频剪切长度不符合要求！')
            continue
        except IOError:
            print(f'视频[{cmds[idx][i][3]}]保存出错！')
            continue
    print(f'{cmds[idx][0][0]} 处理完毕！')


def _test_video_cv2(video_path):
    try:
        # imageio.get_reader(video_path, 'ffmpeg')
        capture = cv2.VideoCapture(video_path)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        count = 0
        while True:
            success, frame = capture.read()
            if not success:
                break
            else:
                count += 1
        if frame_count != count:
            return False, 0
        else:
            if frame_count < 20:
                print(f'{video_path} 太短了')
                return False, frame_count
            elif frame_count > 1000:
                print(f'{video_path} 太长了')
                return False, frame_count
            else:
                return True, frame_count
    except OSError:
        return False, 0


def _test_video_decord(lock, output_file, total_paths, idx):
    video_path = total_paths[idx]
    try:
        capture = VideoReader(video_path)
        frame_count = len(capture)
        if frame_count < 20:
            print(f'{video_path} 太短了')
            is_ok = False
        elif frame_count > 1000:
            print(f'{video_path} 太长了')
            is_ok = False
        else:
            # import numpy as np
            # frame_ids = np.array([0, frame_count - 1])
            # print(capture.get_batch(frame_ids).asnumpy())
            frame_count_real = get_real_frames(video_path)
            if frame_count_real != frame_count:
                print(f'frame_count_real {frame_count_real} != frame_count {frame_count}')
                is_ok = False
            else:
                print(f'{video_path} 完整！')
                is_ok = True
    except OSError:
        is_ok = False
    except RuntimeError:
        is_ok = False
    if not is_ok:
        lock.acquire()
        with open(output_file, 'a') as f:
            f.write(video_path + '\n')
        lock.release()


def remove_bad_video(output_dir='/home/jjiang/data/zoo_clip'):
    bad_output_file = '/home/jjiang/experiments/mmaction2/bad_video_list.txt'
    if os.path.exists(bad_output_file):
        os.remove(bad_output_file)
    # prepare for checking
    pool = Pool(cpu_count() - 1)
    lock = Manager().Lock()

    video_dir = f'{output_dir}/videos'
    total_paths = []
    for train_or_test in ['train.list', 'val.list']:
        new_result = ''
        with open(f'{output_dir}/{train_or_test}', mode='r', encoding='utf-8') as f:
            for line in tqdm(f.readlines()):
                file_name = line.strip().split(' ')[0]
                if not os.path.exists(f'{video_dir}/{file_name}'):
                    print(f'{video_dir}/{file_name}不存在！')
                else:
                    total_paths.append(f'{video_dir}/{file_name}')
                    new_result += line
        with open(f'{output_dir}/{train_or_test}', mode='w', encoding='utf-8') as f:
            f.write(new_result)

    worker_fn = partial(_test_video_decord, lock, bad_output_file, total_paths)
    ids = range(len(total_paths))

    prog_bar = mmcv.ProgressBar(len(total_paths))
    for _ in pool.imap_unordered(worker_fn, ids):
        prog_bar.update()
    # start checking
    pool.close()
    pool.join()
    error_count = 0
    try:
        with open(bad_output_file, mode='r', encoding='utf-8') as f:
            for _ in f.readlines():
                error_count += 1
        print(f'\n共{error_count}个错误视频！')
    except FileNotFoundError:
        print('\n视频全部完整！')


def check_result(output_dir='/home/jjiang/data/zoo_clip'):
    video_dir = f'{output_dir}/videos'
    for train_or_test in ['train.list', 'val.list']:
        label_set = set()
        with open(f'{output_dir}/{train_or_test}', mode='r', encoding='utf-8') as f:
            for line in tqdm(f.readlines()):
                file_name = line.strip().split(' ')[0]
                label = line.strip().split(' ')[1]
                label_set.add(label)
                if not os.path.exists(f'{video_dir}/{file_name}'):
                    print(f'文件{video_dir}/{file_name} 不存在！')
        label_set = sorted(list(label_set))
        print(len(label_set))
        print(label_set)


def del_result(to_delete_file, output_dir='/home/jjiang/data/zoo_clip'):
    to_delete_names = []
    with open(to_delete_file, mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            to_delete_names.append(line.strip())

    for to_delete_name in to_delete_names:
        # print('to_delete_name', to_delete_name)
        video_dir = f'{output_dir}/videos'
        for train_or_test in ['train.list', 'val.list']:
            new_txt = ''
            with open(f'{output_dir}/{train_or_test}', mode='r', encoding='utf-8') as f:
                for line in tqdm(f.readlines()):
                    file_name = line.strip().split(' ')[0]
                    # print(file_name)
                    label = line.strip().split(' ')[1]
                    if f'{video_dir}/{file_name}' == to_delete_name:
                        os.remove(f'{to_delete_name}')
                        print(f'找到坏的视频 {to_delete_name}')
                    else:
                        new_txt += line
            with open(f'{output_dir}/{train_or_test}', mode='w', encoding='utf-8') as f:
                f.write(new_txt)


def analysis_result(output_dir='/home/jjiang/data/zoo_clip'):
    for train_or_test in ['train.list', 'val.list']:
        label_dict = {}
        with open(f'{output_dir}/{train_or_test}', mode='r', encoding='utf-8') as f:
            for line in tqdm(f.readlines()):
                file_name = line.strip().split(' ')[0]
                label = file_name.split('/')[0]
                if label not in label_dict:
                    label_dict[label] = 1
                else:
                    label_dict[label] += 1

        label_set = sorted(list(label_dict.keys()))
        print(len(label_set))
        pprint(label_dict)


def get_video_duration(video_path: str):
    ext = os.path.splitext(video_path)[-1]
    if ext != '.mp4' and ext != '.avi' and ext != '.flv':
        raise Exception('format not support')
    ffprobe_cmd = 'ffprobe -i {} -show_entries format=duration -v quiet -of csv="p=0"'
    p = subprocess.Popen(
        ffprobe_cmd.format(video_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)
    out, err = p.communicate()
    duration_info = float(str(out, 'utf-8').strip())
    return int(duration_info)


def get_real_frames(video_path: str):
    ext = os.path.splitext(video_path)[-1]
    if ext != '.mp4' and ext != '.avi' and ext != '.flv':
        raise Exception('format not support')
    ffprobe_cmd = f'ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 {video_path}'
    p = subprocess.Popen(
        ffprobe_cmd.format(video_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)
    out, err = p.communicate()
    duration_info = float(str(out, 'utf-8').strip())
    return int(duration_info)


def remove_blank_path(train_test_dir='/home/jjiang/data/train_test_video'):
    for train_or_test in os.listdir(train_test_dir):
        directory = f'{train_test_dir}/{train_or_test}'
        for file in os.listdir(directory):
            path = f'{directory}/{file}'
            path_without_blank = ''.join(path.split(' '))
            if path != path_without_blank:
                print(f'{path} -> {path_without_blank}')
                os.rename(path, path_without_blank)


if __name__ == '__main__':
    # remove_blank_path()

    # video_clip(output_dir='/home/jjiang/data/zoo_clip_new')
    # remove_bad_video(output_dir='/home/jjiang/data/zoo_clip_new')
    # del_result(to_delete_file='/home/jjiang/experiments/mmaction2/bad_video_list.txt', output_dir='/home/jjiang/data/zoo_clip_new')
    # remove_bad_video(output_dir='/home/jjiang/data/zoo_clip_new')
    analysis_result(output_dir='/home/jjiang/data/zoo_clip_new')

    # 检查数据
    # python tools/analysis/check_videos.py configs/recognition/tsn/my_tsn_r50_video_1x1x8_100e_kinetics400_rgb.py \
    #     --decoder decord \
    #     --split train \
    #     --output-file invalid_videos_train.txt \
    #     --num-processes=5
    #
    # python tools/analysis/check_videos.py configs/recognition/tsn/my_tsn_r50_video_1x1x8_100e_kinetics400_rgb.py \
    #     --decoder decord \
    #     --split val \
    #     --output-file invalid_videos_val.txt \
    #     --num-processes=5

    # # 后续暂时不用，用mmaction的check
    # check_result()
