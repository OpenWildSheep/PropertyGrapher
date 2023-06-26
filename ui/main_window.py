import os

from EntityLibPy import EntityLib
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QStyle,
    QStyleOptionTitleBar,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QFileDialog,
)

from PySide2.QtCore import QCoreApplication, Qt, QDir, QSize
import sys
from pathlib import Path
from typing import Optional
from PropertyGrapher.ui.tabs import ViewerTabs, ViewerTab


class MenuButton(QPushButton):
    """Menu button, mostly for style."""

    def __init__(
        self,
        text: str,
        icon: str = None,
        parent: QWidget = None,
        size: int = 50,
        icon_size: int = 25,
    ):
        """Initialize."""
        super().__init__("", parent=parent)

        self.icon_size = icon_size
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(size, size)
        self.setToolTip(text)
        self.set_icon(icon)

    def set_icon(self, icon):
        icons_path = QDir.searchPaths("grapher_icons")
        icon = f"{icons_path[0]}/{icon}.png"
        self.setIcon(QIcon(icon))
        self.setIconSize(QSize(self.icon_size, self.icon_size))


class GraphViewer(QMainWindow):
    def __init__(self, entity_lib: EntityLib, output_path: Path):
        super().__init__()

        QDir.addSearchPath(
            "grapher_icons",
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                "_sources",
                "icons",
            ),
        )
        self.entity_lib = entity_lib
        self.output_path = output_path
        self._current_file: Optional[Path] = None

        self.create_ui()
        self.set_full_screen()

        self.setWindowIcon(QIcon(f"{QDir.searchPaths('grapher_icons')[0]}/app.png"))
        self.setWindowTitle("Property Grapher")

    def create_ui(self):

        main_frame = QFrame(self)
        main_layout = QHBoxLayout(main_frame)

        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        open_button = MenuButton("Open property as graph", "open_2")
        open_button.clicked.connect(self.open_entity_graph)
        self.reload_button = MenuButton("Reload property's graph", "reload_2")
        self.reload_button.clicked.connect(self.reload_graph)
        self.reload_button.setEnabled(False)

        menu_layout.addWidget(open_button)
        menu_layout.addWidget(self.reload_button)

        main_layout.addLayout(menu_layout)

        self.tabs = ViewerTabs()
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        self.tabs.currentChanged.connect(self.tabs.current_changed)
        main_layout.addWidget(self.tabs)

        self.setCentralWidget(main_frame)

    def get_default_dir(self) -> str:
        current_widget = self.tabs.currentWidget()
        if current_widget:
            return current_widget.current_entity.as_posix()
        else:
            return str(self.entity_lib.rawdata_path)

    def open_entity_graph(self):
        dialog = QFileDialog()

        default_dir = self.get_default_dir()
        dialog.setDirectory(default_dir)
        file_name = dialog.getOpenFileName(
            self,
            "Open property File",
            default_dir,
        )
        file_path = file_name[0]
        if not file_path:
            return

        self.create_graph(Path(file_path))

    def reload_graph(self):
        self.tabs.currentWidget().reload_graph()

    def create_graph(self, file_path: Path) -> None:
        widget = ViewerTab(self)
        widget.load_graph(file_path)
        self.tabs.addTab(widget, widget.label)
        self.tabs.setCurrentWidget(widget)

    def set_full_screen(self):

        title_bar_height = self.style().pixelMetric(
            QStyle.PM_TitleBarHeight, QStyleOptionTitleBar(), self
        )

        geometry = QCoreApplication.instance().desktop().availableGeometry()
        geometry.setY(title_bar_height)
        geometry.setHeight(geometry.height())
        self.setGeometry(geometry)


def create_window(
    entity_lib: EntityLib, output_path: Path, file_path: Optional[Path] = None
) -> GraphViewer:

    app = QApplication.instance()
    existing_pyside2_app = bool(app)
    main_window = None

    if not existing_pyside2_app:
        app = QApplication(sys.argv)
        app.setOrganizationName("WildSheepStudio")
        app.setOrganizationDomain("wildsheepstudio.com")
    else:
        for window in app.topLevelWidgets():
            if isinstance(window, GraphViewer):
                main_window = window
                break
    if not main_window:
        main_window = GraphViewer(entity_lib, output_path)
        main_window.show()

    main_window.raise_()

    if file_path and file_path.suffix == ".entity":
        main_window.create_graph(file_path=file_path)

    if not existing_pyside2_app:
        sys.exit(app.exec_())

    return main_window
