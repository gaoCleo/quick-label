# --coding:utf-8--
from typing import List

import numpy as np
import matplotlib.pyplot as plt
import cv2
import sys

from tqdm import tqdm

sys.path.append('..')
from segment.segment_anything.segment_anything import sam_model_registry, SamPredictor, SamAutomaticMaskGenerator


class SegmentAnythingAI:
    def __init__(self, checkpoint_path: str,
                 device: str = 'cuda'):
        model_type: str = 'vit_h'
        sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        sam.to(device)
        self.predictor = SamPredictor(sam)
        self.mask_generator = SamAutomaticMaskGenerator(sam, points_per_batch=32, points_per_side=15)

    def set_img(self, img_path):
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        self.predictor.set_image(image)

    def detect_auto(self, img_path, return_mask_contour: bool = True, category: str = "", obj_id: int=0):
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        masks = self.mask_generator.generate(image)
        anns = []

        for i, mask in enumerate(masks):
            x1, y1, w, h = mask["bbox"]
            ann = {
                "obj_id": obj_id,
                "annotation": {
                    "box": [x1, y1, x1+w, y1+h],
                    "category": category
                }
            }

            if return_mask_contour:
                contours, _ = cv2.findContours(mask["segmentation"].astype(np.uint8) * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                nums = [contour.shape[0] for contour in contours]
                idx = nums.index(max(nums))
                epsilon = 0.005 * cv2.arcLength(contours[idx], True)
                approx = cv2.approxPolyDP(contours[idx], epsilon, True).squeeze(1).tolist()  # shape = [num_points, 1, 2]
                ann["annotation"]["mask"] = approx
            else:
                ann["annotation"]["mask"] = mask["segmentation"].astype(np.uint8) * 255

            obj_id += 1
            anns.append(ann)
        return anns

    def detect_by_boxes(self, boxes: list = None, return_mask_contour: bool = True) -> List:
        # add prompt
        if boxes is not None:
            boxes = np.array(boxes)

        # predict
        masks, scores, logits = self.predictor.predict(
            box=boxes,
            multimask_output=False,
        )  # mask: ndarray(1, h, w)

        num = len(boxes)
        masks_contour = []
        if return_mask_contour:
            for i in range(num):
                mask = masks[i].astype(np.uint8)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                nums = [contour.shape[0] for contour in contours]
                idx = nums.index(max(nums))
                epsilon = 0.005 * cv2.arcLength(contours[idx], True)
                approx = cv2.approxPolyDP(contours[idx], epsilon, True).squeeze(1).tolist()  # shape = [num_points, 1, 2]
                masks_contour.append(approx)
            return masks_contour
        else:
            return [masks[i].astype(np.uint8) for i in range(num)]

    def detect_by_points(self, img_path,
                         points: list = None,
                         labels: list = None):
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        self.predictor.set_image(image)

        # add prompt
        if points is not None and labels is not None:
            assert len(points) == len(labels)
            points = np.array(points)
            labels = np.array(labels)

        # predict
        masks, scores, logits = self.predictor.predict(
            point_coords=points,
            point_labels=labels,
            multimask_output=True,
        )

# if __name__ == '__main__':
#     detect_image(img_path='notebooks/images/truck.jpg',
#                  points=[[500, 375]],
#                  labels=[1],
#                  multimask_output=True)
