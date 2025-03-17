from xmlrpc.client import boolean

from model.simulator import *
from .EventManager import *
import threading

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
            # self.simulator.initialize()
            pass
        elif isinstance(event, SimulatorEvent):
            print("SimulatorManager received SimulatorEvent")
            command = event.cmd
            print(f"SimulatorManager received: {command}")
            if command["command"] == "cavatar":
                print("SimulatorManager received create_avatar command")
                self.create_avatar(command["avatar_name"])
            elif command["command"] == "savatar":
                print("SimulatorManager received set_avatar command")
                self.set_avatar(command["avatar_name"])
            elif command["command"] == "smap":
                print("SimulatorManager received set_map command")
                self.set_map(command["map_name"])
            elif command["command"] == "sbrain":
                print("SimulatorManager received set_brain command")
                self.set_brain(command["brain_name"])
            elif command["command"] == "move":
                print("SimulatorManager received move command")
                self.set_task(command["target"][0], command["target"][1],
                              command["target"][2], command["target"][3])
                self.run_simulator()
            elif command["command"] == "sdb":
                print("SimulatorManager received sdb command")
                self.set_database(command["state"] == "true")
            elif command["command"] == "lavatar":
                print("SimulatorManager received lavatar command")
                self.list_avatars()
            elif command["command"] == "lmap":
                print("SimulatorManager received lmap command")
                self.list_maps()
            elif command["command"] == "lbrain":
                print("SimulatorManager received lbrain command")
                self.list_brains()


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
            error_message = f"[cavatar] Avatar creation failed due to duplicated avatar name: {avatar_name}."
            self.event_manager.post_event(
                ActionStatusEvent(is_created,error_message, "create_avatar"))
        else:
            success_message = f"[cavatar] Avatar '{avatar_name}' created successfully."
            self.event_manager.post_event(
                ActionStatusEvent(is_created, success_message, "create_avatar"))

    def set_avatar(self, avatar_name: str) -> None:
        is_set = self.simulator.set_avatar(avatar_name)
        if not is_set:
            error_message = f"[savatar] Avatar '{avatar_name}' set failed because it does not exist."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, error_message, "set_avatar"))
        else:
            success_message = f"[savatar] Avatar '{avatar_name}' set successfully."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, success_message, "set_avatar"))

    def set_map(self, map_name: str) -> None:
        is_set = self.simulator.set_map(map_name)
        if not is_set:
            error_message = f"[smap] Map '{map_name}' set failed because the map was not found."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, error_message, "set_map"))
        else:
            success_message = f"[smap] Map '{map_name}' set successfully."
            self.event_manager.post_event(VisualizerEvent("minimap", map_name))
            self.event_manager.post_event(
                ActionStatusEvent(is_set, success_message, "set_map"))

    def set_task(self, start_row, start_col, destination_row, destination_col) -> None:
        is_set = self.simulator.set_task(start_row, start_col,
                                         destination_row, destination_col)
        self.event_manager.post_event(ActionStatusEvent(True, "[move] Task set successfully.", "set_task"))
        if not is_set:
            error_message = f"[move] Task set failed due to invalid coordinates: ({start_row}, {start_col}) → ({destination_row}, {destination_col})."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, error_message, "set_task"))
        else:
            success_message = f"[move] Task set successfully from ({start_row}, {start_col}) to ({destination_row}, {destination_col}). \n start calculating the path."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, success_message, "set_task"))

    def set_brain(self, brain_name: str) -> None:
        is_set = self.simulator.set_brain(brain_name)
        if not is_set:
            error_message = f"[sbrain] Brain set failed due to invalid brain name: {brain_name}."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, error_message, "set_brain"))
        else:
            success_message = f"[sbrain] Brain set successfully to {brain_name}."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, success_message, "set_brain"))

    def run_simulator(self) -> None:
        is_running, running_result = self.simulator.run()
        if not is_running:
            error_message = "[move] Simulator failed to start due to unset elements (missing map, avatar, or task)."
            self.event_manager.post_event(
                ActionStatusEvent(is_running, error_message, "run_simulator"))
        else:
            success_message = "[move] Simulator finished successfully, start to animate the process.\n"
            result_message = f"[move] Task completed." if running_result else "[move] Task failed."
            message =  result_message + success_message
            self.event_manager.post_event(
                ActionStatusEvent(is_running, message, "run_simulator"))
            self.event_manager.post_event(VisualizerEvent("animation", self.simulator.target_map))


    def set_database(self, database_available: bool) -> None:
        self.simulator.database_available = database_available
        success_message = f"[sdb] Database connection set to {database_available}."
        self.event_manager.post_event(
            ActionStatusEvent(True, success_message, "set_database")
        )

    def list_avatars(self) -> None:
        avatar_names = self.simulator.get_avatar_names()

        if not avatar_names:
            message = "[lavatar] No avatars found."
        else:
            message = "[lavatar] List of existing avatars:\n"
            message += "\n".join([f"  - {name}" for name in avatar_names])

        self.event_manager.post_event(
            ActionStatusEvent(True, message, "list_avatars")
        )

    def list_brains(self) -> None:
        brain_names = self.simulator.get_brain_names()

        if not brain_names:
            message = "[lbrain] No brains found."
        else:
            message = "[lbrain] List of available brains:\n"
            message += "\n".join([f"  - {name}" for name in brain_names])

        self.event_manager.post_event(
            ActionStatusEvent(True, message, "list_brains")
        )

    def list_maps(self) -> None:
        map_names = self.simulator.get_map_names()

        if not map_names:
            message = "[lmap] No maps found."
        else:
            message = "[lmap] List of available maps:\n"
            message += "\n".join([f"  - {name}" for name in map_names])

        self.event_manager.post_event(
            ActionStatusEvent(True, message, "list_maps")
        )




