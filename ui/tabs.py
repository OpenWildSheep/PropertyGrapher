from pathlib import Path
from typing import Optional

from EntityLibPy import EntityLib
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QGraphicsScene,
    QMainWindow,
)

from PropertyGrapher.grapher.graph import create_graph
from PropertyGrapher.ui.graphics_view import GraphicsView


class ViewerTab(QWidget):
    def __init__(self, main_window: QMainWindow, parent: QWidget = None):
        """Initialize."""

        super().__init__(parent=parent)

        self.view = None
        self._current_file = None
        self._label = None
        self.main_window = main_window

        self.create_ui()

    @property
    def entity_lib(self) -> EntityLib:
        return self.main_window.entity_lib

    @property
    def label(self) -> str:
        """Get tab label."""
        return self._label

    @label.setter
    def label(self, value):
        """Set tab label."""
        self._label = value

        if self.parent():
            tabs_widget = self.parent().parent()
            tabs_widget.setTabText(
                tabs_widget.currentIndex(),
                self.label,
            )

    @property
    def current_prop(self):
        return self._current_file

    @current_prop.setter
    def current_prop(self, file_path: Path):
        self._current_file = file_path
        self.label = file_path.name
        self.main_window.reload_button.setEnabled(True)

    def create_ui(self):
        main_layout = QVBoxLayout(self)
        self.view = GraphicsView(self.entity_lib, QGraphicsScene())
        main_layout.addWidget(self.view)

    def load_graph(self, file_path: Path) -> None:
        graph_data = create_graph(
            self.entity_lib,
            file_path,
            self.main_window.output_path,
            view=False,
            generate_files=False,
        )

        if not graph_data.get("objects"):
            print(graph_data)
            raise Exception(f"No property found in {file_path.as_posix()}")
        self.current_prop = Path(graph_data["objects"][0]["tooltip"])
        self.view.load_graph(graph_data)

    def reload_graph(self) -> None:
        self.load_graph(self.current_prop)


class ViewerTabs(QTabWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.clicked_index = None

    def current_changed(self, index: int) -> None:
        self.clicked_index = index

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MidButton:
            self.removeTab(self.clicked_index)
        super(ViewerTabs, self).mouseReleaseEvent(event)

    def tab_clicked(self, index):
        self.clicked_index = index

    def clear(self) -> None:
        for i in reversed(range(self.count())):
            self.removeTab(i)
