from typing import List, Optional, Tuple

from PyQt5.QtCore import QRectF, QPointF, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QBrush, QTransform, QColor
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem


class DrawableView(QGraphicsView):
    DRAW_BOX = 0
    REVISE_BOX = 1

    sig_update_box = pyqtSignal(QGraphicsRectItem)
    sig_add_box = pyqtSignal(QGraphicsRectItem)
    sig_remove_box = pyqtSignal(QGraphicsRectItem)
    sig_select_box = pyqtSignal(QGraphicsRectItem)

    def __init__(self, *args, **kwargs):
        super(DrawableView, self).__init__(*args, **kwargs)
        self.flags = {}
        self.drawn_box: List[QGraphicsRectItem] = []

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

    def set_pen(self, color: Tuple[int, int, int]):
        self.current_pen = QPen(QColor(*color))

    def draw_box(self, box: [List, QRectF],
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

    def set_flag(self, key: int, flag: bool):
        assert key in [self.DRAW_BOX, self.REVISE_BOX]

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

    def _remove_revise_box_item(self):
        if self.revise_box_item is not None:
            self.rect_selected.setPen(self.rect_selected_pen)
            self.rect_selected.setRect(self.revise_box_item.rect())
            self.scene().removeItem(self.revise_box_item)

            self.sig_update_box.emit(self.rect_selected)
            self.revise_box_item = None
            self.rect_selected = None
            self.rect_selected_pen = None

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

        super(DrawableView, self).mousePressEvent(event)

    def _add_editable_box(self, rect: QRectF):
        self.revise_box_item = box = BoxGraphicsItem(rect)
        self.scene().addItem(box)

    def mouseMoveEvent(self, event) -> None:
        if self.flags.get(self.DRAW_BOX):
            if self.drawing_rect is not None:
                self.scene().removeItem(self.drawing_rect)

            scene_pt = self.mapToScene(event.pos())
            self.drawing_rect = self.scene().addRect(_get_rect_from_pts(scene_pt, self.start_scene_pt),
                                                     QPen(Qt.gray), QBrush(Qt.transparent))
        super(DrawableView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self.flags.get(self.DRAW_BOX):
            scene_pt = self.mapToScene(event.pos())
            if scene_pt != self.start_scene_pt:
                self.draw_box([self.start_scene_pt.x(),
                               self.start_scene_pt.y(),
                               scene_pt.x(), scene_pt.y()],
                              pen=self.current_pen)


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


def _get_rect_of_circle(center: QPointF, radius: float):
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
