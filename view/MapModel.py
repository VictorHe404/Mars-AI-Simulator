# --- Model ---
import os

from PyQt6.QtCore import QObject, pyqtSignal, QPointF, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem


class MapModel(QObject):
    avatar_position_changed = pyqtSignal(QPointF)
    map_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.explored_areas = set()

class MiniMapView(QGraphicsView):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.mini_map_height = 160
        self.mini_map_width = 160
        self.background_item = None  # Initialize background item

        self.setFixedSize(self.mini_map_height, self.mini_map_width)
        self.setStyleSheet("border: 2px solid black;")

        # Load initial mini map background
        self.init_minimap("viewImage/miniMapDemo.png")

    def init_minimap(self, relative_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, relative_path)

        if os.path.exists(image_path):
            mini_map_background = QPixmap(image_path)
            mini_map_background = mini_map_background.scaled(
                self.mini_map_height - 5, self.mini_map_width - 5,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.background_item = QGraphicsPixmapItem(mini_map_background)
            self.scene.addItem(self.background_item)
        else:
            print(f"[ERROR] Mini map image not found at: {image_path}")

    # Update mini map function
    def update_minimap(self, mini_map_image_path):
        # Resolve absolute path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(mini_map_image_path):
            image_path = os.path.join(base_dir, mini_map_image_path)
        else:
            image_path = mini_map_image_path

        if os.path.exists(image_path):
            # Remove the old background item if it exists
            if self.background_item:
                self.scene.removeItem(self.background_item)

            mini_map_background = QPixmap(image_path)
            mini_map_background = mini_map_background.scaled(
                self.mini_map_height - 5, self.mini_map_width - 5,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.background_item = QGraphicsPixmapItem(mini_map_background)
            self.scene.addItem(self.background_item)
        else:
            print(f"[ERROR] Mini map image not found at: {image_path}")

#Main Map
class MainMapView(QGraphicsView):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.main_map_width = 600
        self.main_map_height = 600
        self.background_item = None  # Initialize the background item

        self.setFixedSize(self.main_map_width, self.main_map_height)
        self.setStyleSheet("border: 2px solid black;")

        # Load the initial main map background
        self.init_mainmap("viewImage/mainMapDemo.png")

    def init_mainmap(self, relative_path):
        """
        Load and display the background image for the main map.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, relative_path)

        if os.path.exists(image_path):
            main_map_background = QPixmap(image_path)
            main_map_background = main_map_background.scaled(
                self.main_map_width - 5, self.main_map_height - 5,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.background_item = QGraphicsPixmapItem(main_map_background)
            self.scene.addItem(self.background_item)
        else:
            print(f"[ERROR] Main map image not found at: {image_path}")

    def update_mainmap(self, main_map_image_path):
        """
        Update the background image of the main map.
        """
        # Resolve absolute path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(main_map_image_path):
            image_path = os.path.join(base_dir, main_map_image_path)
        else:
            image_path = main_map_image_path

        if os.path.exists(image_path):
            # Remove old background if it exists
            if self.background_item:
                self.scene.removeItem(self.background_item)

            main_map_background = QPixmap(image_path)
            main_map_background = main_map_background.scaled(
                self.main_map_width - 5, self.main_map_height - 5,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.background_item = QGraphicsPixmapItem(main_map_background)
            self.scene.addItem(self.background_item)
        else:
            print(f"[ERROR] Main map image not found at: {image_path}")
