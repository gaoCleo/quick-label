from typing import List, Tuple

from PyQt5.QtCore import QRectF, Qt, QPoint, QPointF
from PyQt5.QtGui import QBrush, QPen, QColor, QPolygonF
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem

from data_objs import GraphImage
from ui.canvas_ui import BoxGraphicsItem, DrawableView, RPolygonGraphicsItem


class CanvasController:
    """
    关于坐标的说明：因为我把图片 offset 放在view左上角，所以图片坐标和 view 坐标是一致的
    """

    def __init__(self, graphicsView):
        self.img: GraphImage = None
        self.scene: QGraphicsScene = None
        self.view: DrawableView = graphicsView

    def init_ui(self):
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(Qt.darkGray))
        self.view.setScene(self.scene)
        self.view.setSceneRect(QRectF(0, 0, 200, 200))

    def set_img(self, graphicsPixmapItem: QGraphicsPixmapItem):
        self.img = graphicsPixmapItem
        graphicsPixmapItem.setOffset(self.view.mapToScene(0, 0))
        self.scene.addItem(graphicsPixmapItem)
        # todo: clear others

    def set_flag(self, key: int, flag: bool):
        self.view.set_flag(key, flag)

    def set_pen(self, color: Tuple[int, int, int]):
        self.view.set_pen(color)

    def add_box(self, box_coord, color: Tuple[int, int, int]):
        """
        在场景中添加 box
        :param box_coord: [x1, y1, x2, y2] in view coord
        :param color:
        :return:
        """
        pen = QPen(QColor(*color))
        self.view.draw_box(self.map_view2scene(box_coord), pen)

    def add_mask(self, mask: List[Tuple[float, float]]):
        points = []
        for point in mask:
            points.append(QPointF(point[0], point[1]))
        polygon = QPolygonF(points)
        polygon_item = RPolygonGraphicsItem(polygon)
        self.scene.addItem(polygon_item)

    def get_boxes(self) -> List[Tuple]:
        drawn_boxes = [self.map_scene2view(item.rect())
                       for item in self.view.drawn_box]
        return drawn_boxes

    def set_selected_box(self, rect: QGraphicsRectItem):
        self.view.set_box_selected(rect)

    def remove_box(self, rect: QGraphicsRectItem):
        self.view.remove_drawn_rect(rect)

    def map_scene2view(self, rect: QRectF) -> Tuple:
        """

        :param rect:
        :return: tuple(x1, y1, x2, y2)
        """
        pt1 = rect.topLeft()
        pt2 = rect.bottomRight()

        pt1 = self.view.mapFromScene(pt1)
        pt2 = self.view.mapFromScene(pt2)

        return pt1.x(), pt1.y(), pt2.x(), pt2.y()

    def map_view2scene(self, box_coord) -> QRectF:
        """

        :param box_coord: [x1, y1, x2, y2] in view coord
        :return: QRectF in scene coord
        """
        x1, y1, x2, y2 = box_coord
        pt1 = self.view.mapToScene(QPoint(int(x1), int(y1)))
        pt2 = self.view.mapToScene(QPoint(int(x2), int(y2)))
        return QRectF(pt1, pt2)

    def revise_rect_color(self, color: Tuple[int, int, int]):
        pen = QPen(QColor(*color))
        self.view.rect_selected_pen = pen
