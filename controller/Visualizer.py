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
            print("status message",event.msg)
            self.main_page.display_output(event.msg)
        elif isinstance(event, VisualizerEvent):
            self.main_page.start_visualizer()

    def __str__(self):
        return "Visualizer"

    # def visualize(self, pic_path: str) -> None:
    #     """
    #     Visualize the picture
    #     """
    #     pic_path = os.path.join(os.getcwd(), pic_path)
    #     print(f"Visualizer is visualizing {pic_path}")
    #     picture_counter = 0
    #     while os.path.exists(os.path.join(pic_path, f'elevation_map_{picture_counter+ 1}.png')):
    #         path = os.path.join(pic_path, f'elevation_map_{picture_counter + 1}.png')
    #         if picture_counter == 0:
    #             self.main_page.main_map.init_mainmap(path)
    #         else:
    #             self.main_page.main_map.update_mainmap(path)
    #         time.sleep(0.2)
    #         picture_counter += 1

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
