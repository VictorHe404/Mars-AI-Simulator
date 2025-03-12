from ..model.simulator import *
from .EventManager import *

class SimulatorManager:
    def __init__(self, event_manager: EventManager) -> None:
        self.event_manager = event_manager
        self.event_manager.register(self)
        self.simulator = Simulator()
        print("SimulatorManager is registered")

    def notify(self, event: Event) -> None:
        """
        Notify the listener with the given event
        """
        print(f"SimulatorManager received: {event}")

        if isinstance(event, Quit):
            self.event_manager.unregister(self)
        elif isinstance(event, InitialEvent):
            self.simulator.initialize()
        elif isinstance(event, TicketEvent):
             if TicketEvent.msg == "Create avatar a1":
                    self.simulator.create_avatar("a1")



    def initialize(self, avatar_name: str | None) -> None:
        """
        Initialize the SimulatorManager
        """
        print("SimulatorManager is initializing")
        if avatar_name is not None:
            self.simulator.initialize(avatar_name)
        else:
            self.simulator.initialize("default_avatar")
        # TODO 1: set avatar name
        # TODO 2: set task
        # TODO 3: move from A to B

    def create_avatar(self, avatar_name: str) -> None:
        """
        Create an avatar
        """
        self.simulator.create_avatar(avatar_name)
        # finished creating avatar
        self.event_manager.post_event(TicketEvent("Avatar created"))
