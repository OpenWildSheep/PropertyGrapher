from math import sqrt

from PySide2.QtCore import QPointF, Qt
from PySide2.QtGui import QPolygonF, QPainterPath, QPen, QPainter
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsScene,
    QWidget,
    QStyleOptionGraphicsItem,
)


class Arrow(QGraphicsItem):
    def __init__(
        self, arrow_data: dict, scene: QGraphicsScene, parent: QWidget = None
    ) -> None:
        super().__init__(parent=parent)
        self.pen = self.get_pen(arrow_data)
        self.head_node_id = arrow_data.get("head")
        self.tail_node_id = arrow_data.get("tail")
        self.points = self.get_points(arrow_data)

        self.path = self.get_path()

        scene.addItem(self)
        self.setZValue(100)

    @staticmethod
    def get_points(arrow_data: dict):

        for item in arrow_data["_draw_"]:
            points = item.get("points")
            if points:
                return [QPointF(*point) for point in points]

        raise Exception("Arrow should always have points")

    @staticmethod
    def get_pen(arrow_data: dict):
        color = None
        for item in arrow_data["_draw_"]:
            color = item.get("color")
            if color:
                break

        if not color:
            raise Exception("Arrow should always have a color")

        pen = QPen(color)
        pen.setWidth(2)
        pen.setColor(color)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)

        style = arrow_data.get("style", "solid")
        if style == "dashed":
            pen.setDashPattern([2, 4])
        else:
            pen.setStyle(Qt.SolidLine)

        return pen

    def get_path(self) -> QPainterPath:
        """Create cubic path from points."""
        path = QPainterPath()
        path.moveTo(self.points[0])

        i = 1
        while i < len(self.points) - 2:
            path.cubicTo(*self.points[i : i + 3])
            i += 1
        return path

    def contains_point(self, x, y, epsilon):
        p = (x, y)
        min_distance = float(0x7FFFFFFF)
        t = 0.0
        while t < 1.0:
            point = self.path.pointAtPercent(t)
            spline_point = (point.x(), point.y())
            distance = self.distance(p, spline_point)
            if distance < min_distance:
                min_distance = distance
            t += 0.1
        return min_distance <= epsilon

    def boundingRect(self):
        return self.path.boundingRect()

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget,
    ):

        painter.setPen(self.pen)
        painter.strokePath(self.path, painter.pen())

        triangle_source = self.arrow_head_calc(
            self.path.pointAtPercent(0),
            self.points[-1],
        )

        if triangle_source is not None:
            painter.drawPolyline(triangle_source)

        painter.setRenderHint(painter.Antialiasing)
        painter.setRenderHint(painter.SmoothPixmapTransform)
        painter.setRenderHint(painter.TextAntialiasing)

    @staticmethod
    def distance(p0, p1):
        a = p1[0] - p0[0]
        b = p1[1] - p0[1]
        return sqrt(a * a + b * b)

    def arrow_head_calc(self, start_point=None, end_point=None):

        if start_point is None:
            start_point = self.points[-2]

        if end_point is None:
            end_point = self.points[-1]

        dx, dy = start_point.x() - end_point.x(), start_point.y() - end_point.y()

        length = sqrt(dx**2 + dy**2)
        normalized_x, normalized_y = dx / length, dy / length

        perpendicular_x = -normalized_y
        perpendicular_y = normalized_x

        _arrow_height = _arrow_width = 5

        left_x = (
            end_point.x()
            + _arrow_height * normalized_x
            + _arrow_width * perpendicular_x
        )
        left_y = (
            end_point.y()
            + _arrow_height * normalized_y
            + _arrow_width * perpendicular_y
        )

        right_x = (
            end_point.x()
            + _arrow_height * normalized_x
            - _arrow_width * perpendicular_x
        )
        right_y = (
            end_point.y()
            + _arrow_height * normalized_y
            - _arrow_width * perpendicular_y
        )

        point2 = QPointF(left_x, left_y)
        point3 = QPointF(right_x, right_y)

        return QPolygonF([point2, end_point, point3])
