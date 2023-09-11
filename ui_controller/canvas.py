from typing import List, Tuple

from PyQt5.QtCore import QRectF, Qt, QPoint, QPointF
from PyQt5.QtGui import QBrush, QPen, QColor, QPolygonF
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsPolygonItem

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
        x1, y1 = box_coord[0]
        x2, y2 = box_coord[1]

        self.view.draw_box(QRectF(*(self.map_view2scene([(x1, y1), (x2, y2)]))), pen)

    def add_mask_in_box(self, mask: List[Tuple[float, float]], color: Tuple[int, int, int]) -> QGraphicsPolygonItem:
        """
        添加 mask 但不新增 objects
        :param mask:
        :return:
        """
        points = self.map_view2scene(mask)
        polygon = QPolygonF(points)
        # polygon_item = RPolygonGraphicsItem(polygon)
        # self.scene.addItem(polygon_item)
        pen = QPen(QColor(*color))
        brush = QBrush(QColor(*color, 150))
        return self.scene.addPolygon(polygon, pen, brush)

    def set_selected_box(self, rect: QGraphicsRectItem):
        self.view.set_box_selected(rect)

    def set_selected_mask(self, polygon: QGraphicsPolygonItem):
        self.view.set_polygon_selected(polygon)

    def remove_box(self, rect: QGraphicsRectItem):
        self.view.remove_drawn_rect(rect)

    def map_scene2view(self, points: List[QPointF]) -> List[Tuple[float, float]]:
        """

        :param points:
        :return: tuple(x1, y1, x2, y2)
        """
        new_points = []
        for pt in points:
            new_pt = self.view.mapFromScene(pt)
            new_points.append((new_pt.x(), new_pt.y()))

        return new_points

    def map_view2scene(self, points: List[Tuple[float, float]]) -> List[QPointF]:
        """

        :param points: in view coord
        :return: QRectF in scene coord
        """
        pts = []
        for point in points:
            pt = self.view.mapToScene(QPoint(int(point[0]), int(point[1])))
            pts.append(pt)
        return pts

    def revise_obj_color(self, color: Tuple[int, int, int]):
        pen = QPen(QColor(*color))
        brush = QBrush(QColor(*color, 150))
        self.view.rect_selected_pen = pen
        self.view.polygon_selected_pen = pen
        self.view.polygon_selected_brush = brush
