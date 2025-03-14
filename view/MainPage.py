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

# --- Main Application ---
class MainPage(QMainWindow):
    command_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mars AI - Map Interface")
        self.main_page_height = 800
        self.main_page_width = 1200

        self.setGeometry(100, 100, self.main_page_width, self.main_page_height)

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
        self.mini_map = MiniMapView(self.model)
        self.main_map = MainMapView(self.model)

        map_layout.addWidget(self.mini_map)
        map_layout.addWidget(self.main_map)

        # Command Prompt
        self.command_prompt = CommandPromptWidget(self, height=int(self.main_page_height / 3))
        self.command_prompt.command_signal.connect(self.process_command)

        # Assemble the main layout
        main_layout.addLayout(map_layout)
        main_layout.addWidget(self.command_prompt)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def process_command(self, command):
        """Emit the command to Visualizer."""
        self.command_signal.emit(command)

    def display_output(self, message):
        """Display output in the command prompt's activity log."""
        self.command_prompt.display_output(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec())
