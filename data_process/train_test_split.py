import os
import random
from pprint import pprint
import shutil

from tqdm import tqdm

random.seed(123456789)


def get_total_video_paths(dirs='/home/jjiang/data/zoo'):
    paths = []
    for directory in os.listdir(dirs):
        video_dir = f'{dirs}/{directory}'
        if directory == '标注':
            continue
        elif directory in ['210716', '211026', '220413', 'earlyer']:
            for file in os.listdir(video_dir):
                prefix, suffix = os.path.splitext(file)
                if suffix in ['.xlsx', '.xls']:
                    continue
                relative_path = f'{video_dir}/{prefix}'
                paths.append(relative_path)
        elif directory == '220113':
            for sub_directory in os.listdir(video_dir):
                for file in os.listdir(f'{video_dir}/{sub_directory}'):
                    prefix, suffix = os.path.splitext(file)
                    if suffix in ['.xlsx', '.xls']:
                        continue
                    relative_path = f'{video_dir}/{sub_directory}/{prefix}'
                    paths.append(relative_path)
        else:
            raise Exception('不符合规范的文件夹')
    for path in paths:
        source_video_path = f'{path}.mp4'
        source_annotation_path = f'{path}.xlsx'
        if not os.path.exists(source_annotation_path):
            source_annotation_path = f'{path}.xls'
        if not os.path.exists(source_video_path) or not os.path.exists(source_annotation_path):
            raise Exception(f'{source_video_path} {source_annotation_path} 路径有问题！')
    return paths


def train_test_video_split(dirs='/home/jjiang/data/zoo', output_dir='/home/jjiang/data/train_test_video',
                           test_ratio=0.25):
    if os.path.exists(output_dir):
        raise Exception(f'{output_dir} 已经存在！')
    else:
        os.makedirs(output_dir)
        os.makedirs(f'{output_dir}/train')
        os.makedirs(f'{output_dir}/test')
    paths = get_total_video_paths(dirs)
    total_videos = len(paths)
    print(total_videos)
    random.shuffle(paths)
    test_idx = random.sample(range(total_videos), k=int(total_videos * test_ratio))
    test_idx = set(test_idx)
    for i in tqdm(range(len(paths))):
        path = paths[i]
        source_video_path = f'{path}.mp4'
        source_annotation_path = f'{path}.xlsx'
        suffix = '.xlsx'
        if not os.path.exists(source_annotation_path):
            source_annotation_path = f'{path}.xls'
            suffix = '.xls'
        file_name = path.split('/')[-1]

        train_or_test = 'test' if i in test_idx else 'train'
        target_video_path = f'{output_dir}/{train_or_test}/{file_name}.mp4'
        target_annotation_path = f'{output_dir}/{train_or_test}/{file_name}{suffix}'

        if os.path.exists(target_video_path) or os.path.exists(target_annotation_path):
            raise Exception(f'路径{target_video_path} {target_annotation_path} 已经存在！')
        shutil.copyfile(source_video_path, target_video_path)
        shutil.copyfile(source_annotation_path, target_annotation_path)


if __name__ == '__main__':
    train_test_video_split()
