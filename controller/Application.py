from .EventManager import *
from .CommandController import CommandController
from .Visualizer import Visualizer
from .SimulatorManager import *


class Application:
    """
    Application class: the main class of the application
    """
    def __init__(self) -> None:
        self.running = False
        self.event_manager = EventManager()
        self.keyboard_controller = CommandController(self.event_manager)
        self.visualizer = Visualizer(self.event_manager)
        self.simulator_manager = SimulatorManager(self.event_manager)

    def notify(self, event: Event) -> None:
        """
        Notify the listener with the given event
        """
        if isinstance(event, Quit):
            self.running = False
            self.event_manager.unregister(self)

        elif isinstance(event, InitialEvent):
            print("Application is initializing")
            self.running = True
        elif isinstance(event, TicketEvent):
            pass

    def run(self) -> None:
        """
        Run the application
        """
        self.event_manager.post_event(InitialEvent("Application is running"))


    def __str__(self):
        return "Application"
