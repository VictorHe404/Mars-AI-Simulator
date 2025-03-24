import os
import webbrowser
from PyQt6.QtWidgets import (
    QHBoxLayout, QMessageBox, QWidget, QPushButton, QMenu, QVBoxLayout, QTextEdit
)
from PyQt6.QtGui import QAction


class TaskbarWidget(QWidget):
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
        set_avatar_action = QAction("Set Avatar", self)  # ✅ New action

        self.avatar_menu.addAction(list_avatar_action)
        self.avatar_menu.addAction(create_avatar_action)
        self.avatar_menu.addAction(set_avatar_action)  # ✅ Add to menu

        # Connect actions
        list_avatar_action.triggered.connect(self.list_avatar)
        create_avatar_action.triggered.connect(self.create_avatar)
        set_avatar_action.triggered.connect(self.set_avatar)  # ✅ Connect action

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
        show_map_action = QAction("Show Map", self)
        self.setting_menu.addAction(show_map_action)

        show_map_action.triggered.connect(self.show_map_window)

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

    def create_avatar(self):
        QMessageBox.information(self, "Create Avatar", "Create Avatar")

    def list_avatar(self):
        QMessageBox.information(self, "List Avatar", "List Avatar")

    def set_avatar(self):
        QMessageBox.information(self, "Set Avatar", "Set Avatar feature is under development.")

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

    def open_github_link(self):
        try:
            webbrowser.open("https://github.com/VictorHe404/COMP361")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open GitHub link: {e}")

    def show_map_window(self):
        QMessageBox.information(self, "Map", "Map feature is under development!")

    def open_settings(self):
        print("[INFO] Opening settings dialog")
