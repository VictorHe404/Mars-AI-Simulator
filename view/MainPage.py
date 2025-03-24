import sys
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsPixmapItem, QSlider, QTabWidget, QTextEdit, QLineEdit, QPushButton, QFrame,
    QMessageBox
)
from PyQt6.QtGui import QPixmap, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPointF, QFile
import os

from view.CommandPromptWidget import CommandPromptWidget
from view.MapModel import MapModel, MiniMapView, MainMapView
from view.TaskBarWidget import TaskbarWidget


class MainPage(QMainWindow):
    command_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mars AI - Map Interface")

        # Get screen size
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()

        # Dynamically set width and height based on screen size (50%)
        self.main_page_width = int(rect.width() * 0.5)
        self.main_page_height = int(rect.height() * 0.5)
        self.setGeometry(50, 50, self.main_page_width, self.main_page_height)

        # Model and Controller
        self.model = MapModel()

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Task Bar
        self.taskbar = TaskbarWidget(self)
        main_layout.addWidget(self.taskbar)

        # Map Layout
        map_layout = QHBoxLayout()

        # Mini map + Property widget on left
        mini_map_container = QVBoxLayout()
        self.mini_map = MiniMapView(self.model)

        # Property widget (read-only text field)
        self.property_widget = QTextEdit()
        self.property_widget.setReadOnly(True)
        self.property_widget.setFixedWidth(self.mini_map.width())
        self.property_widget.setFixedHeight(200)
        self.property_widget.setPlaceholderText("Properties will be displayed here...")

        mini_map_container.addWidget(self.mini_map)
        mini_map_container.addWidget(self.property_widget)

        # Main map on the right
        self.main_map = MainMapView(self.model)

        map_layout.addLayout(mini_map_container)
        map_layout.addWidget(self.main_map)

        # Command Prompt
        self.command_prompt = CommandPromptWidget(self, height=int(self.main_page_height / 3))
        self.command_prompt.command_signal.connect(self.process_command)

        # Assemble the main layout
        main_layout.addLayout(map_layout)
        main_layout.addWidget(self.command_prompt)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Timer to update image every 100ms (10 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(100)
        self.pic_counter = float('inf')
        self.update_image()

    def process_command(self, command):
        """Emit the command to Visualizer."""
        self.command_prompt.display_output(command)
        self.command_signal.emit(command)

    def display_output(self, message):
        """Display output in the command prompt's activity log."""
        self.command_prompt.display_output(message)

    def update_image(self):
        """Update the map image."""
        cache_path = os.path.join(os.getcwd(), 'cache_directory')
        pic_path = os.path.join(cache_path, f'elevation_map_{self.pic_counter}.png')
        if os.path.exists(pic_path):
            self.main_map.update_mainmap(pic_path)
            self.pic_counter += 1
        else:
            self.pic_counter = float('inf')

    def update_minimap(self, mini_map_image_path):
        pic_path = os.path.join("viewImage", mini_map_image_path)
        print(pic_path)
        self.mini_map.update_minimap(pic_path)

    def update_mainmap(self, main_map_image_path):
        self.main_map.update_mainmap(main_map_image_path)

    def start_visualizer(self):
        self.pic_counter = 0

    def display_properties(self, text: str):
        """Display text in the property widget below the mini map."""
        self.property_widget.setPlainText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec())
