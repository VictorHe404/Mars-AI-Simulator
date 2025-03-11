import webbrowser

from PyQt6.QtWidgets import QHBoxLayout, QMessageBox, QWidget, QPushButton


class TaskbarWidget(QWidget):
    """Custom Taskbar Widget."""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Taskbar layout
        taskbar_layout = QHBoxLayout()
        taskbar_layout.setSpacing(0)

        # Create buttons
        self.avatar_button = QPushButton("Avatar")
        self.instruction_button = QPushButton("Instruction")
        self.github_button = QPushButton("GitHub Link")
        self.setting_button = QPushButton("Setting")

        # Style buttons and add to layout
        for button in [self.avatar_button, self.instruction_button, self.github_button, self.setting_button]:
            button.setFlat(True)
            button.setFixedHeight(40)
            button.setStyleSheet("""
                QPushButton { padding: 10px; border: none; }
                QPushButton:hover { background-color: #ddd; }
            """)
            taskbar_layout.addWidget(button)

        self.setLayout(taskbar_layout)

        # Connect buttons to their functionalities
        self.avatar_button.clicked.connect(self.show_avatar)
        self.instruction_button.clicked.connect(self.show_instructions)
        self.github_button.clicked.connect(self.open_github_link)
        self.setting_button.clicked.connect(self.open_settings)

    def show_avatar(self):
        """Display avatar information."""
        QMessageBox.information(self, "Avatar", "Avatar feature is under development!")

    def show_instructions(self):
        """Display instructions for the application."""
        QMessageBox.information(
            self,
            "Instructions",
            "1. Use the navigation taskbar to explore features.\n"
            "2. Input commands in the terminal for advanced controls.\n"
            "3. Check settings to personalize the experience."
        )

    def open_github_link(self):
        """Open the GitHub repository."""
        try:
            webbrowser.open("https://github.com/VictorHe404/COMP361")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open GitHub link: {e}")

    def open_settings(self):
        """Open the settings dialog."""
        # settings_dialog = SettingDialog(self)
        # if settings_dialog.exec() == QDialog.DialogCode.Accepted:
        #     settings = settings_dialog.get_settings()
        #     QMessageBox.information(
        #         self, "Settings Saved",
        #         f"Username: {settings['username']}\nTheme: {settings['theme']}"
        #     )
        # else:
        #     QMessageBox.information(self, "Settings", "No changes were made.")
        print("[INFO] Opening settings dialog")
