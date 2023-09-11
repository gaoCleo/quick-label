# --coding:utf-8--
import numpy as np
import matplotlib.pyplot as plt
import cv2
import sys

sys.path.append('..')
from segment_anything import sam_model_registry, SamPredictor


def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array(0.6)], axis=0)
    else:
        color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)


def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels == 1]  # 熟练运用张量作为切片 index
    neg_points = coords[labels == 0]
    # 用画散点图的函数，而不是用画点的函数，这样可以一次性把所有点都画出来
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green',
               marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red',
               marker='*', s=marker_size, edgecolor='white', linewidth=1.25)


def show_box(box, ax):
    # box = [x1, y1, x2, y2]
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0, 0, 0, 0), lw=2))


def detect_image(img_path,
                 points: list = None,
                 labels: list = None,
                 boxes: list = None,
                 multimask_output: bool = True,
                 is_plot: bool = True,
                 sam_checkpoint: str = '/home/gao/checkpoint/sam/sam_vit_h_4b8939.pth',
                 model_type: str = 'vit_h',
                 device: str = 'cuda'):
    image = cv2.imread(img_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    if is_plot:
        plt.figure(figsize=(10, 10))
        plt.imshow(image)
        plt.title('Original image')
        plt.axis('on')
        plt.show()

    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device)

    predictor = SamPredictor(sam)

    predictor.set_image(image)

    # add prompt
    if points is not None and labels is not None:
        assert len(points) == len(labels)
        points = np.array(points)
        labels = np.array(labels)
        if is_plot:
            plt.figure(figsize=(10, 10))
            plt.imshow(image)
            show_points(points, labels, plt.gca())
            plt.title('Image with points')
            plt.axis('on')
            plt.show()
    if boxes is not None:
        boxes = np.array(boxes)
        if is_plot:
            plt.figure(figsize=(10, 10))
            plt.imshow(image)
            for box in boxes:
                show_box(box, plt.gca())
            plt.title('Image with Box')
            plt.axis('on')
            plt.show()

    # predict
    masks, scores, logits = predictor.predict(
        point_coords=points,
        point_labels=labels,
        box=boxes,
        multimask_output=multimask_output,
    )

    for i, (mask, score) in enumerate(zip(masks, scores)):
        plt.figure(figsize=(10, 10))
        plt.imshow(image)
        show_mask(mask, plt.gca())
        if points is not None and labels is not None:
            show_points(points, labels, plt.gca())
        plt.title(f'Mask {i + 1}, Score: {score:.3f}', fontsize=18)
        plt.axis('off')
        plt.show()


if __name__ == '__main__':
    detect_image(img_path='notebooks/images/truck.jpg',
                 points=[[500, 375]],
                 labels=[1],
                 multimask_output=True)
