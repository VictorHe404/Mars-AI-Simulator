from PyQt6.QtCore import QObject, pyqtSignal

class TestSignals(QObject):
    test_signal = pyqtSignal(str)

    def emit_signal(self):
        self.test_signal.emit("Test Message1")

def handle_message(message):
    print(f"Received message: {message}")

if __name__ == "__main__":
    test = TestSignals()
    test.test_signal.connect(handle_message)
    test.emit_signal()