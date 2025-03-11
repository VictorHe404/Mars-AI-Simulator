from controller.ControllerSignals import ControllerSignals
# from .EventManager import *
import sys
from PyQt6.QtCore import QObject
from view.WelcomeScreen import *
from view.MainPage import *

class Visualizer(QObject):
    """
    Visualizer: visualize the event
    """
    # def __init__(self, event_manager: EventManager, signals) -> None
    # 暂时移除event manager，用于测试代码
    def __init__(self) -> None:
        super().__init__()
        # self.event_manager = event_manager
        # self.event_manager.register(self)
        # Initialize instance variables to None
        # self.app: QApplication | None = None
        # self.window: WelcomePage | None = None
        print("Visualizer is registered")
        self.app = QApplication(sys.argv)
        self.window = WelcomePage()
        self.main_page = MainPage()
        self.window.start_signal.connect(self.on_start)
        self.main_page.command_signal.connect(self.excute_command)

    def on_start(self):
        """
        Receive Start Signal from WelcomePage, and start the main page
        """
        print("Visualizer is starting")
        self.window.close()
        self.main_page.show()

    def excute_command(self, command):
        """
        Function to execute the command, and display the output
        """
        if command == "hello":
            self.main_page.display_output(
                "Hello, world!")

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

    # def notify(self, event: Event) -> None:
    #     """
    #     Notify the listener with the given event
    #     #### Message to Victor He: your visualizer should receive the CommandEvent
    #     and them visualize the command
    #     """
    #     print(f"Visualizer received: {event}")
    #
    #     if isinstance(event, Quit):
    #         self.event_manager.unregister(self)
    #         self.window.close()
    #     elif isinstance(event, InitialEvent):
    #         self.initialize()
    #     elif isinstance(event, TicketEvent):
    #         pass
    #
    #     pass

    def __str__(self):
        return "Visualizer"

if __name__ == "__main__":
    visualizer = Visualizer()
    visualizer.initialize()
