from typing import Tuple, List

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGraphicsScene, QWidget, QVBoxLayout, QLabel


class Node(QWidget):
    def __init__(
        self, node_data: dict, scene: QGraphicsScene, parent: QWidget = None
    ) -> None:

        super().__init__(parent=parent)

        self.id = node_data["_gvid"]
        self.name = node_data["name"]
        self.file_path = node_data["tooltip"]
        self.x, self.y, self.width, self.height = self.get_pos_and_size(node_data)

        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)

        self.label = QLabel(node_data["label"], self)
        self.label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addWidget(self.label)

        self.set_position()
        self.set_color(node_data)
        self.setToolTip(self.file_path)

        proxy = scene.addWidget(self)
        proxy.setZValue(1000)
        self.setFixedSize(int(self.width), int(self.height))

    def set_color(self, node_data: dict) -> None:
        for item in node_data["_draw_"]:
            color = item.get("color")
            if color and color != "#000000":
                self.setStyleSheet(f"background-color: {color};")

    @staticmethod
    def get_pos_and_size(node_data: dict) -> Tuple[float, float, float, float]:

        for item in node_data["_draw_"]:
            points = item.get("points")
            if points:
                x_values = [v[0] for v in points]
                y_values = [v[1] for v in points]

                x = min(x_values)
                y = min(y_values)
                width = max(x_values) - x
                height = max(y_values) - y
                return x, y, width, height

        raise Exception("Node has no points, this should not happen")

    def set_position(self) -> None:
        self.move(int(self.x), int(self.y))

    def get_size(self, points: List[List[float]]) -> Tuple[float, float]:
        return self.get_width(points), self.get_height(points)

    @staticmethod
    def get_width(points: List[List[float]]) -> float:
        return max(p[0] for p in points) - min([p[0] for p in points])

    @staticmethod
    def get_height(points: List[List[float]]) -> float:
        return max(p[1] for p in points) - min([p[1] for p in points])
