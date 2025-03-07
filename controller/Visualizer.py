from .EventManager import *
import sys
from PyQt6.QtCore import QObject
from view.WelcomeScreen import *

class Visualizer(QObject):
    """
    Visualizer: visualize the event
    """
    def __init__(self, event_manager: EventManager) -> None:
        super().__init__()
        self.event_manager = event_manager
        self.event_manager.register(self)
        # Initialize instance variables to None
        self.app: QApplication | None = None
        self.window: WelcomePage | None = None
        print("Visualizer is registered")

    def initialize(self) -> None:
        """
        Initialize the Visualizer
        """
        print("Visualizer is initializing")

        if not QApplication.instance():
            self.app = QApplication(sys.argv)  # Store it as an instance variable
        else:
            self.app = QApplication.instance()

        self.window = WelcomePage()  # Store the window as an instance variable
        self.window.show()
        self.app.exec()

    def notify(self, event: Event) -> None:
        """
        Notify the listener with the given event
        #### Message to Victor He: your visualizer should receive the CommandEvent
        and them visualize the command
        """
        print(f"Visualizer received: {event}")

        if isinstance(event, Quit):
            self.event_manager.unregister(self)
            self.window.close()
        elif isinstance(event, InitialEvent):
            self.initialize()
        elif isinstance(event, TicketEvent):
            pass

    def __str__(self):
        return "Visualizer"

