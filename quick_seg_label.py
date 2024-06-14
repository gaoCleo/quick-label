import argparse
import json
import os
from typing import Tuple

import cv2
from tqdm import tqdm

from object_detector.detector import ObjectDetector
from segment.segment_ai import SegmentAnythingAI

obj_detector = ObjectDetector()
segment_ai = SegmentAnythingAI(r'segment/segment_anything/sam_vit_h_4b8939.pth')


def pipeline(img_path: str, dsize: Tuple[int, int], save_img_dir: str, text_prompt: str, overlap: float):
    if not os.path.exists(save_img_dir):
        os.mkdir(save_img_dir)
    filename = os.path.basename(img_path).split('.')[0]
    filetype = os.path.basename(img_path).split('.')[1]
    # 切成 4 块并保存到新文件夹
    patches, _, _ = _patchify(cv2.imread(img_path), dsize, overlap=overlap, return_list=True)
    img_list = []
    for i, patch in enumerate(patches):
        img_save_name = os.path.join(save_img_dir, f'{filename}_{i}.{filetype}')
        cv2.imwrite(img_save_name, patch)
        img_list.append(img_save_name)

    for patch_path in img_list:
        object_id = 0
        img_anno = {'file_name': patch_path}
        obj_anns = []

        xyxy_list, _ = obj_detector.detect(img_path=patch_path,
                                           text_prompt=text_prompt)
        segment_ai.set_img(patch_path)
        for xyxy in xyxy_list:
            x1, y1, x2, y2 = xyxy
            h = y2 - y1

            if h > 2000:
                continue  # 跳过明显预测错误的框
            # 因为 Sam 模型会切割出一些小点点出来，所有要找最大面积的 contour 所以只能一个一个找
            points = segment_ai.detect_by_boxes(boxes=[xyxy, ])[0]
            obj_anns.append({"obj_id": object_id,
                             "annotation": {"box": xyxy,
                                            "category": text_prompt,
                                            "mask": points}})
            object_id += 1

        img_anno['obj_anns'] = obj_anns

        if not os.path.exists(os.path.join(save_img_dir, 'json')):
            os.mkdir(os.path.join(save_img_dir, 'json'))
        short_filename = os.path.basename(patch_path).split('.')[0]
        with open(os.path.join(save_img_dir, 'json', f'{short_filename}.json'), 'w', encoding='utf8') as f:
            json.dump(img_anno, f)


def pipeline_sam_only(img_path: str, dsize: Tuple[int, int], save_img_dir: str, text_prompt: str, overlap: float):
    if not os.path.exists(save_img_dir):
        os.mkdir(save_img_dir)
    filename = os.path.basename(img_path).split('.')[0]
    filetype = os.path.basename(img_path).split('.')[1]
    # 切成 4 块并保存到新文件夹
    # patches, _, _ = _patchify(cv2.imdecode(img_path), dsize, overlap=overlap, return_list=True)
    patches, _, _ = _patchify(cv2.imread(img_path), dsize, overlap=overlap, return_list=True)
    img_list = []
    for i, patch in enumerate(patches):
        img_save_name = os.path.join(save_img_dir, f'{filename}_{i}.{filetype}')
        cv2.imwrite(img_save_name, patch)
        img_list.append(img_save_name)

    for patch_path in tqdm(img_list):
        object_id = 0
        img_anno = {'file_name': patch_path}
        segment_ai.set_img(patch_path)

        img_anno['obj_anns'] = segment_ai.detect_auto(patch_path, category=text_prompt, obj_id=object_id)

        object_id += len(img_anno['obj_anns'])

        if not os.path.exists(os.path.join(save_img_dir, 'json')):
            os.mkdir(os.path.join(save_img_dir, 'json'))
        short_filename = os.path.basename(patch_path).split('.')[0]
        with open(os.path.join(save_img_dir, 'json', f'{short_filename}.json'), 'w', encoding='utf8') as f:
            json.dump(img_anno, f)


def _patchify(img, dsize, overlap=0.2, return_list=False):
    """
    将图片切割为 MxN 块 patches
    :param img: numpy (h, w, channel)
    :param dsize: (int_h, int_w)
    :param overlap: float 各个 patch 之间重叠的像素比例
    :param return_list: bool 如果为真，以数组的形式返回
    :return: dict，key 是位置元组，value 是切割后的 numpy 数组
        patches: dict[(i, j)]=crop_image
        overlap_rate: dict[(i, j)]=((croped_h-step_h)/croped_h, (croped_w-step_w)/croped_w) 重叠的像素占 patch 的比例
        start_pos: dict[(i, j)]=(h1, w1) patch左上角在原图中的坐标
    """
    h, w = img.shape[:2]
    num_h, num_w = dsize
    step_h = int(h / num_h)
    step_w = int(w / num_w)

    overlap_h = int(h * overlap)
    overlap_w = int(w * overlap)

    patches = [] if return_list else {}
    overlap_rate = [] if return_list else {}
    start_pos = [] if return_list else {}
    for i in range(num_h):
        for j in range(num_w):
            h1 = max(0, i * step_h - overlap_h)
            w1 = max(0, j * step_w - overlap_w)
            croped = img[h1:(i + 1) * step_h, w1:(j + 1) * step_w]
            if return_list:
                patches.append(croped)
            else:
                patches[(i, j)] = croped

            croped_h, croped_w = croped.shape[:2]
            overlap_r = ((croped_h - step_h) / croped_h, (croped_w - step_w) / croped_w)
            if return_list:
                overlap_rate.append(overlap_r)
            else:
                overlap_rate[(i, j)] = overlap_r

            if return_list:
                start_pos.append((h1, w1))
            else:
                start_pos[(i, j)] = (h1, w1)
    return patches, overlap_rate, start_pos


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--sr_dir', type=str, help='The root path of images to be detected')
    # parser.add_argument('--ds_dir', type=str, help='The root path of patches and json files to be saved')
    # parser.add_argument('--prompt', type=str, help='The prompt')
    # args = parser.parse_args()
    src_root_dir = 'G:\weeds_2024\Shanghai_mix'
    dst_root_dir = 'G:\weeds_2024\Shanghai_mix_processing'

    subdirs = os.listdir(src_root_dir)
    for subdir in subdirs:
        print('='*50, subdir, '='*50)
        if not os.path.exists(os.path.join(dst_root_dir, subdir)):
            os.mkdir(os.path.join(dst_root_dir, subdir))
        args = {
            'sr_dir': os.path.join(src_root_dir, subdir),
            'ds_dir': os.path.join(dst_root_dir, subdir),
            'prompt': 'wheat'
        }

        files = os.listdir(args['sr_dir'])
        for img in tqdm(files):
            # pipeline_sam_only(os.path.join(args.sr_dir, img), (3, 3), args.ds_dir, args.prompt, overlap=0.2)
            try:
                # pipeline_sam_only(os.path.join(args.sr_dir, img), (3, 3), args.ds_dir, args.prompt, overlap=0.2)
                pipeline(os.path.join(args['sr_dir'], img), (3, 3), args['ds_dir'], args['prompt'], overlap=0.0)
            except Exception as e:
                print(os.path.join(args['sr_dir'], img), 'can not be detected')
                print(e)
