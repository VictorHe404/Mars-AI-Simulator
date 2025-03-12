from xmlrpc.client import boolean

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
        is_created = self.simulator.add_avatar(avatar_name)
        if not is_created:
            error_message = "Avatar creation failed due to duplicated avatar name."
            self.event_manager.post_event(
                ActionStatusEvent(is_created,error_message, "create_avatar"))
        else:
            success_message = "Avatar created successfully."
            self.event_manager.post_event(
                ActionStatusEvent(is_created, success_message, "create_avatar"))

    def set_avatar(self, avatar_name: str) -> None:
        is_set = self.simulator.set_avatar(avatar_name)
        if not is_set:
            error_message = "Avatar set failed due to avatar does not exist."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, error_message, "set_avatar"))
        else:
            success_message = "Avatar set successfully."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, success_message, "set_avatar"))

    def set_map(self, map_name: str) -> None:
        is_set = self.simulator.set_map(map_name)
        if not is_set:
            error_message = "Map set failed due map not found."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, error_message, "set_map"))
        else:
            success_message = "Map set successfully."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, success_message, "set_map"))

    def set_task(self, start_row, start_col, destination_row, destination_col) -> None:
        is_set = self.simulator.set_task(start_row, start_col, destination_row, destination_col)
        if not is_set:
            error_message = "Task set failed due to invalid coordinates."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, error_message, "set_task"))
        else:
            success_message = "Task set successfully."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, success_message, "set_task"))

    def set_brain(self, brain_name: str) -> None:
        is_set = self.simulator.set_brain(brain_name)
        if not is_set:
            error_message = f"Brain set failed due to invalid brain name: {brain_name}."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, error_message, "set_brain"))
        else:
            success_message = f"Brain set successfully to {brain_name}."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, success_message, "set_brain"))

    def run_simulator(self) -> None:
        is_running = self.simulator.run()
        if not is_running:
            error_message = "Simulator failed to start due to unset elements."
            self.event_manager.post_event(
                ActionStatusEvent(is_running, error_message, "run_simulator"))
        else:
            success_message = "Simulator finished successfully."
            self.event_manager.post_event(
                ActionStatusEvent(is_running, success_message, "run_simulator"))













