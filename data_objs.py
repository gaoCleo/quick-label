"""
这里存放自定义对象类
"""
from typing import List, Union, Optional, Tuple

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QListWidgetItem, QGraphicsPolygonItem


class GraphImage:
    def __init__(self, img_path: str, size: QSize):
        pixmap = QPixmap(img_path)
        self.img_meta = {
            'height': pixmap.height(),
            'width': pixmap.width(),
            'path': img_path,
        }
        pixmap = pixmap.scaled(size)
        self.img_meta['resized_height'] = pixmap.height()
        self.img_meta['resized_width'] = pixmap.width()
        self.item = QGraphicsPixmapItem(pixmap)

    def map_original2resized(self, coord) -> Tuple:
        x1, y1, x2, y2 = coord
        h_rate = self.img_meta['resized_height'] / self.img_meta['height']
        w_rate = self.img_meta['resized_width'] / self.img_meta['width']
        return x1 * w_rate, y1 * h_rate, x2 * w_rate, y2 * h_rate

    def map_resized2original(self, coord) -> Tuple:
        x1, y1, x2, y2 = coord
        h_rate = self.img_meta['resized_height'] / self.img_meta['height']
        w_rate = self.img_meta['resized_width'] / self.img_meta['width']
        return x1 / w_rate, y1 / h_rate, x2 / w_rate, y2 / h_rate


class ObjectItem:
    def __init__(self, obj_id: int, category: str = 'object',
                 rect: QGraphicsRectItem = None,
                 list_item: QListWidgetItem = None,
                 mask: QGraphicsPolygonItem = None,
                 original_coord: Tuple = None):
        self.object_id = obj_id

        self.rect: QGraphicsRectItem = rect
        self.list_item: QListWidgetItem = list_item
        self.mask: QGraphicsPolygonItem = mask

        self.original_coord: Tuple = original_coord
        self.category = category


class ObjectItemCan:
    def __init__(self):
        self._objs: List[ObjectItem] = []
        self._objs_id: List[int] = []
        self._objs_rect: List[QGraphicsRectItem] = []
        self._objs_listitem: List[QListWidgetItem] = []
        self._objs_mask: List[QGraphicsPolygonItem] = []

    def __len__(self):
        return len(self._objs)

    def __getitem__(self, item):
        return self._objs[item]

    def add_obj(self, obj: ObjectItem):
        if self._objs_id.count(obj.object_id) > 0:
            raise ValueError('object has been added into the can')
        self._objs.append(obj)
        self._objs_id.append(obj.object_id)
        self._objs_rect.append(obj.rect)
        self._objs_listitem.append(obj.list_item)
        self._objs_mask.append(obj.mask)

    def remove_obj(self, obj: ObjectItem):
        idx = self._query_index(obj)
        if idx is not None:
            del obj
            self._objs.pop(idx)
            self._objs_id.pop(idx)
            self._objs_rect.pop(idx)
            self._objs_listitem.pop(idx)
            self._objs_mask.pop(idx)

    def clear(self):
        self._objs.clear()
        self._objs_id.clear()
        self._objs_rect.clear()
        self._objs_listitem.clear()
        self._objs_mask.clear()

    def _query_index(self, obj_attr: Union[ObjectItem, int,
                                              QGraphicsRectItem,
                                              QListWidgetItem,
                                              QGraphicsPolygonItem]) -> Optional[int]:
        assert type(obj_attr) in [ObjectItem, int, QGraphicsRectItem, QListWidgetItem, QGraphicsPolygonItem]
        try:
            source_list = None
            if type(obj_attr) is ObjectItem:
                source_list = self._objs
            elif type(obj_attr) is int:
                source_list = self._objs_id
            elif type(obj_attr) is QGraphicsRectItem:
                source_list = self._objs_rect
            elif type(obj_attr) is QListWidgetItem:
                source_list = self._objs_listitem
            elif type(obj_attr) is self._objs_mask:
                source_list = self._objs_mask
            idx = source_list.index(obj_attr)
            return idx
        except ValueError:
            return None

    def query_id(self, obj_attr: Union[QGraphicsRectItem, QListWidgetItem, QGraphicsPolygonItem]) -> Optional[int]:
        idx = self._query_index(obj_attr)
        if idx is not None:
            return self._objs_id[idx]
        return None

    def query_obj(self, obj_attr: Union[int, QGraphicsRectItem, QListWidgetItem, QGraphicsPolygonItem]) -> Optional[ObjectItem]:
        idx = self._query_index(obj_attr)
        if idx is not None:
            return self._objs[idx]
        return None