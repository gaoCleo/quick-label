import json
import os.path
import sys
import my_config as config
from typing import Union, Optional

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
    def __init__(self):
        super(MyMainWindows, self).__init__()

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
        from object_detector.detector import ObjectDetector
        self.obj_detector = ObjectDetector()

    def sig_bound(self):
        self.view.sig_add_box.connect(self.add_box)
        self.view.sig_update_box.connect(self.update_box_coord)
        self.view.sig_remove_box.connect(self.remove_obj_item)
        self.view.sig_select_box.connect(self.select_obj_item)
        self.lw_objs.itemClicked.connect(self.select_obj_item)
        self.lw_labels.itemClicked.connect(self.set_current_category)
        self.lw_labels.itemClicked.connect(self.update_category)

    def init_ui(self):
        self.color_controller = ColorController()
        # 设置场景
        self.canvas_controller = CanvasController(self.view)
        self.canvas_controller.init_ui()
        self.canvas_controller.set_pen(self.color_controller.query_color(self.default_category))
        # 初始化信息表格
        self.obj_msg_controller = MessageTableController(self.tw_obj_message)
        self.obj_msg_controller.init_ui()
        self.lb_default_category.setText(self.default_category)

        self.objs_list_controller = ObjectListController(self.lw_objs)

        self.category_labels_controller = LabelController(self.lw_labels)
        self.category_labels_controller.init_ui(self.color_controller.default[0], self.default_category)

    def btn_bound(self):
        self.btn_open_pic.clicked.connect(self.open_pic)
        self.btn_save_pic.clicked.connect(self.save_pic)
        self.btn_detect_box.clicked.connect(self.detect_box)
        self.btn_detect_mask.clicked.connect(self.detect_mask)
        self.btn_add_category.clicked.connect(self.add_category)
        self.btn_delete_category.clicked.connect(self.delete_category)
        self.btn_add_box.clicked.connect(self.set_add_box)
        self.btn_revise.clicked.connect(self.set_revise)
        self.btn_ok.clicked.connect(self.set_flags_false)
        self.btn_delete_obj.clicked.connect(self.delete_obj)

    ######## btn func ###############
    def set_flags_false(self):
        my_log('set all flags to False')
        self.canvas_controller.set_flag(self.view.DRAW_BOX, False)
        self.canvas_controller.set_flag(self.view.REVISE_BOX, False)
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

    def set_revise(self):
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
                self.canvas_controller.add_box(self.img.map_original2resized(xyxy),
                                               self.color_controller.query_color(self.default_category))

    def detect_mask(self):
        print("detect mask")

    def add_category(self):
        my_log("add a category")
        text, okPressed = QInputDialog.getText(self, "add a new category", "category:", QLineEdit.Normal, "")
        if okPressed and text != '':
            self.category_labels_controller.add_category_label(color=self.color_controller.random_select(text),
                                                               category=text)

    def delete_category(self):
        print("delete category")

    ######## signals func ###############
    def add_box(self, rect):
        coord = self.canvas_controller.map_scene2view(rect.rect())
        if self.img is not None:
            coord = self.img.map_resized2original(coord)
        obj_item = ObjectItem(obj_id=self.obj_id, rect=rect, original_coord=coord, category=self.default_category)
        self.objs_list_controller.add_obj(obj_item,
                                          self.color_controller.query_color_name(self.default_category))
        self.obj_id += 1
        self.objs_can.add_obj(obj_item)

    def update_box_coord(self, rect):
        coord = self.canvas_controller.map_scene2view(rect.rect())
        if self.img is not None:
            coord = self.img.map_resized2original(coord)
        obj_item = self.objs_can.query_obj(rect)
        if obj_item is not None:
            obj_item.original_coord = coord

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

            self.objs_list_controller.set_selected(obj_item_selected.list_item)
            self.canvas_controller.set_selected_box(obj_item_selected.rect)
            self.obj_msg_controller.set_obj_msg(obj_item_selected)

            self.view.sig_select_box.connect(self.select_obj_item)
            self.lw_objs.itemClicked.connect(self.select_obj_item)

    def set_current_category(self, item: QListWidgetItem):
        self.lb_default_category.setText(item.text())
        self.default_category = item.text()
        self.canvas_controller.set_pen(self.color_controller.query_color(self.default_category))

    def update_category(self):
        item = self.objs_list_controller.lw.currentItem()
        obj_item_selected = None
        if item is not None:
            obj_item_selected: ObjectItem = self.objs_can.query_obj(item)
        if obj_item_selected is not None:
            # update obj_item
            obj_item_selected.category = self.default_category
            # repaint
            self.objs_list_controller.revise_object(obj_item_selected,
                                                    self.color_controller.query_color_name(self.default_category))
            self.obj_msg_controller.set_obj_msg(obj_item_selected)
            self.canvas_controller.revise_rect_color(self.color_controller.query_color(self.default_category))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindows()
    window.show()
    sys.exit(app.exec_())
