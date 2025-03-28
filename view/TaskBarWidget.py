import os
import webbrowser
from logging.config import listen

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout, QMessageBox, QWidget, QPushButton, QMenu, QVBoxLayout, QTextEdit, QInputDialog
)
from PyQt6.QtGui import QAction


class TaskbarWidget(QWidget):
    #Setting Signals
    list_map_signal = pyqtSignal()
    set_map_signal = pyqtSignal(str)

    #Avatar Signals
    list_avatar_signal = pyqtSignal()
    create_avatar_signal = pyqtSignal(str)
    set_avatar_signal = pyqtSignal(str)
    set_brain_signal = pyqtSignal(str)

    """Custom Taskbar Widget like Chrome with dropdown menus on Avatar and Setting."""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Main layout
        self.taskbar_layout = QHBoxLayout()
        self.taskbar_layout.setSpacing(0)

        # Add buttons
        self.create_setting_button()
        self.create_avatar_button()
        self.create_instruction_button()
        self.create_github_button()

        self.setLayout(self.taskbar_layout)

    def button_style(self):
        return """
            QPushButton { padding: 10px; border: 2px solid #555; border-radius: 5px;}
            QPushButton:hover { background-color: #ddd; }
        """

    def create_avatar_button(self):
        """Create Avatar button with dropdown menu."""
        self.avatar_button = QPushButton("Avatar")
        self.avatar_button.setFlat(True)
        self.avatar_button.setFixedHeight(40)
        self.avatar_button.setStyleSheet(self.button_style())

        # Dropdown menu
        self.avatar_menu = QMenu(self)
        list_avatar_action = QAction("List Avatar", self)
        create_avatar_action = QAction("Create Avatar", self)
        set_avatar_action = QAction("Set Avatar", self)
        set_brain_action = QAction("Set Brain", self)

        self.avatar_menu.addAction(list_avatar_action)
        self.avatar_menu.addAction(create_avatar_action)
        self.avatar_menu.addAction(set_avatar_action)
        self.avatar_menu.addAction(set_brain_action)

        # Connect actions
        list_avatar_action.triggered.connect(self.__list_avatar_button__)
        create_avatar_action.triggered.connect(self.__create_avatar_button__)
        set_avatar_action.triggered.connect(self.__set_avatar_button__)
        set_brain_action.triggered.connect(self.__set_brain_button__)

        self.avatar_button.clicked.connect(self.show_avatar_menu)
        self.taskbar_layout.addWidget(self.avatar_button)

    def create_instruction_button(self):
        """Create Instruction.txt button."""
        self.instruction_button = QPushButton("Instruction")
        self.instruction_button.setFlat(True)
        self.instruction_button.setFixedHeight(40)
        self.instruction_button.setStyleSheet(self.button_style())
        self.instruction_button.clicked.connect(self.show_instructions)

        self.taskbar_layout.addWidget(self.instruction_button)

    def create_github_button(self):
        """Create GitHub button."""
        self.github_button = QPushButton("GitHub Link")
        self.github_button.setFlat(True)
        self.github_button.setFixedHeight(40)
        self.github_button.setStyleSheet(self.button_style())
        self.github_button.clicked.connect(self.open_github_link)

        self.taskbar_layout.addWidget(self.github_button)

    def create_setting_button(self):
        """Create Setting button with dropdown menu."""
        self.setting_button = QPushButton("Setting")
        self.setting_button.setFlat(True)
        self.setting_button.setFixedHeight(40)
        self.setting_button.setStyleSheet(self.button_style())

        # Dropdown menu
        self.setting_menu = QMenu(self)
        list_map_action = QAction("List Map", self)
        set_map_action = QAction("Set Map", self)
        self.setting_menu.addAction(list_map_action)
        self.setting_menu.addAction(set_map_action)

        list_map_action.triggered.connect(self.__list_map_button__)
        set_map_action.triggered.connect(self.__set_map_button__)

        self.setting_button.clicked.connect(self.show_setting_menu)
        self.taskbar_layout.addWidget(self.setting_button)

    def show_avatar_menu(self):
        """Display dropdown menu under Avatar button."""
        self.avatar_menu.setFixedWidth(self.avatar_button.width())
        self.avatar_menu.exec(self.avatar_button.mapToGlobal(self.avatar_button.rect().bottomLeft()))

    def show_setting_menu(self):
        """Display dropdown menu under Setting button."""
        self.setting_menu.setFixedWidth(self.setting_button.width())
        self.setting_menu.exec(self.setting_button.mapToGlobal(self.setting_button.rect().bottomLeft()))

    # Avatar Buttons
    def __list_avatar_button__(self):
        self.list_avatar_signal.emit()

    def list_avatar(self, avatar_list):
        QMessageBox.information(self, avatar_list, avatar_list)

    def __create_avatar_button__(self):
        avatar_name, ok_pressed = QInputDialog.getText(
            self,
            "Create Avatar",
            "Enter Avatar name:"
        )
        self.create_avatar_signal.emit(avatar_name)

    def create_avatar(self, avatar_name):
        QMessageBox.information(self, "Create Avatar Success", "Avatar " + avatar_name + " is created.")

    def __set_avatar_button__(self):
        avatar_name, ok_pressed = QInputDialog.getText(
            self,
            "Set Avatar Name",
            "Enter Brain name:"
        )
        self.set_avatar_signal.emit(avatar_name)

    def set_avatar(self, avatar_name):
        QMessageBox.information(self, "Set Avatar Success", "Avatar " + avatar_name + " is set.")

    def __set_brain_button__(self):
        brain_name, ok_pressed = QInputDialog.getText(
            self,
            "Set Brain Name",
            "Enter Brain name:"
        )
        self.set_brain_signal.emit(brain_name)

    def set_brain(self, brain_name):
        QMessageBox.information(self,"Set Brain Success", "Brain " + brain_name + " is set.")

    # Setting
    def __list_map_button__(self):
        self.list_map_signal.emit()

    def list_map(self, map_list):
        QMessageBox.information(self, map_list, map_list)

    def __set_map_button__(self):
        map_name, ok_pressed = QInputDialog.getText(
            self,
            "Set Map Name",
            "Enter map name:"
        )
        self.set_map_signal.emit(map_name)

    def set_map(self, name):
        QMessageBox.information(self, "Set Map Success", "Map " + name + " is set.")

    #Instruction
    def show_instructions(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_path, 'Instruction.txt')

        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            content = f"Could not load instructions:\n{e}"

        # Create a new window
        window = QWidget()
        window.setWindowTitle("Instruction")
        window.resize(600, 400)

        layout = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(content)

        layout.addWidget(text_edit)

        window.setLayout(layout)
        window.show()
        self.instruction_window = window

    #Github Link
    def open_github_link(self):
        try:
            webbrowser.open("https://github.com/VictorHe404/COMP361")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open GitHub link: {e}")

    def open_settings(self):
        print("[INFO] Opening settings dialog")
