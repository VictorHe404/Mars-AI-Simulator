import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsPixmapItem, QSlider, QTabWidget, QTextEdit, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtGui import QPixmap, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPointF
import os


# --- Model ---
class MapModel(QObject):
    avatar_position_changed = pyqtSignal(QPointF)
    map_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.avatar_position = QPointF(400, 300)
        self.explored_areas = set()

    def move_avatar(self, dx, dy):
        self.avatar_position += QPointF(dx, dy)
        self.explored_areas.add((int(self.avatar_position.x()), int(self.avatar_position.y())))
        self.avatar_position_changed.emit(self.avatar_position)
        self.map_updated.emit()


# --- View ---
class MiniMapView(QGraphicsView):
    def __init__(self, model: MapModel):
        super().__init__()
        self.model = model
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.setFixedSize(160, 160)
        self.setStyleSheet("border: 2px solid black;")

        # Mini map background
        mini_map_background = QPixmap("view/viewImage/miniMapBackground.png")
        self.background_item = QGraphicsPixmapItem(mini_map_background)
        self.scene.addItem(self.background_item)

        # Avatar marker
        self.avatar_marker = QGraphicsEllipseItem(-5, -5, 10, 10)
        self.avatar_marker.setBrush(QBrush(QColor(255, 0, 0)))
        self.scene.addItem(self.avatar_marker)

        self.model.avatar_position_changed.connect(self.update_avatar_position)

    def update_avatar_position(self, position: QPointF):
        self.avatar_marker.setPos(position.x() / 10, position.y() / 10)  # Scale to fit mini-map


class MainMapView(QGraphicsView):
    def __init__(self, model: MapModel):
        super().__init__()
        self.model = model
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        background_path = os.path.join(os.path.dirname(__file__), "view/viewImage/welcomeBackground.png")
        if os.path.exists(background_path):
            background_pixmap = QPixmap(background_path)
            self.background_item = QGraphicsPixmapItem(background_pixmap)
            self.scene.addItem(self.background_item)

        # Avatar setup
        self.avatar = QGraphicsEllipseItem(-15, -15, 30, 30)
        self.avatar.setBrush(QBrush(QColor(255, 255, 255)))
        self.avatar.setPen(QPen(QColor(0, 0, 0)))
        self.scene.addItem(self.avatar)

        # Detectable area
        self.detectable_area = QGraphicsEllipseItem(-100, -100, 200, 200)
        self.detectable_area.setBrush(QBrush(QColor(200, 200, 200, 50)))
        self.detectable_area.setPen(QPen(Qt.PenStyle.NoPen))
        self.scene.addItem(self.detectable_area)

        self.model.avatar_position_changed.connect(self.update_avatar_position)

    def update_avatar_position(self, position: QPointF):
        self.avatar.setPos(position)
        self.detectable_area.setPos(position)


# --- Controller ---
class MapController(QObject):
    def __init__(self, model: MapModel):
        super().__init__()
        self.model = model
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_avatar_step)
        self.target_position = None

    def move_avatar_to(self, x, y):
        self.target_position = QPointF(x, y)
        self.timer.start(50)

    def move_avatar_step(self):
        if not self.target_position:
            self.timer.stop()
            return

        current = self.model.avatar_position
        dx = (self.target_position.x() - current.x()) / 10
        dy = (self.target_position.y() - current.y()) / 10

        if abs(dx) < 1 and abs(dy) < 1:
            self.model.move_avatar(dx, dy)
            self.timer.stop()
        else:
            self.model.move_avatar(dx, dy)


# --- Main Application ---
class MapInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mars AI - Map Interface")
        self.setGeometry(100, 100, 1200, 800)

        # Model and Controller
        self.model = MapModel()
        self.controller = MapController(self.model)

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Navigation bar
        self.tab_bar = QTabWidget()
        self.tab_bar.addTab(QWidget(), "Avatar")
        self.tab_bar.addTab(QWidget(), "Instruction")
        self.tab_bar.addTab(QWidget(), "GitHub Link")
        self.tab_bar.addTab(QWidget(), "Setting")
        self.tab_bar.setStyleSheet("QTabBar::tab { color: black; font-size: 14px; padding: 6px; }")
        main_layout.addWidget(self.tab_bar)

        # Map layout
        map_layout = QHBoxLayout()
        self.mini_map = MiniMapView(self.model)
        self.main_map = MainMapView(self.model)

        # Zoom slider
        zoom_slider = QSlider(Qt.Orientation.Vertical)
        zoom_slider.setMinimum(1)
        zoom_slider.setMaximum(100)
        zoom_slider.setValue(50)
        zoom_slider.valueChanged.connect(lambda val: self.main_map.scale(val / 50, val / 50))

        map_layout.addWidget(self.mini_map)
        map_layout.addWidget(self.main_map)
        map_layout.addWidget(zoom_slider)

        # Command terminal
        terminal_layout = QHBoxLayout()
        command_input = QLineEdit()
        execute_button = QPushButton("Execute")
        activity_log = QTextEdit()
        activity_log.setReadOnly(True)

        execute_button.clicked.connect(lambda: self.execute_command(command_input.text(), activity_log))

        terminal_layout.addWidget(command_input)
        terminal_layout.addWidget(execute_button)
        terminal_layout.addWidget(activity_log)

        # Add all layouts
        main_layout.addLayout(map_layout)
        main_layout.addLayout(terminal_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def execute_command(self, command, log_widget):
        log_widget.append(f"$ {command}")
        parts = command.split()
        if parts[0] == "move" and len(parts) == 3:
            x, y = int(parts[1]), int(parts[2])
            self.controller.move_avatar_to(x, y)
            log_widget.append(f"Moving avatar to ({x}, {y})...")
        else:
            log_widget.append("Unknown command.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapInterface()
    window.show()
    sys.exit(app.exec())
