from EventManager import *
from KeyboardController import KeyboardController

class Application:
    """
    Application class: the main class of the application
    """
    def __init__(self) -> None:
        self.event_manager = EventManager()

        self.keyboard_controller = KeyboardController(self.event_manager)
        # self.visualizer = Visualizer(self.event_manager)

    def run(self) -> None:
        """
        Run the application
        """
        self.keyboard_controller.run()
        # self.visualizer.run()

    def __str__(self):
        return "Application"
