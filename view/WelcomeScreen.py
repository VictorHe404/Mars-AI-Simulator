import sys
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QMessageBox, QVBoxLayout, QWidget, QHBoxLayout, QDialog, QTextEdit
)
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QDesktopServices
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
import os

class WelcomePage(QMainWindow):
    start_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mars AI - Welcome")

        window_width = 700
        window_height = 450
        self.setFixedSize(window_width, window_height)

        # Set at the middle of the screen
        screen = self.screen().availableGeometry()
        center_x = screen.center().x() - window_width // 2
        center_y = screen.center().y() - window_height // 2
        self.move(center_x, center_y)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set background image
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        background_path = os.path.join(base_dir, "view", "viewImage", "welcomeBackground.png")

        background_pixmap = QPixmap(background_path)
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(background_pixmap.scaled(
            self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)))
        self.setPalette(palette)

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
        """Display instructions for the application."""
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

    def open_github(self):
        """Open the project's GitHub repository."""
        webbrowser.open("https://github.com/VictorHe404/COMP361")

    def show_about_us(self):
        """Display information about the team."""
        QMessageBox.information(
            self,
            "About Us",
            "Authors: Mars AI Team\nContact: marsai@example.com"
        )

    def start_application(self):
        """Emit the start signal to transition to the main application."""
        print("Starting application...")
        self.start_signal.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WelcomePage()
    window.show()
    sys.exit(app.exec())
