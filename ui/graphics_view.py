import json
import os
from pathlib import Path

from EntityLibPy import EntityLib
from PySide2.QtCore import QPoint, QPointF
from PySide2.QtGui import QMouseEvent, Qt, QWheelEvent
from PySide2.QtWidgets import (
    QGraphicsView,
    QAction,
    QGraphicsProxyWidget,
    QMenu,
    QWidget,
    QGraphicsScene,
)


from PropertyGrapher.ui.node import Node
from PropertyGrapher.ui.arrow import Arrow


class MouseEffectsData:

    is_moving = False
    previous_position = QPointF(0.0, 0.0)
    wheel_position = None
    zoom_factor = 1


class GraphicsView(QGraphicsView):

    _zoom_in_factor = 1.25
    _zoom_out_factor = 1 / _zoom_in_factor
    _scene_margin = 250

    def __init__(
        self, entity_lib: EntityLib, scene: QGraphicsScene, parent: QWidget = None
    ) -> None:
        super().__init__(scene, parent=parent)

        self.entity_lib = entity_lib
        self.mouse_effects_data = MouseEffectsData()
        self.scene = scene

        self.setViewportMargins(10, 10, 10, 10)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

        # Anchors needs to be set to NoAnchor to enable translate and zoom
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)

    @property
    def rawdata_path(self) -> str:
        return str(self.entity_lib.rawdata_path)

    def open_in_property_editor(self, file_path: str) -> None:
        from PropertyEditor.__main__ import main as editor_main
        
        editor_main(self.entity_lib, file_to_open=file_path)

    def open_dependencies_graph(self, file_path: Path) -> None:
        self.parent().main_window.create_graph(
            Path(
                self.rawdata_path,
                file_path,
            )
        )

    def reset_scene(self):
        # As QGraphicsScene.clear() method leads to a crash
        # just create a new scene instead
        self.scene = QGraphicsScene()
        self.mouse_effects_data = MouseEffectsData()
        self.setScene(self.scene)

    def load_file(self, file_path: Path) -> None:
        with open(file_path.as_posix()) as json_file:
            self.load_graph(json.load(json_file))

    def load_graph(self, graph_data: dict) -> None:
        self.reset_scene()
        self.create_graphics_items(graph_data)
        self.resize_scene()

    def resize_scene(self) -> None:
        scene_rect = self.scene.sceneRect()
        self.scene.setSceneRect(
            scene_rect.x() - self._scene_margin,
            scene_rect.y() - self._scene_margin,
            scene_rect.width() + self._scene_margin * 2,
            scene_rect.height() + self._scene_margin * 2,
        )

    def create_graphics_items(self, graph_data: dict) -> None:
        self.create_nodes(graph_data)
        self.create_arrows(graph_data)

    def create_arrows(self, graph_data: dict) -> None:
        for arrow in graph_data.get("edges", []):
            Arrow(arrow, self.scene)

    def create_nodes(self, graph_data: dict) -> None:
        for node in graph_data.get("objects", []):
            Node(node, self.scene)

    def context_menu(self, point: QPoint) -> None:
        menu = QMenu(self)

        proxy = self.scene.itemAt(self.mapToScene(point), self.viewportTransform())
        if isinstance(proxy, QGraphicsProxyWidget):

            open_dependencies_graph = QAction("Open in PropertyGrapher", self)
            open_dependencies_graph.triggered.connect(
                lambda: self.open_dependencies_graph(
                    Path(
                        self.rawdata_path,
                        proxy.widget().file_path,
                    )
                )
            )
            menu.addAction(open_dependencies_graph)

            # Property editor is another tool,
            # optional for the use of the Property grapher
            # Load the module from here to avoid circular imports
            try:
                from PropertyEditor.__main__ import main as editor_main

                open_property_editor = QAction("Open in PropertyEditor", self)
                open_property_editor.triggered.connect(
                    lambda: self.open_in_property_editor(proxy.widget().file_path)
                )
                menu.addAction(open_property_editor)

            except ModuleNotFoundError:
                pass

            open_file = QAction("Open file", self)
            open_file.triggered.connect(
                lambda: os.startfile(
                    Path(
                        self.rawdata_path,
                        proxy.widget().file_path,
                    ).as_posix()
                )
            )
            menu.addAction(open_file)

            menu.exec_(self.mapToGlobal(point))

    def zoom(self, event: QWheelEvent) -> None:
        if event.delta() > 0:
            _zoom_factor = self._zoom_in_factor
        else:
            _zoom_factor = self._zoom_out_factor

        self.scale(_zoom_factor, _zoom_factor)
        self.mouse_effects_data.zoom_factor = (
            self.mouse_effects_data.zoom_factor * _zoom_factor
        )

    def move_after_zoom(
        self, event: QWheelEvent, mouse_scene_position: QPointF
    ) -> None:
        if self.mouse_effects_data.wheel_position is None:
            self.mouse_effects_data.wheel_position = mouse_scene_position

        delta = self.mapToScene(event.pos()) - self.mouse_effects_data.wheel_position
        self.translate(delta.x(), delta.y())

    def wheelEvent(self, event: QWheelEvent) -> None:
        mouse_scene_position = self.mapToScene(event.pos())
        self.zoom(event)
        self.move_after_zoom(event, mouse_scene_position)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() in [Qt.MiddleButton, Qt.LeftButton]:
            self.mouse_effects_data.is_moving = True
            self.mouse_effects_data.previous_position = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.mouse_effects_data.is_moving:
            delta = event.pos() - self.mouse_effects_data.previous_position
            self.mouse_effects_data.previous_position = event.pos()

            self.translate(delta.x(), delta.y())

        self.mouse_effects_data.wheel_position = None

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.mouse_effects_data.is_moving:
            self.mouse_effects_data.is_moving = False
            self.mouse_effects_data.previous_position = None
