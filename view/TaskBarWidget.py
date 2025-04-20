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
    report_signal = pyqtSignal()
    set_animation_speed_signal = pyqtSignal(float)
    set_task_signal = pyqtSignal(int, int, int, int)
    run_task_signal = pyqtSignal()
    set_database_signal = pyqtSignal(str)
    set_max_frame_signal = pyqtSignal(int)

    #Avatar Signals
    list_avatar_signal = pyqtSignal()
    create_avatar_signal = pyqtSignal(str)
    set_avatar_signal = pyqtSignal(str)
    info_avatar_signal = pyqtSignal(str)
    set_brain_signal = pyqtSignal(str)
    list_brain_signal = pyqtSignal()

    """Taskbar Widget"""
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
        """Create Avatar button"""
        self.avatar_button = QPushButton("Avatar")
        self.avatar_button.setFlat(True)
        self.avatar_button.setFixedHeight(40)
        self.avatar_button.setStyleSheet(self.button_style())

        # Dropdown menu
        self.avatar_menu = QMenu(self)
        list_avatar_action = QAction("List Avatar", self)
        create_avatar_action = QAction("Create Avatar", self)
        set_avatar_action = QAction("Set Avatar", self)
        info_avatar_action = QAction("Info Avatar", self)
        list_brain_action = QAction("List Brain", self)
        set_brain_action = QAction("Set Brain", self)

        self.avatar_menu.addAction(list_avatar_action)
        self.avatar_menu.addAction(create_avatar_action)
        self.avatar_menu.addAction(set_avatar_action)
        self.avatar_menu.addAction(info_avatar_action)
        self.avatar_menu.addAction(list_brain_action)
        self.avatar_menu.addAction(set_brain_action)

        # Connect actions
        list_avatar_action.triggered.connect(lambda: self.list_avatar_signal.emit())
        create_avatar_action.triggered.connect(self.__create_avatar_button__)
        set_avatar_action.triggered.connect(self.__set_avatar_button__)
        list_brain_action.triggered.connect(lambda: self.list_brain_signal.emit())
        set_brain_action.triggered.connect(self.__set_brain_button__)
        info_avatar_action.triggered.connect(self.__info_avatar_button__)

        self.avatar_button.clicked.connect(self.show_avatar_menu)
        self.taskbar_layout.addWidget(self.avatar_button)

    def create_instruction_button(self):
        """Create Instruction.txt button"""
        self.instruction_button = QPushButton("Instruction")
        self.instruction_button.setFlat(True)
        self.instruction_button.setFixedHeight(40)
        self.instruction_button.setStyleSheet(self.button_style())
        self.instruction_button.clicked.connect(self.show_instructions)

        self.taskbar_layout.addWidget(self.instruction_button)

    def create_github_button(self):
        """Create GitHub button"""
        self.github_button = QPushButton("GitHub Link")
        self.github_button.setFlat(True)
        self.github_button.setFixedHeight(40)
        self.github_button.setStyleSheet(self.button_style())
        self.github_button.clicked.connect(self.open_github_link)

        self.taskbar_layout.addWidget(self.github_button)

    def create_setting_button(self):
        """Create Setting button with dropdown menu"""
        self.setting_button = QPushButton("Setting")
        self.setting_button.setFlat(True)
        self.setting_button.setFixedHeight(40)
        self.setting_button.setStyleSheet(self.button_style())

        # Dropdown menu
        self.setting_menu = QMenu(self)
        list_map_action = QAction("List Map", self)
        set_map_action = QAction("Set Map", self)
        report_action = QAction("Report", self)
        set_animation_action = QAction("Set Animation", self)
        set_task_action = QAction("Set Task", self)
        run_task_action = QAction("Run", self)
        set_database_action = QAction("Set Database Mode", self)
        set_max_frame_action = QAction("Set Max Frame Size", self)

        self.setting_menu.addAction(list_map_action)
        self.setting_menu.addAction(set_map_action)
        self.setting_menu.addAction(report_action)
        self.setting_menu.addAction(set_animation_action)
        self.setting_menu.addAction(set_task_action)
        self.setting_menu.addAction(run_task_action)
        self.setting_menu.addAction(set_database_action)
        self.setting_menu.addAction(set_max_frame_action)

        list_map_action.triggered.connect(lambda: self.list_map_signal.emit())
        set_map_action.triggered.connect(self.__set_map_button__)
        report_action.triggered.connect(self.__report_button__)
        set_animation_action.triggered.connect(self.__set_animation_button__)
        set_task_action.triggered.connect(self.__set_task_button__)
        run_task_action.triggered.connect(lambda: self.run_task_signal.emit())
        set_database_action.triggered.connect(self.__set_database_button__)
        set_max_frame_action.triggered.connect(self.__set_max_frame_button__)

        self.setting_button.clicked.connect(self.show_setting_menu)
        self.taskbar_layout.addWidget(self.setting_button)

    def show_avatar_menu(self):
        """Display dropdown menu"""
        self.avatar_menu.setFixedWidth(self.avatar_button.width())
        self.avatar_menu.exec(self.avatar_button.mapToGlobal(self.avatar_button.rect().bottomLeft()))

    def show_setting_menu(self):
        """Display dropdown menu"""
        self.setting_menu.setFixedWidth(self.setting_button.width())
        self.setting_menu.exec(self.setting_button.mapToGlobal(self.setting_button.rect().bottomLeft()))

    def list_avatar(self, avatar_list):
        QMessageBox.information(self, avatar_list, avatar_list)

    def __create_avatar_button__(self):
        avatar_name, ok_pressed = QInputDialog.getText(
            self,
            "Create Avatar",
            "Enter Avatar name:"
        )
        if ok_pressed:
            self.create_avatar_signal.emit(avatar_name)

    def create_avatar(self, avatar_name):
        QMessageBox.information(self, "Create Avatar", avatar_name)

    def __set_avatar_button__(self):
        avatar_name, ok_pressed = QInputDialog.getText(
            self,
            "Set Avatar Name",
            "Enter Avatar name:"
        )
        if ok_pressed:
            self.set_avatar_signal.emit(avatar_name)

    def set_avatar(self, avatar_name):
        QMessageBox.information(self, "Set Avatar", avatar_name)

    def __info_avatar_button__(self):
        avatar_name, ok_pressed = QInputDialog.getText(
            self,
            "Get Avatar Info",
            "Enter Avatar name:"
        )
        if ok_pressed:
            self.info_avatar_signal.emit(avatar_name)

    def info_avatar(self, avatar_info):
        QMessageBox.information(self, "Info Avatar", avatar_info)

    def list_brain(self, brain_list):
        QMessageBox.information(self, "List Brain", brain_list)

    def __set_brain_button__(self):
        brain_name, ok_pressed = QInputDialog.getText(
            self,
            "Set Brain Name",
            "Enter Brain name:"
        )
        if ok_pressed:
            self.set_brain_signal.emit(brain_name)

    def set_brain(self, brain_name):
        QMessageBox.information(self,"Set Brain", brain_name)

    # Setting
    def list_map(self, map_list):
        QMessageBox.information(self, map_list, map_list)

    def __set_map_button__(self):
        map_name, ok_pressed = QInputDialog.getText(
            self,
            "Set Map Name",
            "Enter map name:"
        )
        if ok_pressed:
            self.set_map_signal.emit(map_name)

    def set_map(self, map_name):
        QMessageBox.information(self, "Set Map", map_name)

    def __report_button__(self):
        self.report_signal.emit()

    def show_report(self, path):
        try:
            with open(path, 'r', encoding='iso-8859-1') as file:
                content = file.read()
        except Exception as e:
            content = f"Could not load the report:\n{e}"

        # Create a new window
        window = QWidget()
        window.setWindowTitle("Report")
        window.resize(600, 400)

        layout = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(content)

        layout.addWidget(text_edit)

        window.setLayout(layout)
        window.show()
        self.report_window = window

    def __set_animation_button__(self):
        animation_speed, ok_pressed = QInputDialog.getText(
            self,
            "Set Animation Speed",
            "Enter speed (Float):"
        )
        if ok_pressed:
            try:
                animation_speed = float(animation_speed)
                self.set_animation_speed_signal.emit(animation_speed)
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please enter a valid floating-point number for the speed."
                )

    def set_animation_speed(self, animation_speed):
        QMessageBox.information(self, "Set Animation Speed", animation_speed)

    def __set_task_button__(self):
        task_input, ok_pressed = QInputDialog.getText(
            self,
            "Set Task",
            "Enter start and destination coordinates (sX sY dX dY):"
        )

        if ok_pressed:
            try:
                coords = task_input.strip().split()
                if len(coords) == 4:
                    sX, sY, dX, dY = map(int, coords)
                    self.set_task_signal.emit(sX, sY, dX, dY)
                else:
                    raise ValueError("Please enter exactly four space-separated numbers.")
            except ValueError as e:
                QMessageBox.warning(self, "Input Error", f"Please enter four integer numbers separated by spaces.")

    def set_task(self, task_output):
        QMessageBox.information(self, "Set Task", task_output)

    def run_task(self, run_output):
        QMessageBox.information(self, "Run Task", run_output)

    def __set_database_button__(self):
        database_mode, ok_pressed = QInputDialog.getText(
            self,
            "Enable/disable database mode",
            "Enter True or False to enable/disable database mode:"
        )
        if ok_pressed:
            self.set_database_signal.emit(database_mode)

    def set_database_mode(self, output):
        QMessageBox.information(self, "Set Database Mode", output)

    def __set_max_frame_button__(self):
        max_frame, ok_pressed = QInputDialog.getText(
            self,
            "Set Max Frame Size",
            "Enter Size (Integer from 100 to 400):"
        )
        if ok_pressed:
            try:
                max_frame = int(max_frame)
                self.set_max_frame_signal.emit(max_frame)
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please enter a valid int number for the max frame size."
                )

    def set_max_frame_size(self, output):
        QMessageBox.information(self, "Set Max Frame Size", output)

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
