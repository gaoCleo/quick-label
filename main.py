import json
import os.path
import sys

import cv2
import numpy as np
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPen, QBrush, QColor

import my_config
import my_config as config
from typing import Union, Optional, Tuple, List

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QGraphicsScene, QListWidget, QGraphicsPixmapItem, \
    QGraphicsRectItem, QListWidgetItem, QGraphicsPolygonItem, QInputDialog, QLineEdit, QMessageBox

from data_objs import GraphImage, ObjectItemCan, ObjectItem
from ui.ui import Ui_MainWindow
from ui_controller.canvas import CanvasController
from ui_controller.category_label import LabelController
from ui_controller.color import ColorController
from ui_controller.message_table import MessageTableController
from ui_controller.objs_list import ObjectListController


def my_log(msg: str):
    print(msg)


class MyMainWindows(QMainWindow, Ui_MainWindow):
    NO_MODE = 0
    BOX_MODE = 1
    MASK_MODE = 2

    def __init__(self):
        super(MyMainWindows, self).__init__()

        self.img_dir = None
        self.img_path_list = None
        self.img_path_list_idx = None

        self.mode = 2
        self.img: Optional[GraphImage] = None
        self.default_category = 'object'
        self.obj_id = 0
        self.objs_can = ObjectItemCan()
        self.obj_hide_mask: Optional[ObjectItem] = None
        self.current_selected_obj: Optional[ObjectItem] = None

        self.obj_detector = None
        self.segment_ai = None

        self.setupUi(self)
        self.btn_bound()
        self.init_ui()

        self.sig_bound()

        # self.setup_models()

    def setup_models(self):
        try:
            from object_detector.detector import ObjectDetector
            self.obj_detector = ObjectDetector()
        except:
            msg_box = QMessageBox(QMessageBox.Critical,
                                  '错误', 'grounding dino 模型部署错误，只能手动标注 bounding box 框，无法自动标注')
            msg_box.exec_()
        try:
            from segment.segment_ai import SegmentAnythingAI
            self.segment_ai = SegmentAnythingAI(r'segment/segment_anything/sam_vit_h_4b8939.pth')
        except:
            msg_box = QMessageBox(QMessageBox.Critical,
                                  '错误', 'segment anything 模型部署错误，只能手动标注 mask，无法自动标注')
            msg_box.exec_()

    def sig_bound(self):
        self.view.sig_add_box.connect(self.add_box_slot)
        self.view.sig_add_polygon.connect(self.add_mask_slot)
        self.view.sig_update_box.connect(self.update_box_coord_slot)
        self.view.sig_update_polygon.connect(self.update_mask_coord_slot)
        self.view.sig_select_box.connect(self.select_obj_item)
        self.view.sig_select_polygon.connect(self.select_obj_item)
        self.lw_objs.itemClicked.connect(self.select_obj_item)
        self.lw_labels.itemClicked.connect(self.set_current_category)
        self.lw_labels.itemClicked.connect(self.update_category)

    def init_ui(self):
        self.shift_mode()
        self.color_controller = ColorController()
        # 设置场景
        self.canvas_controller = CanvasController(self.view)
        self.canvas_controller.init_ui()
        self.canvas_controller.set_pen(self.color_controller.query_color(self.default_category))
        # self.canvas_controller.add_mask([(0, 0), (20, 0), (30, 10), (10, 30)])
        # 初始化信息表格
        self.obj_msg_controller = MessageTableController(self.tw_obj_message)
        self.obj_msg_controller.init_ui()
        self.lb_default_category.setText(self.default_category)

        self.objs_list_controller = ObjectListController(self.lw_objs)

        self.category_labels_controller = LabelController(self.lw_labels)
        self.category_labels_controller.init_ui(self.color_controller.default[0], self.default_category)

    def btn_bound(self):
        self.btn_mode.clicked.connect(self.shift_mode)
        self.btn_open_pic.clicked.connect(self.open_pic)
        self.btn_save_pic.clicked.connect(self.save_pic)
        self.btn_detect_box.clicked.connect(self.detect_box)
        self.btn_detect_mask.clicked.connect(self.detect_mask)
        self.btn_add_category.clicked.connect(self.add_category)
        self.btn_delete_category.clicked.connect(self.delete_category)
        self.btn_add_box.clicked.connect(self.set_add_box)
        self.btn_revise_box.clicked.connect(self.set_revise_box)
        self.btn_ok.clicked.connect(self.set_flags_false)
        self.btn_delete_obj.clicked.connect(self.delete_obj)
        self.btn_revise_mask.clicked.connect(self.set_revise_mask)
        self.btn_add_mask.clicked.connect(self.set_add_mask)
        self.btn_open_dir.clicked.connect(self.open_img_dir)
        self.btn_previous_img.clicked.connect(self.previous_img)
        self.btn_next_img.clicked.connect(self.next_img)
        self.btn_hide_mask.clicked.connect(self.hide_mask)

    ######## btn func ###############
    def shift_mode(self):
        self.mode = (self.mode + 1) % 3
        if self.mode == self.NO_MODE:
            self.btn_revise_box.setDisabled(True)
            self.btn_add_box.setDisabled(True)
            self.btn_revise_mask.setDisabled(True)
            self.btn_add_mask.setDisabled(True)
            self.btn_mode.setText('…')
        elif self.mode == self.BOX_MODE:
            self.btn_revise_box.setDisabled(False)
            self.btn_add_box.setDisabled(False)
            self.btn_revise_mask.setDisabled(True)
            self.btn_add_mask.setDisabled(True)
            self.btn_mode.setText('□')
        elif self.mode == self.MASK_MODE:
            self.btn_revise_box.setDisabled(True)
            self.btn_add_box.setDisabled(True)
            self.btn_revise_mask.setDisabled(False)
            self.btn_add_mask.setDisabled(False)
            self.btn_mode.setText('◇')

    def set_flags_false(self):
        my_log('set all flags to False')
        self.canvas_controller.set_flag(self.view.DRAW_BOX, False)
        self.canvas_controller.set_flag(self.view.REVISE_BOX, False)
        self.canvas_controller.set_flag(self.view.DRAW_POLYGON, False)
        self.canvas_controller.set_flag(self.view.REVISE_POLYGON, False)
        self.objs_list_controller.cancel_select()
        self.obj_msg_controller.clear()
        # my_log(f'drawn boxes:{self.canvas_controller.get_boxes()}')
        for obj_item in self.objs_can:
            print(obj_item.original_coord, obj_item.category)

    def set_add_box(self):
        my_log('start drawing bounding boxes')
        self.canvas_controller.set_flag(key=self.view.DRAW_BOX, flag=True)
        self.objs_list_controller.cancel_select()
        self.obj_msg_controller.clear()

    def set_add_mask(self):
        my_log('start add mask')
        self.canvas_controller.set_flag(key=self.view.DRAW_POLYGON, flag=True)
        self.objs_list_controller.cancel_select()
        self.obj_msg_controller.clear()

    def set_revise_mask(self):
        my_log('start revise mask')
        self.canvas_controller.set_flag(key=self.view.REVISE_POLYGON, flag=True)

    def delete_obj(self):
        my_log('delete an object')
        list_item = self.lw_objs.currentItem()
        if list_item is not None:
            obj_item = self.objs_can.query_obj(list_item)
            if obj_item is not None:
                self.objs_can.remove_obj(obj_item)
                self.objs_list_controller.remove_listitem(list_item)
                self.canvas_controller.remove_box(obj_item.rect)
                self.view.scene().removeItem(obj_item.mask)
                if self.view.revise_polygon_item is not None:
                    self.view.scene().removeItem(self.view.revise_polygon_item)
                    self.view.revise_polygon_item = None
                if self.view.revise_box_item is not None:
                    self.view.scene().removeItem(self.view.revise_box_item)
                self.set_flags_false()

    def set_revise_box(self):
        my_log('start revising objects')
        self.canvas_controller.set_flag(key=self.view.REVISE_BOX, flag=True)

    def open_pic(self):
        my_log("open pic")

        img_path, _ = QFileDialog.getOpenFileName(self.centralwidget, "选择图片", "../", "*.jpg;;*.png;;All Files(*)")
        my_log(f"open img: {img_path}")
        if os.path.exists(img_path):
            self._set_img(img_path)

    def save_pic(self):
        print("save pic")
        if self.img is not None:
            file_name = os.path.basename(self.img.img_meta['path'])
            short_filename = file_name.split('.')[0]
            img_anno = {'file_name': file_name}
            obj_anns = []
            for obj in self.objs_can:
                if obj.original_mask is not None:
                    mask_img = self._save_mask(obj.original_mask)
                    mask_dir = os.path.join(config.save_dir, short_filename)
                    if not os.path.exists(mask_dir):
                        os.mkdir(mask_dir)
                    cv2.imwrite(os.path.join(mask_dir, f'{obj.object_id}.png'), mask_img)
                obj_anns.append({"obj_id": obj.object_id,
                                 "annotation": {"box": obj.original_coord,
                                                "category": obj.category,
                                                "mask": obj.original_mask}})

            img_anno['obj_anns'] = obj_anns
            with open(os.path.join(config.save_dir, f'{short_filename}.json'), 'w', encoding='utf8') as f:
                json.dump(img_anno, f)
            return img_anno

    def detect_box(self):
        print("detect box")
        if self.img is not None and self.obj_detector is not None:
            try:
                xyxy_list, logits = self.obj_detector.detect(img_path=self.img.img_meta['path'],
                                                             text_prompt=self.le_prompt.text())

                for xyxy in xyxy_list:
                    x1, y1, x2, y2 = xyxy
                    self.canvas_controller.add_box(self.img.map_original2resized([(x1, y1), (x2, y2)]),
                                                   self.color_controller.query_color(self.default_category))
            except:
                msg_box = QMessageBox(QMessageBox.Critical,
                                      '错误', '模型检测错误，请检查文件夹存放结构是否正确，以及模型是否成功部署')
                msg_box.exec_()

    def detect_mask(self):
        print("detect mask")
        if self.img is not None and self.segment_ai is not None:
            try:
                self.segment_ai.set_img(self.img.img_meta['path'])
                for i, obj_item in enumerate(self.objs_can):
                    drawn_mask = obj_item.mask
                    if drawn_mask is None:  # 如果为真说明是画框生成的 obj，要用模型预测 mask；反之是自己画了 mask，不需要预测 mask
                        box = obj_item.original_coord
                        points = self.segment_ai.detect_by_boxes(boxes=[box, ])[0]
                        polygon_item = self.canvas_controller.add_mask_in_box(self.img.map_original2resized(points),
                                                                              color=self.color_controller.query_color(
                                                                                  obj_item.category))
                        self.objs_can.set_mask_item(i, polygon_item)
                        obj_item.original_mask = points

                        bounding_rect = polygon_item.polygon().boundingRect()
                        bounding_box = self._transform_rect_s2v(bounding_rect)
                        obj_item.original_coord = bounding_box

                        # 删除原来画的 bounding box
                        self.view.scene().removeItem(obj_item.rect)
                        self.objs_can.set_rect_item(i, None)
            except:
                msg_box = QMessageBox(QMessageBox.Critical,
                                      '错误', '模型检测错误，请检查文件夹存放结构是否正确，以及模型是否成功部署')
                msg_box.exec_()

    def add_category(self):
        my_log("add a category")
        text, okPressed = QInputDialog.getText(self, "add a new category", "category:", QLineEdit.Normal, "")
        if okPressed and text != '':
            self.category_labels_controller.add_category_label(color=self.color_controller.random_select(text),
                                                               category=text)

    def delete_category(self):
        print("delete category")
        self.category_labels_controller.del_category_label()

    def open_img_dir(self):
        my_log('open img dir')
        # img_dir = QFileDialog.getExistingDirectory(self, '选择文件夹', './')

        img_path, _ = QFileDialog.getOpenFileName(self.centralwidget, "选择图片", "../", "*.jpg;;*.png;;All Files(*)")
        my_log(f"open img: {img_path}")
        if os.path.exists(img_path):
            img_dir = os.path.dirname(img_path)
            self.img_dir = img_dir
            self.img_path_list = _get_img_paths(self.img_dir)
            self.img_path_list_idx = self.img_path_list.index((os.path.basename(img_path)))
            self._set_img(os.path.join(self.img_dir, self.img_path_list[self.img_path_list_idx]))
            try:
                self._read_annotations()
            except:
                pass

    def previous_img(self):
        my_log('annotate previous img')
        if self.img_path_list is not None \
                and self.img_path_list_idx is not None \
                and self.img_dir is not None:
            if self.img_path_list_idx > 1:
                self.img_path_list_idx -= 1

                img_anno = self.save_pic()  # 自动保存
                if my_config.COVER_JSON:
                    short_name = os.path.basename(self.img.img_meta['path']).split('.')[0]
                    json_path = os.path.join(self.img_dir, 'json', f'{short_name}.json')
                    with open(json_path, 'w', encoding='utf8') as f:
                        json.dump(img_anno, f)

                self._set_img(os.path.join(self.img_dir,
                                           self.img_path_list[self.img_path_list_idx]))
                try:
                    self._read_annotations()
                except:
                    pass

    def next_img(self):
        my_log('annotate next img')
        if self.img_path_list is not None \
                and self.img_path_list_idx is not None \
                and self.img_dir is not None:
            if self.img_path_list_idx < (len(self.img_path_list) - 1):
                self.img_path_list_idx += 1

                img_anno = self.save_pic()  # 自动保存
                if my_config.COVER_JSON:
                    short_name = os.path.basename(self.img.img_meta['path']).split('.')[0]
                    json_path = os.path.join(self.img_dir, 'json', f'{short_name}.json')
                    with open(json_path, 'w', encoding='utf8') as f:
                        json.dump(img_anno, f)

                self._set_img(os.path.join(self.img_dir,
                                           self.img_path_list[self.img_path_list_idx]))
                try:
                    self._read_annotations()
                except:
                    pass

    def hide_mask(self):
        if self.obj_hide_mask is None:
            if self.current_selected_obj is not None:
                self.obj_hide_mask = self.current_selected_obj
                mask_item = self.obj_hide_mask.mask
                if mask_item is not None:
                    mask_item.setPen(QPen(Qt.transparent))
                    mask_item.setBrush(QBrush(Qt.transparent))

                if self.view.revise_polygon_item is not None:
                    self.view.scene().removeItem(self.view.revise_polygon_item)
                    self.view.revise_polygon_item = None
        else:
            mask_item = self.obj_hide_mask.mask
            if mask_item is not None:
                category = self.obj_hide_mask.category
                color = self.color_controller.query_color(category)
                mask_item.setPen(QPen(QColor(*color)))
                mask_item.setBrush(QBrush(QColor(*color, my_config.BRUSH_INT)))
                self.obj_hide_mask = None


    ######## signals func ###############
    def _add_obj_slot(self, obj_item):
        list_item = self.objs_list_controller.add_obj(obj_item,
                                                      self.color_controller.query_color_name(
                                                          self.default_category))
        self.obj_id += 1
        self.objs_can.add_obj(obj_item)
        self.objs_can.set_list_item(idx=len(self.objs_can) - 1, item=list_item)

    def add_box_slot(self, rect: QGraphicsRectItem):
        coord = self._transform_rect_s2v(rect.rect())

        obj_item = ObjectItem(obj_id=self.obj_id, rect=rect, original_coord=coord, category=self.default_category)
        self._add_obj_slot(obj_item)

    def add_mask_slot(self, polygon_item: QGraphicsPolygonItem):
        bounding_rect = polygon_item.polygon().boundingRect()
        bounding_box = self._transform_rect_s2v(bounding_rect)
        points = self._transform_polygon_s2v(polygon_item)

        obj_item = ObjectItem(obj_id=self.obj_id, category=self.default_category,
                              original_coord=bounding_box,
                              mask=polygon_item, original_mask=points)
        self._add_obj_slot(obj_item)

    def update_box_coord_slot(self, rect: QGraphicsRectItem):
        coord = self._transform_rect_s2v(rect.rect())
        obj_item = self.objs_can.query_obj(rect)
        if obj_item is not None:
            obj_item.original_coord = coord

    def update_mask_coord_slot(self, polygon_item: QGraphicsPolygonItem):
        bounding_rect = polygon_item.polygon().boundingRect()
        bounding_box = self._transform_rect_s2v(bounding_rect)
        points = self._transform_polygon_s2v(polygon_item)

        obj_item = self.objs_can.query_obj(polygon_item)
        if obj_item is not None:
            obj_item.original_coord = bounding_box
            obj_item.original_mask = points

    def select_obj_item(self, item: Union[QGraphicsRectItem,
                                          QListWidgetItem,
                                          QGraphicsPolygonItem]):
        obj_item_selected: ObjectItem = self.objs_can.query_obj(item)
        self.current_selected_obj = obj_item_selected
        if obj_item_selected is not None:
            my_log(f'selected object id: {obj_item_selected.object_id}')
            # 当物体被选中后，一系列事情发生
            self.lw_objs.itemClicked.disconnect(self.select_obj_item)
            self.view.sig_select_box.disconnect(self.select_obj_item)
            self.view.sig_select_polygon.disconnect(self.select_obj_item)

            self.objs_list_controller.set_selected(obj_item_selected.list_item)
            if obj_item_selected.rect is not None:
                self.canvas_controller.set_selected_box(obj_item_selected.rect)
            if obj_item_selected.mask is not None:
                self.canvas_controller.set_selected_mask(obj_item_selected.mask)
            self.obj_msg_controller.set_obj_msg(obj_item_selected)

            self.view.sig_select_polygon.connect(self.select_obj_item)
            self.view.sig_select_box.connect(self.select_obj_item)
            self.lw_objs.itemClicked.connect(self.select_obj_item)

    def set_current_category(self, item: QListWidgetItem):
        self.lb_default_category.setText(item.text())
        self.default_category = item.text()
        self.canvas_controller.set_pen(self.color_controller.query_color(self.default_category))

    def update_category(self):
        item = self.objs_list_controller.lw.currentItem()
        obj_item_selected: Optional[ObjectItem] = None
        if item is not None:
            obj_item_selected = self.objs_can.query_obj(item)
        if obj_item_selected is not None:
            # update obj_item
            obj_item_selected.category = self.default_category
            # repaint
            self.objs_list_controller.revise_object(obj_item_selected,
                                                    self.color_controller.query_color_name(self.default_category))
            self.obj_msg_controller.set_obj_msg(obj_item_selected)
            self.canvas_controller.revise_obj_color(self.color_controller.query_color(self.default_category))

    ########## utils #################
    def _transform_rect_s2v(self, rect: QRectF) -> Tuple:
        pt1 = rect.topLeft()
        pt2 = rect.bottomRight()
        coord = self.canvas_controller.map_scene2view([pt1, pt2])
        if self.img is not None:
            coord = self.img.map_resized2original(coord)
        x1, y1, x2, y2 = coord[0][0], coord[0][1], coord[1][0], coord[1][1]
        return x1, y1, x2, y2

    def _transform_polygon_s2v(self, polygon_item: QGraphicsPolygonItem) -> List[Tuple[float, float]]:
        polygon = polygon_item.polygon()
        num_points = polygon.size()
        points = [polygon.at(i) for i in range(num_points)]
        points = self.canvas_controller.map_scene2view(points)
        if self.img is not None:
            points = self.img.map_resized2original(points)
        return points

    def _init_state(self):
        for obj_item in self.objs_can:
            # self.objs_can.remove_obj(obj_item)
            self.objs_list_controller.remove_listitem(obj_item.list_item)
            self.canvas_controller.remove_box(obj_item.rect)
            self.view.scene().removeItem(obj_item.mask)
        if self.view.revise_polygon_item is not None:
            self.view.scene().removeItem(self.view.revise_polygon_item)
        if self.view.revise_box_item is not None:
            self.view.scene().removeItem(self.view.revise_box_item)
            self.view.revise_box_item = None
        self.objs_can = ObjectItemCan()
        self.set_flags_false()
        self.lb_pic_name.setText('')
        self.obj_hide_mask = None
        self.current_selected_obj = None

    def _set_img(self, img_path: str):
        self._init_state()
        self.img = GraphImage(img_path, self.view.size())
        self.canvas_controller.set_img(self.img.item)
        self.lb_pic_name.setText(self.img.img_meta['path'])

    def _save_mask(self, points: List[Tuple[float, float]]):
        if self.img is not None:
            h = self.img.img_meta['height']
            w = self.img.img_meta['width']
            mask = np.zeros((h, w), dtype=np.uint8)
            cnt = np.array(points, dtype=np.int64)
            cnt = cnt[:, None, :]
            cv2.drawContours(mask, [cnt, ], -1, (255, 255, 255), -1)
            return mask

    def _read_annotations(self):
        if self.img_dir is not None and self.img is not None:
            short_name = os.path.basename(self.img.img_meta['path']).split('.')[0]
            json_path = os.path.join(self.img_dir, 'json', f'{short_name}.json')
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        obj_list = data["obj_anns"]
        for obj in obj_list:
            self.obj_id = obj["obj_id"]
            category = obj["annotation"]["category"]
            polygon = obj["annotation"]["mask"]
            box = obj["annotation"]["box"]

            color_name = self.color_controller.query_color_name(category)
            if color_name is None:
                color_name = self.color_controller.random_select(category)
                self.category_labels_controller.add_category_label(color=color_name,
                                                                   category=category)

            polygon_item = self.canvas_controller.add_mask_in_box(self.img.map_original2resized(polygon),
                                                                  color=self.color_controller.query_color(category))
            obj_item = ObjectItem(obj_id=self.obj_id,
                                  category=category,
                                  mask=polygon_item,
                                  original_coord=box,
                                  original_mask=polygon)

            self.objs_can.add_obj(obj_item)
            list_item = self.objs_list_controller.add_obj(obj_item, color_name)
            self.objs_can.set_list_item(idx=len(self.objs_can) - 1, item=list_item)
        self.obj_id += 1


def _is_picture(img_path: str):
    return img_path.endswith('.png') or img_path.endswith('.jpg')


def _get_img_paths(sr_dir: str):
    img_list = os.listdir(sr_dir)
    return list(filter(_is_picture, img_list))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindows()
    window.show()
    sys.exit(app.exec_())
