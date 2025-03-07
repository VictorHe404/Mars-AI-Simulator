import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsPixmapItem, QSlider, QTabWidget, QTextEdit, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtGui import QPixmap, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPointF, QFile
import os

# --- Model ---
class MapModel(QObject):
    avatar_position_changed = pyqtSignal(QPointF)
    map_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.explored_areas = set()


# --- View ---
class MiniMapView(QGraphicsView):
    def __init__(self, model: MapModel):
        super().__init__()
        self.model = model
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.mini_map_height = 160
        self.mini_map_width = 160

        self.setFixedSize(self.mini_map_height, self.mini_map_width)
        self.setStyleSheet("border: 2px solid black;")

        # Mini map background
        image_path = os.path.abspath("viewImage/miniMapDemo.png")
        mini_map_background = QPixmap(image_path)
        mini_map_background = mini_map_background.scaled(self.mini_map_height-5, self.mini_map_width-5,
                                                         Qt.AspectRatioMode.KeepAspectRatio,
                                                         Qt.TransformationMode.SmoothTransformation)
        self.background_item = QGraphicsPixmapItem(mini_map_background)
        self.scene.addItem(self.background_item)

    def update_minimap(self, mini_map_image):
        """

        """
        mini_map_background = QPixmap(mini_map_image)
        self.background_item = QGraphicsPixmapItem(mini_map_background)
        self.scene.addItem(self.background_item)

#Main Map
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

# --- Controller ---
class MapController(QObject):
    def __init__(self, model: MapModel):
        super().__init__()
        self.model = model


# --- Main Application ---
class MainPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mars AI - Map Interface")
        self.main_page_height = 800
        self.main_page_width = 1200

        self.setGeometry(100, 100, self.main_page_width, self.main_page_height)

        # Model and Controller
        self.model = MapModel()
        self.controller = MapController(self.model)

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()


        # Navigation Taskbar (Replaces QTabWidget)
        taskbar_layout = QHBoxLayout()
        taskbar_layout.setSpacing(0)  # Remove spacing between buttons

        # Taskbar buttons
        taskbar_buttons = [
            QPushButton("Avatar"),
            QPushButton("Instruction"),
            QPushButton("GitHub Link"),
            QPushButton("Setting")
        ]

        # Configure each button
        for button in taskbar_buttons:
            button.setFlat(True)  # Removes the raised button effect
            button.setFixedHeight(40)  # Uniform height
            button.setStyleSheet("QPushButton { padding: 10px; border: none; }"
                                 "QPushButton:hover { background-color: #ddd; }")  # Simple hover effect
            taskbar_layout.addWidget(button)

        # Add taskbar to main layout
        main_layout.addLayout(taskbar_layout)

        # Map layout
        map_layout = QHBoxLayout()
        self.mini_map = MiniMapView(self.model)
        self.main_map = MainMapView(self.model)

        map_layout.addWidget(self.mini_map)
        map_layout.addWidget(self.main_map)

        # Command terminal
        terminal_layout = QVBoxLayout()  # Vertical layout for proper alignment

        activity_log = QTextEdit()
        activity_log.setReadOnly(True)
        activity_log.setFixedHeight(int(self.main_page_height/3))
        activity_log.setStyleSheet("background-color: black; color: white; font-family: Consolas; font-size: 14px;")

        command_input = QLineEdit()
        command_input.setStyleSheet("background-color: black; color: white; font-family: Consolas; font-size: 14px;")
        command_input.setPlaceholderText("Type a command...")

        # Execute command function
        def execute_command():
            command = command_input.text().strip()
            if command:
                activity_log.append(f"C:\\> {command}")  # Simulate Windows CMD prompt
                #process_command(command)  # Function to handle command execution
                command_input.clear()  # Clear input after execution

        # Handle key press (Enter to execute command)
        command_input.returnPressed.connect(execute_command)

        # # Function to simulate command execution
        # def process_command(command):
        #     if command.lower() == "clear":
        #         activity_log.clear()  # Clear the output log
        #     elif command.lower() == "exit":
        #         activity_log.append("Exiting session...")
        #     else:
        #         activity_log.append(f"'{command}' is not recognized as an internal or external command.")


        terminal_layout.addWidget(activity_log)
        input_layout = QHBoxLayout()
        input_layout.addWidget(command_input)
        terminal_layout.addLayout(input_layout)

        # Add all layouts
        main_layout.addLayout(map_layout)
        main_layout.addLayout(terminal_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec())
