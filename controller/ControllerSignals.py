from PyQt6.QtCore import QObject, pyqtSignal

class ControllerSignals(QObject):
    start_signal = pyqtSignal()
    command_signal = pyqtSignal(str)