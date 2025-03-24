from .EventManager import *
import sys
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QRunnable, QThreadPool

from controller.EventManager import EventManager
from view.WelcomeScreen import *
from view.MainPage import *
import time
import os

class Visualizer(QObject):
    """
    Visualizer: visualize the event
    """
    display_output_signal = pyqtSignal(str)
    update_mainmap_signal = pyqtSignal(str)
    update_minimap_signal = pyqtSignal(str)
    start_visualizer_signal = pyqtSignal()
    def __init__(self, event_manager: EventManager) -> None:
        super().__init__()
        self.event_manager = event_manager
        self.event_manager.register(self)
        print("Visualizer is registered")
        self.app = QApplication(sys.argv)
        self.window = WelcomePage()
        self.main_page = MainPage()
        self.window.start_signal.connect(self.on_start)
        self.main_page.command_signal.connect(self.execute_command)
        # Thread pool for concurrent task execution
        self.thread_pool = QThreadPool.globalInstance()
        self.display_output_signal.connect(self.main_page.display_output)
        self.update_mainmap_signal.connect(self.main_page.update_mainmap)
        self.update_minimap_signal.connect(self.main_page.update_minimap)
        self.start_visualizer_signal.connect(self.main_page.start_visualizer)

    def on_start(self):
        """
        Receive Start Signal from WelcomePage, and start the main page
        """
        print("Visualizer is starting")
        self.window.close()
        self.main_page.show()

    def execute_command(self, command: str) -> None:
        """
        Function to execute the command, and display the output
        """
        # post the command to EventManager so that KeyboardController can parse it
        # self.event_manager.post_event(CommandEvent(command))
        worker = CommandWorker(self.event_manager, command)
        self.thread_pool.start(worker)  # Submit task to the thread pool

    def initialize(self) -> None:
        """
        Initialize the Visualizer
        """
        print("Visualizer is initializing")

        # if not QApplication.instance():
        #     self.app = QApplication(sys.argv)  # Store it as an instance variable
        # else:
        #     self.app = QApplication.instance()
        self.window.show()
        sys.exit(self.app.exec())

    def notify(self, event: Event) -> None:
        """
        Notify the listener with the given event
        """
        if isinstance(event, Quit):
            self.event_manager.unregister(self)
            self.window.close()
        elif isinstance(event, InitialEvent):
            self.initialize()
        elif isinstance(event, ActionStatusEvent):
            print("status message", event.msg)
            self.display_output_signal.emit(event.msg)  # via signal to prevent the timer started from other thread
        elif isinstance(event, VisualizerEvent):
            if event.msg == "animation":
                self.start_visualizer_signal.emit()  # via signal to prevent the timer started from other thread
            elif event.msg == "minimap":
                if event.map_path in ["Louth_Crater_Normal", "Louth_Crater_Sharp"]:
                    self.update_minimap_signal.emit("Louth_Crater_minimap.png")
            elif event.msg in ["main_map", "task"]:
                self.update_mainmap_signal.emit(event.map_path)

    def __str__(self):
        return "Visualizer"


class CommandWorker(QRunnable):
    """Worker task that processes commands in parallel using QThreadPool."""

    output_signal = pyqtSignal(str)  # Signal to send output back

    def __init__(self, event_manager, command):
        super().__init__()
        self.event_manager = event_manager
        self.command = command

    def run(self):
        """Execute the command asynchronously."""
        self.event_manager.post_event(CommandEvent(self.command))  # Post event
        print(f"Command processed: {self.command}")
