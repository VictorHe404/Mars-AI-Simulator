import sys
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QMessageBox, QVBoxLayout, QWidget, QHBoxLayout, QMenuBar
)
from PyQt6.QtGui import QPixmap, QAction, QPalette, QBrush
from PyQt6.QtCore import Qt
import os

class WelcomePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mars AI - Welcome")
        self.setGeometry(100, 100, 800, 600)

        # Set up the menu bar with black text
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("QMenuBar { color: black; font-size: 16px; } QMenu { color: black; font-size: 14px; }")

        avatar_menu = menu_bar.addMenu("Avatar")

        instruction_action = QAction("Instruction", self)
        instruction_action.triggered.connect(self.show_instructions)
        instruction_menu = menu_bar.addMenu("Instruction")
        instruction_menu.addAction(instruction_action)

        github_action = QAction("GitHub Link", self)
        github_action.triggered.connect(self.open_github)
        github_menu = menu_bar.addMenu("GitHub Link")
        github_menu.addAction(github_action)

        setting_menu = menu_bar.addMenu("Setting")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set background image
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        background_path = os.path.join(base_dir, "view", "viewImage", "welcomeBackground.png")

        if os.path.exists(background_path):
            background_pixmap = QPixmap(background_path)
            palette = QPalette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(background_pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)))
            self.setPalette(palette)
        else:
            print(f"[Background Image Not Found at {background_path}]")

        # Layouts
        main_layout = QVBoxLayout()
        button_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        # Welcome label
        welcome_label = QLabel("Welcome")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 36px; font-weight: bold; color: black; background-color: rgba(255, 255, 255, 180);")

        # Buttons
        button_style = "font-size: 16px; color: black; padding: 10px 20px; background-color: rgba(255, 255, 255, 200); border-radius: 10px;"

        instruction_button = QPushButton("Instruction")
        instruction_button.setStyleSheet(button_style)
        instruction_button.clicked.connect(self.show_instructions)

        github_button = QPushButton("GitHub Link")
        github_button.setStyleSheet(button_style)
        github_button.clicked.connect(self.open_github)

        about_button = QPushButton("About us")
        about_button.setStyleSheet(button_style)
        about_button.clicked.connect(self.show_about_us)

        start_button = QPushButton("START")
        start_button.setStyleSheet("font-size: 24px; color: black; padding: 10px 20px; background-color: rgba(0, 150, 255, 200); border-radius: 15px;")
        start_button.clicked.connect(self.start_application)

        # Add buttons to button layout
        button_layout.addWidget(instruction_button)
        button_layout.addWidget(github_button)
        button_layout.addWidget(about_button)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(base_dir, "view", "viewImage", "361Logo.jpg")

        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                logo_label.setPixmap(
                    logo_pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )
            else:
                logo_label.setText("[Failed to Load Logo Image]")
        else:
            logo_label.setText(f"[Logo Not Found at {logo_path}]")

        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right_layout.addWidget(logo_label)
        right_layout.addStretch()

        # Combine left buttons and right logo
        top_layout.addLayout(button_layout)
        top_layout.addLayout(right_layout)

        # Add widgets to main layout
        main_layout.addWidget(welcome_label)
        main_layout.addLayout(top_layout)
        main_layout.addStretch()
        main_layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        central_widget.setLayout(main_layout)

    def show_instructions(self):
        QMessageBox.information(
            self,
            "Instructions",
            "This page contains frequently used commands and basic instructions to help navigate the application effectively."
        )

    def open_github(self):
        webbrowser.open("https://github.com/VictorHe404/COMP361")

    def show_about_us(self):
        QMessageBox.information(
            self,
            "About Us",
            "Authors: Mars AI Team\\nContact: marsai@example.com"
        )

    def start_application(self):
        QMessageBox.information(self, "Start", "Entering the main page of the application.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WelcomePage()
    window.show()
    sys.exit(app.exec())
