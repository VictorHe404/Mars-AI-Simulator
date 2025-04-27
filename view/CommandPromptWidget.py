from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

class CommandPromptWidget(QWidget):
    command_signal = pyqtSignal(str)

    def __init__(self, parent=None, height=250):
        super().__init__(parent)

        # Layout for terminal
        terminal_layout = QVBoxLayout()

        # Activity log (for command output)
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setFixedHeight(height)
        self.activity_log.setStyleSheet(
            "background-color: black; color: white; font-family: Consolas; font-size: 14px;"
        )

        # Command input
        self.command_input = QLineEdit()
        self.command_input.setStyleSheet(
            "background-color: black; color: white; font-family: Consolas; font-size: 14px;"
        )
        self.command_input.setPlaceholderText("Type a command...")
        self.command_input.returnPressed.connect(self.send_command)

        # Input layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.command_input)

        # Assemble layouts
        terminal_layout.addWidget(self.activity_log)
        terminal_layout.addLayout(input_layout)

        self.setLayout(terminal_layout)

    def send_command(self):
        """Emit the command when entered."""
        command = self.command_input.text().strip()
        if command:
            self.command_signal.emit(command)
            self.command_input.clear()

    def display_output(self, message):
        """Display the output message in the activity log."""
        self.activity_log.append(message)
        self.activity_log.moveCursor(QTextCursor.MoveOperation.End)
