# --coding:utf-8--
import torch
from torchvision.ops import box_convert
from transformers import AutoModel

from groundingdino.util.inference import load_model, load_image, predict, annotate
import cv2

model = load_model("object_detector/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py",
                   "object_detector/GroundingDINO/weigts/groundingdino_swint_ogc.pth")
BOX_TRESHOLD = 0.25
TEXT_TRESHOLD = 0.25

class ObjectDetector:
    def __init__(self):
        pass

    def detect(self, img_path, text_prompt):
        image_source, image = load_image(img_path)

        boxes, logits, phrases = predict(
            model=model,
            image=image,
            caption=text_prompt,
            box_threshold=BOX_TRESHOLD,
            text_threshold=TEXT_TRESHOLD
        )

        h, w, _ = image_source.shape
        boxes = boxes * torch.Tensor([w, h, w, h])
        xyxy = box_convert(boxes=boxes, in_fmt="cxcywh", out_fmt="xyxy").numpy().tolist()
        logits = logits.cpu().tolist()
        return xyxy, logits