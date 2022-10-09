import os
import sys
import cv2
import imageio

parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)
import pandas as pd

from tqdm import tqdm

from data_process.analysis import get_map_dict


def video_clip(source_dir='/home/jjiang/data/train_test_video', output_dir='/home/jjiang/data/zoo_clip'):
    if os.path.exists(output_dir):
        raise Exception(f'{output_dir} 已经存在！')
    else:
        os.makedirs(output_dir)
        os.makedirs(f'{output_dir}/videos')

    total_class_clustered_dict, human_dict, total_class_human_changed = get_map_dict()
    label_dict = {total_class_human_changed[i]: i for i in range(len(total_class_human_changed))}

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
                if file_name == 'F3694 小天鹅房车':
                    start_local = data['video_name'].tolist()
                    end_local = data['duration_s'].tolist()
                    data_local = data['duration_frame'].tolist()
                else:
                    print(f'source_annotation_path')
                    raise Exception
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
                    output_video_name = f'{new_label}/{file_name}_{segment_idx}.mp4'
                    output_video_name_without_blank = ''.join(output_video_name.split(' '))
                    output_video_name = output_video_name_without_blank
                    copy_path = f'{output_dir}/videos/{output_video_name}'

                    if not os.path.exists(f'{output_dir}/videos/{new_label}'):
                        os.makedirs(f'{output_dir}/videos/{new_label}')

                    ff = f'ffmpeg -ss {start_time} -i {source_video_path} -t {duration} -c copy {copy_path}'
                    os.system(ff)
                    annotation_all += f'{output_video_name} {label_dict[new_label]}\n'
        with open(annotation_output_path, mode='w', encoding='utf-8') as f:
            f.write(annotation_all)


def _test_video(video_path):
    try:
        # imageio.get_reader(video_path, 'ffmpeg')
        capture = cv2.VideoCapture(video_path)
        success, frame = capture.read()
        if success:
            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(capture.get(cv2.CAP_PROP_FPS))
            total_length = int(frame_count / fps)
            if frame_count < 30:
                print(f'{video_path} 太短了')
                return False, frame_count
            elif frame_count > 10000:
                print(f'{video_path} 太长了')
                return False, frame_count
            else:
                return True, frame_count
        else:
            return False, 0
    except OSError:
        return False, 0


def remove_bad_video(output_dir='/home/jjiang/data/zoo_clip'):
    video_dir = f'{output_dir}/videos'
    for train_or_test in ['train.list', 'val.list']:
        new_txt = ''
        with open(f'{output_dir}/{train_or_test}', mode='r', encoding='utf-8') as f:
            for line in tqdm(f.readlines()):
                file_name = line.strip().split(' ')[0]
                check, frame_count = _test_video(f'{video_dir}/{file_name}')
                if not check:
                    print(f'{video_dir}/{file_name} 视频损坏')
                    try:
                        os.remove(f'{video_dir}/{file_name}')
                    except FileNotFoundError:
                        continue
                else:
                    new_txt += line
        with open(f'{output_dir}/{train_or_test}', mode='w', encoding='utf-8') as f:
            f.write(new_txt)


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


def del_result(output_dir='/home/jjiang/data/zoo_clip'):
    to_delete_name = '老虎小动/2021-08-26-11-30-02_2021-08-26-12-00-02_40.mp4'

    video_dir = f'{output_dir}/videos'
    for train_or_test in ['train.list', 'val.list']:
        new_txt = ''
        with open(f'{output_dir}/{train_or_test}', mode='r', encoding='utf-8') as f:
            for line in tqdm(f.readlines()):
                file_name = line.strip().split(' ')[0]
                label = line.strip().split(' ')[1]
                if file_name == to_delete_name:
                    os.remove(f'{video_dir}/{file_name}')
                    print(f'找到坏的视频 {video_dir}/{file_name}')
                else:
                    new_txt += line
        with open(f'{output_dir}/{train_or_test}', mode='w', encoding='utf-8') as f:
            f.write(new_txt)


if __name__ == '__main__':
    # video_clip()
    # remove_bad_video()
    # check_result()
    del_result()
