from typing import List, Optional, Tuple, Union

from PyQt5.QtCore import QRectF, QPointF, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QBrush, QTransform, QColor, QPolygonF
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, \
    QGraphicsPolygonItem, QGraphicsLineItem


class DrawableView(QGraphicsView):
    DRAW_BOX = 0
    REVISE_BOX = 1
    DRAW_POLYGON = 2
    REVISE_POLYGON = 3

    sig_update_box = pyqtSignal(QGraphicsRectItem)
    sig_add_box = pyqtSignal(QGraphicsRectItem)
    sig_remove_box = pyqtSignal(QGraphicsRectItem)
    sig_select_box = pyqtSignal(QGraphicsRectItem)

    sig_select_polygon = pyqtSignal(QGraphicsPolygonItem)
    sig_add_polygon = pyqtSignal(QGraphicsPolygonItem)
    sig_update_polygon = pyqtSignal(QGraphicsPolygonItem)

    def __init__(self, *args, **kwargs):
        super(DrawableView, self).__init__(*args, **kwargs)
        self.flags = {}
        self.drawn_box: List[QGraphicsRectItem] = []
        self.drawn_polygon: List[QGraphicsPolygonItem] = []

        # 与实时绘制 box 有关
        self.flags[self.DRAW_BOX] = False
        self.radius = 5
        self.start_scene_pt: Optional[QPointF] = None
        self.drawing_rect: Optional[QGraphicsRectItem] = None
        self.current_pen: QPen = QPen(Qt.green)

        # 修改已经绘制好的
        self.flags[self.REVISE_BOX] = False
        self.rect_selected: Optional[QGraphicsRectItem] = None  # 当前选中的 rect
        self.revise_box_item: Optional[BoxGraphicsItem] = None  # 当前出现在画面上的 revisable box，每次最多出现 1 个 revisable box
        self.rect_selected_pen: Optional[QPen] = None

        # 与实时绘制 polygon 有关
        self.anchor_radius = 5
        self.flags[self.DRAW_POLYGON] = False
        self.drawing_polygon_points: List[QPointF] = []
        self._drawing_polygon_items = []
        self._drawing_line_item: Optional[QGraphicsLineItem] = None

        # 修改已经绘制好的 polygon
        self.flags[self.REVISE_POLYGON] = False
        self.polygon_selected: Optional[QGraphicsPolygonItem] = None
        self.revise_polygon_item: Optional[RPolygonGraphicsItem] = None
        self.polygon_selected_pen: Optional[QPen] = None
        self.polygon_selected_brush: Optional[QBrush] = None

    def set_pen(self, color: Tuple[int, int, int]):
        self.current_pen = QPen(QColor(*color))

    def draw_box(self, box: Union[List, QRectF],
                 pen: QPen = QPen(Qt.green),
                 brush: QBrush = QBrush(Qt.transparent)) -> QGraphicsRectItem:
        """
        这个坐标是相对 scene 的坐标
        :param box: list as [x1, y1, x2, y2] in scene coord or QRectF in scene coord
        :param pen:
        :param brush:
        :return:
        """
        if type(box) is QRectF:
            rect = self.scene().addRect(box, pen, brush)
        else:
            x1, y1, x2, y2 = box
            w = x2 - x1
            h = y2 - y1
            rect = self.scene().addRect(QRectF(x1, y1, w, h),
                                        pen,
                                        brush)
        self.drawn_box.append(rect)
        self.sig_add_box.emit(rect)
        return rect

    def draw_polygon(self, polygon: QPolygonF,
                     pen: QPen,
                     brush: QBrush = QBrush(QColor(0, 0, 0, 20))) -> QGraphicsPolygonItem:
        polygon_item = self.scene().addPolygon(polygon, pen, brush)
        self.drawn_polygon.append(polygon_item)
        self.sig_add_polygon.emit(polygon_item)
        return polygon_item

    def set_flag(self, key: int, flag: bool):
        assert key in [self.DRAW_BOX, self.REVISE_BOX,
                       self.DRAW_POLYGON, self.REVISE_POLYGON]

        if flag is True:
            self.flags = dict.fromkeys(self.flags, False)
        self.flags[key] = flag

        if self.flags.get(self.DRAW_BOX) is False:
            if self.drawing_rect is not None:
                self.scene().removeItem(self.drawing_rect)

        self._remove_revise_box_item()
        if self.flags.get(self.REVISE_BOX) is False:
            for item in self.drawn_box:
                item.setFlag(QGraphicsRectItem.ItemIsSelectable, False)
        else:
            for item in self.drawn_box:
                item.setFlag(QGraphicsRectItem.ItemIsSelectable, True)

        self._remove_revise_polygon_item()
        if self.flags.get(self.REVISE_POLYGON) is False:
            for item in self.drawn_polygon:
                item.setFlag(QGraphicsPolygonItem.ItemIsSelectable, False)
        else:
            for item in self.drawn_polygon:
                item.setFlag(QGraphicsPolygonItem.ItemIsSelectable, True)

    def _remove_revise_box_item(self):
        if self.revise_box_item is not None:
            self.rect_selected.setPen(self.rect_selected_pen)
            self.rect_selected.setRect(self.revise_box_item.rect())
            self.scene().removeItem(self.revise_box_item)

            self.sig_update_box.emit(self.rect_selected)
            self.revise_box_item = None
            self.rect_selected = None
            self.rect_selected_pen = None

    def _remove_revise_polygon_item(self):
        if self.revise_polygon_item is not None:
            self.polygon_selected.setPen(self.polygon_selected_pen)
            self.polygon_selected.setBrush(self.polygon_selected_brush)
            self.polygon_selected.setPolygon(self.revise_polygon_item.polygon())
            self.scene().removeItem(self.revise_polygon_item)

            self.sig_update_polygon.emit(self.polygon_selected)
            self.revise_polygon_item = None
            self.polygon_selected = None
            self.polygon_selected_pen = None
            self.polygon_selected_brush = None

    def set_box_selected(self, item: QGraphicsRectItem):
        self.set_flag(self.REVISE_BOX, True)
        if item is not self.rect_selected:  # 重新选择另一个来修改
            if self.revise_box_item is not None:
                self._remove_revise_box_item()
        self.rect_selected = item
        self.rect_selected_pen = item.pen()
        item.setPen(QPen(Qt.transparent))
        self._add_editable_box(item.rect())
        self.sig_select_box.emit(item)

    def set_polygon_selected(self, item: QGraphicsPolygonItem):
        self.set_flag(self.REVISE_POLYGON, True)
        if item is not self.polygon_selected:  # 重新选择另一个来修改
            if self.revise_polygon_item is not None:
                self._remove_revise_polygon_item()
        self.polygon_selected = item
        self.polygon_selected_pen = item.pen()
        self.polygon_selected_brush = item.brush()
        item.setPen(QPen(Qt.transparent))
        self._add_editable_polygon(item.polygon())
        self.sig_select_polygon.emit(item)

    def remove_drawn_rect(self, item: QGraphicsRectItem):
        if item in self.drawn_box:
            self.drawn_box.remove(item)
            self.scene().removeItem(item)
            self.sig_remove_box.emit(item)

    def mousePressEvent(self, event) -> None:
        pt = event.pos()
        scene_pt = self.mapToScene(pt)
        print(f'here view: {pt}, map to scene: {scene_pt}')
        if self.flags.get(self.DRAW_BOX):
            self.start_scene_pt = scene_pt
        elif self.flags.get(self.REVISE_BOX):
            item = self.scene().itemAt(scene_pt, QTransform())
            print(f'select item {item}')
            if type(item) is QGraphicsRectItem:
                self.set_box_selected(item)
        elif self.flags.get(self.DRAW_POLYGON):
            self.setMouseTracking(True)
            # 判断是不是点击和第一个相同的点，即结束标记
            end_flag = False
            if len(self._drawing_polygon_items) > 0:
                if self._drawing_polygon_items[0].contains(scene_pt):
                    self.draw_polygon(QPolygonF(self.drawing_polygon_points),
                                      pen=self.current_pen)
                    self._init_drawing_polygon()
                    end_flag = True

            if not end_flag:
                self.drawing_polygon_points.append(scene_pt)
                anchor = QGraphicsRectItem(scene_pt.x() - self.anchor_radius,
                                           scene_pt.y() - self.anchor_radius,
                                           self.anchor_radius * 2,
                                           self.anchor_radius * 2)
                self._drawing_polygon_items.append(anchor)
                self.scene().addItem(anchor)

                if self._drawing_line_item is not None:
                    item = QGraphicsLineItem(self._drawing_line_item.line())
                    self.scene().addItem(item)
                    self._drawing_polygon_items.append(item)
                print('add a point')
        elif self.flags.get(self.REVISE_POLYGON):
            item = self.scene().itemAt(scene_pt, QTransform())
            print(f'select item {item}')
            if type(item) is QGraphicsPolygonItem:
                self.set_polygon_selected(item)

        super(DrawableView, self).mousePressEvent(event)

    def _add_editable_box(self, rect: QRectF):
        self.revise_box_item = box = BoxGraphicsItem(rect)
        self.scene().addItem(box)

    def _add_editable_polygon(self, polygon: QPolygonF):
        self.revise_polygon_item = p = RPolygonGraphicsItem(polygon)
        self.scene().addItem(p)

    def mouseMoveEvent(self, event) -> None:
        scene_pt = self.mapToScene(event.pos())
        if self.flags.get(self.DRAW_BOX):
            if self.drawing_rect is not None:
                self.scene().removeItem(self.drawing_rect)
            self.drawing_rect = self.scene().addRect(_get_rect_from_pts(scene_pt, self.start_scene_pt),
                                                     QPen(Qt.gray), QBrush(Qt.transparent))
        elif self.flags.get(self.DRAW_POLYGON):
            if len(self.drawing_polygon_points) > 0:
                pt1 = self.drawing_polygon_points[-1]
                if self._drawing_line_item is not None:
                    self.scene().removeItem(self._drawing_line_item)
                self._drawing_line_item = QGraphicsLineItem(pt1.x(), pt1.y(), scene_pt.x(), scene_pt.y())
                self.scene().addItem(self._drawing_line_item)

        super(DrawableView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self.flags.get(self.DRAW_BOX):
            scene_pt = self.mapToScene(event.pos())
            if scene_pt != self.start_scene_pt:
                self.draw_box([self.start_scene_pt.x(),
                               self.start_scene_pt.y(),
                               scene_pt.x(), scene_pt.y()],
                              pen=self.current_pen)

    def _init_drawing_polygon(self):
        self.setMouseTracking(False)
        for item in self._drawing_polygon_items:
            self.scene().removeItem(item)
        if self._drawing_line_item is not None:
            self.scene().removeItem(self._drawing_line_item)
        self.drawing_polygon_points.clear()
        self._drawing_polygon_items.clear()
        self._drawing_line_item = None


class BoxGraphicsItem(QGraphicsRectItem):
    TopLeft = 0
    TopRight = 1
    BottomRight = 2
    BottomLeft = 3

    def __init__(self, rect, radius: int = 5):
        super().__init__()
        self.radius = radius
        self.setRect(rect)
        # self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)

        self.path_circle = QPainterPath()
        self.path_rect = QPainterPath()
        self.anchors: List[QRectF] = []

        self._update_path_circle(rect)
        self._update_path_box(rect)

        self.select_point = None  # 目前正在拖动哪个点

    def _update_path_circle(self, rect: QRectF):
        self.path_circle.clear()
        self.anchors.clear()
        points: List[QPointF] = [rect.topLeft(), rect.topRight(),
                                 rect.bottomRight(), rect.bottomLeft()]

        for p in points:
            self.path_circle.addEllipse(p, self.radius, self.radius)
            self.anchors.append(_get_rect_of_circle(p, self.radius))

    def _update_path_box(self, rect):
        self.path_rect.clear()
        self.path_rect.addRect(rect)

    def boundingRect(self) -> QRectF:
        rect = self.rect()
        x1, y1 = rect.topLeft().x(), rect.topLeft().y()
        h, w = rect.height(), rect.width()

        x1 -= self.radius
        y1 -= self.radius
        h += self.radius * 2
        w += self.radius * 2
        return QRectF(x1, y1, w, h)

    def paint(self, painter: QPainter, item, widget=None) -> None:
        painter.save()
        painter.setPen(QPen(Qt.green))
        painter.drawPath(self.path_rect)
        painter.restore()

        painter.save()
        painter.setPen(QPen(Qt.NoPen))  # 不要边框
        painter.setBrush(QBrush(Qt.darkBlue))
        painter.setOpacity(0.5)
        painter.drawPath(self.path_circle)
        painter.restore()

        super().paint(painter, item, widget)

    def mousePressEvent(self, event) -> None:
        pos = event.pos()
        # 判定选中了谁
        self.select_point = self._select_who(pos)
        if self.select_point is not None:
            print(f'select: {self.select_point}')

    def mouseMoveEvent(self, event) -> None:
        if self.select_point is not None:
            self._repaint_rect(event.pos())
        else:
            super().mouseMoveEvent(event)

    def _select_who(self, pos):
        for i, anchor in enumerate(self.anchors):
            if anchor.contains(pos):
                return i
        return None

    def _repaint_rect(self, pos: QPointF):
        rect = self.rect()
        self.prepareGeometryChange()

        new_rect = None
        if self.select_point == self.TopLeft:
            new_rect = _get_rect_from_pts(pos, rect.bottomRight())
        elif self.select_point == self.TopRight:
            new_rect = _get_rect_from_pts(pos, rect.bottomLeft())
        elif self.select_point == self.BottomRight:
            new_rect = _get_rect_from_pts(pos, rect.topLeft())
        elif self.select_point == self.BottomLeft:
            new_rect = _get_rect_from_pts(pos, rect.topRight())

        if new_rect is not None:
            self.setRect(new_rect)
        self._update_data()

    def _update_data(self):
        rect = self.rect()
        self._update_path_circle(rect)
        self._update_path_box(rect)


class RPolygonGraphicsItem(QGraphicsPolygonItem):
    """
    右键添加新的 point
    中键可以删除 point
    """

    def __init__(self, polygon: QPolygonF, radius: int = 5):
        super(RPolygonGraphicsItem, self).__init__()
        self.setPolygon(polygon)
        self.setFlag(QGraphicsPolygonItem.ItemIsSelectable, True)
        self.radius = radius

        self.path_circle = QPainterPath()
        self.path_polygon = QPainterPath()
        self.anchors: List[QRectF] = []

        self._update_path_circle(polygon)
        self._update_path_polygon(polygon)

        self.select_point: Optional[int] = None  # the index in self.anchors

    def _update_path_circle(self, polygon: QPolygonF):
        self.path_circle.clear()
        self.anchors.clear()

        num_points = polygon.size()
        for i in range(num_points):
            point = polygon.at(i)
            self.path_circle.addEllipse(point, self.radius, self.radius)
            self.anchors.append(_get_rect_of_circle(point, self.radius))

    def _update_path_polygon(self, polygon: QPolygonF):
        self.path_polygon.clear()
        self.path_polygon.addPolygon(polygon)

    def mousePressEvent(self, event) -> None:
        pos = event.pos()
        # 判定选中了谁
        if event.buttons() == Qt.LeftButton:
            self.select_point = self._select_who(pos)
            if self.select_point is not None:
                print(f'select: {self.select_point}')
        elif event.buttons() == Qt.RightButton:
            # 按下右键，添加新的点
            self._repaint_added_pos_polygon(pos)
        elif event.buttons() == Qt.MidButton:
            self.select_point = self._select_who(pos)
            if self.select_point is not None:
                print(f'delete: {self.select_point}')
                self._repaint_deleted_pos_polygon()

    def mouseMoveEvent(self, event) -> None:
        if self.select_point is not None:
            self._repaint_polygon(event.pos())
        else:
            super().mouseMoveEvent(event)

    def paint(self, painter: QPainter, item, widget=None) -> None:
        painter.save()
        painter.setPen(QPen(Qt.green))
        painter.drawPath(self.path_polygon)
        painter.restore()

        painter.save()
        painter.setPen(QPen(Qt.NoPen))  # 不要边框
        painter.setBrush(QBrush(Qt.darkBlue))
        painter.setOpacity(0.5)
        painter.drawPath(self.path_circle)
        painter.restore()

        super().paint(painter, item, widget)

    def boundingRect(self) -> QRectF:
        rect = self.polygon().boundingRect()
        x1, y1 = rect.topLeft().x(), rect.topLeft().y()
        h, w = rect.height(), rect.width()

        x1 -= self.radius
        y1 -= self.radius
        h += self.radius * 2
        w += self.radius * 2
        return QRectF(x1, y1, w, h)

    def _select_who(self, pos):
        for i, anchor in enumerate(self.anchors):
            if anchor.contains(pos):
                return i
        return None

    def _repaint_deleted_pos_polygon(self):
        polygon = self.polygon()
        self.prepareGeometryChange()

        polygon.remove(self.select_point)
        self.setPolygon(polygon)

        self._update_data()

    def _repaint_added_pos_polygon(self, pos: QPointF):
        polygon = self.polygon()
        self.prepareGeometryChange()

        i = self._find_neighbor(pos)
        polygon.insert(i, pos)
        self.setPolygon(polygon)

        self._update_data()

    def _repaint_polygon(self, pos: QPointF):
        polygon = self.polygon()
        self.prepareGeometryChange()

        polygon.replace(self.select_point, pos)
        self.setPolygon(polygon)

        self._update_data()

    def _update_data(self):
        polygon = self.polygon()
        self._update_path_circle(polygon)
        self._update_path_polygon(polygon)

    def _find_neighbor(self, pos: QPointF) -> int:
        distance_list = []
        for point in self.anchors:
            distance_list.append(_distance(point.center(), pos))

        min_idx = distance_list.index(min(distance_list))
        return min_idx


def _get_rect_of_circle(center: QPointF, radius: float) -> QRectF:
    """
    返回以 center 为圆心，以 2*radius 为长、宽的矩形
    :param center:
    :param radius:
    :return:
    """
    x1 = center.x() - radius
    y1 = center.y() - radius
    return QRectF(x1, y1, 2 * radius, 2 * radius)


def _get_rect_from_pts(pt1: QPointF, pt2: QPointF) -> QRectF:
    """
    pt1 和 pt2 是矩形两个对角的点，但是不知道具体是哪两个对角的点
    返回以这两个点画出的矩形
    :param pt1:
    :param pt2:
    :return:
    """
    x1, y1 = pt1.x(), pt1.y()
    x2, y2 = pt2.x(), pt2.y()

    rect_x1 = min(x1, x2)
    rect_y1 = min(y1, y2)
    rect_w = abs(x1 - x2)
    rect_h = abs(y1 - y2)

    return QRectF(rect_x1, rect_y1, rect_w, rect_h)


def _distance(pt1: QPointF, pt2: QPointF) -> float:
    x1, y1 = pt1.x(), pt1.y()
    x2, y2 = pt2.x(), pt2.y()

    return (x1 - x2) ** 2 + (y1 - y2) ** 2
