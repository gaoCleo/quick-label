import json
import os.path
import sys

from PyQt5.QtCore import QRectF

import my_config as config
from typing import Union, Optional, Tuple, List

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QGraphicsScene, QListWidget, QGraphicsPixmapItem, \
    QGraphicsRectItem, QListWidgetItem, QGraphicsPolygonItem, QInputDialog, QLineEdit

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

        self.mode = 2
        self.img: Optional[GraphImage] = None
        self.default_category = 'object'
        self.obj_id = 0
        self.objs_can = ObjectItemCan()

        self.setupUi(self)
        self.btn_bound()
        self.init_ui()

        self.sig_bound()

        self.setup_models()

    def setup_models(self):
        # from object_detector.detector import ObjectDetector
        # self.obj_detector = ObjectDetector()
        from segment.segment_ai import SegmentAnythingAI
        self.segment_ai = SegmentAnythingAI(r'segment/segment_anything/sam_vit_h_4b8939.pth')

    def sig_bound(self):
        self.view.sig_add_box.connect(self.add_box_slot)
        self.view.sig_add_polygon.connect(self.add_mask_slot)
        self.view.sig_update_box.connect(self.update_box_coord_slot)
        self.view.sig_update_polygon.connect(self.update_mask_coord_slot)
        self.view.sig_remove_box.connect(self.remove_obj_item)
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
                self.set_flags_false()

    def set_revise_box(self):
        my_log('start revising objects')
        self.canvas_controller.set_flag(key=self.view.REVISE_BOX, flag=True)

    def open_pic(self):
        my_log("open pic")

        img_path, _ = QFileDialog.getOpenFileName(self.centralwidget, "选择图片", "../", "*.jpg;;*.png;;All Files(*)")
        my_log(f"open img: {img_path}")
        if os.path.exists(img_path):
            self.img = GraphImage(img_path, self.view.size())
            self.canvas_controller.set_img(self.img.item)

    def save_pic(self):
        print("save pic")
        if self.img is not None:
            file_name = os.path.basename(self.img.img_meta['path'])
            short_filename = file_name.split('.')[0]
            img_anno = {'file_name': file_name}
            obj_anns = []
            for obj in self.objs_can:
                # todo: 这里补充保存 mask
                obj_anns.append({"obj_id": self.obj_id,
                                 "annotation": {"box": obj.original_coord,
                                                "category": obj.category,
                                                "mask": f"{self.obj_id}.png"}})

            img_anno['obj_anns'] = obj_anns
            with open(os.path.join(config.save_dir, f'{short_filename}.json'), 'w', encoding='utf8') as f:
                json.dump(img_anno, f)

    def detect_box(self):
        print("detect box")
        if self.img is not None:
            xyxy_list, logits = self.obj_detector.detect(img_path=self.img.img_meta['path'],
                                                         text_prompt=self.le_prompt.text())

            for xyxy in xyxy_list:
                x1, y1, x2, y2 = xyxy
                self.canvas_controller.add_box(self.img.map_original2resized([(x1, y1), (x2, y2)]),
                                               self.color_controller.query_color(self.default_category))

    def detect_mask(self):
        print("detect mask")
        if self.img is not None:
            boxes = [obj_item.original_coord for obj_item in self.objs_can]
            self.segment_ai.set_img(self.img.img_meta['path'])
            for box in boxes:
                points = self.segment_ai.detect_by_boxes(boxes=[box,])[0]
                self.canvas_controller.add_mask_in_box(self.img.map_original2resized(points))

    def add_category(self):
        my_log("add a category")
        text, okPressed = QInputDialog.getText(self, "add a new category", "category:", QLineEdit.Normal, "")
        if okPressed and text != '':
            self.category_labels_controller.add_category_label(color=self.color_controller.random_select(text),
                                                               category=text)

    def delete_category(self):
        print("delete category")

    ######## signals func ###############
    def _add_obj_slot(self, obj_item):
        self.objs_list_controller.add_obj(obj_item,
                                          self.color_controller.query_color_name(self.default_category))
        self.obj_id += 1
        self.objs_can.add_obj(obj_item)

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

    def remove_obj_item(self, item: Union[QGraphicsRectItem,
                                          QListWidgetItem,
                                          QGraphicsPolygonItem]):
        obj_item_selected: ObjectItem = self.objs_can.query_obj(item)
        if obj_item_selected is not None:
            my_log(f'remove object id: {obj_item_selected.object_id}')

            self.view.sig_remove_box.disconnect(self.remove_obj_item)

            self.objs_list_controller.remove_listitem(obj_item_selected.list_item)
            self.objs_can.remove_obj(obj_item_selected)
            self.canvas_controller.remove_box(obj_item_selected.rect)

            self.view.sig_remove_box.connect(self.remove_obj_item)

    def select_obj_item(self, item: Union[QGraphicsRectItem,
                                          QListWidgetItem,
                                          QGraphicsPolygonItem]):
        obj_item_selected: ObjectItem = self.objs_can.query_obj(item)
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
        return  x1, y1, x2, y2

    def _transform_polygon_s2v(self, polygon_item: QGraphicsPolygonItem) -> List[Tuple[float, float]]:
        polygon = polygon_item.polygon()
        num_points = polygon.size()
        points = [polygon.at(i) for i in range(num_points)]
        points = self.canvas_controller.map_scene2view(points)
        if self.img is not None:
            points = self.img.map_resized2original(points)
        return points


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindows()
    window.show()
    sys.exit(app.exec_())
