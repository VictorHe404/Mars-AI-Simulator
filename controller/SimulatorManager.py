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

            elif command["command"] == "stask":
                print("SimulatorManager received stask command")
                self.set_task(command["x1"], command["y1"], command["x2"], command["y2"])
            elif command["command"] == "run":
                print("SimulatorManager received run command")
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



            #fast_task a1 Louth_Crater_Sharp greedy -t 20 20 35 45
            elif command["command"] == "fast_task":
                print("SimulatorManager received fast_task command")
                self.fast_task(command)

            elif command["command"] == "iavatar":
                print("SimulatorManager received iavatar command")
                avatar_name = command.get("avatar_name")

                if avatar_name:
                    found, info = self.simulator.get_avatar_characteristics(avatar_name)
                    if found:
                        self.event_manager.post_event(
                            ActionStatusEvent(True, f"[iavatar] Info for avatar '{avatar_name}':\n{info}", "iavatar"))
                    else:
                        self.event_manager.post_event(
                            ActionStatusEvent(False, f"[iavatar] Avatar '{avatar_name}' not found.", "iavatar"))
                else:
                    found, info = self.simulator.get_target_avatar_characteristics()
                    if found:
                        self.event_manager.post_event(
                            ActionStatusEvent(True, f"[iavatar] Info for currently selected avatar:\n{info}",
                                              "iavatar"))
                    else:
                        self.event_manager.post_event(
                            ActionStatusEvent(False, "[iavatar] No avatar is currently selected.", "iavatar"))



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
        self.event_manager.post_event(ActionStatusEvent(True, "[stask] Task set successfully.", "set_task"))
        if not is_set:
            error_message = f"[stask] Task set failed due to invalid coordinates: ({start_row}, {start_col}) → ({destination_row}, {destination_col})."
            self.event_manager.post_event(
                ActionStatusEvent(is_set, error_message, "set_task"))
        else:
            success_message = f"[stask] Task set successfully from ({start_row}, {start_col}) to ({destination_row}, {destination_col})."
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

    '''
    def run_simulator(self) -> None:
        is_running, running_result = self.simulator.run()
        if not is_running:
            error_message = "[run] Simulator failed to start due to unset elements (missing map, avatar, or task)."
            self.event_manager.post_event(
                ActionStatusEvent(is_running, error_message, "run_simulator"))
        else:
            success_message = "[run] Simulator finished successfully, start to animate the process.\n"
            result_message = f"[run] Task completed." if running_result else "[move] Task failed."
            message =  result_message + success_message
            self.event_manager.post_event(
                ActionStatusEvent(is_running, message, "run_simulator"))
            self.event_manager.post_event(VisualizerEvent("animation", self.simulator.target_map))
    '''

    def run_simulator(self) -> None:
        is_running, running_result, estimated_time, virtual_time = self.simulator.run_simulation()

        if not is_running:
            error_message = "[run] Simulator failed to start due to unset elements (missing map, avatar, or task)."
            self.event_manager.post_event(
                ActionStatusEvent(False, error_message, "run_simulator")
            )
            return
        pre_animation_msg = f"[run] The task took {virtual_time} seconds of simulate time to finish.\n"
        pre_animation_msg += f"[run] Task {'completed' if running_result else 'failed'}, starting processing animation...\n"
        pre_animation_msg += f"[run] Estimated duration: ~{estimated_time} seconds."
        self.event_manager.post_event(ActionStatusEvent(is_running,pre_animation_msg, "run_simulator"))
        self.simulator.process_simulation_output()
        success_msg = "[run] Simulator finished successfully, start to animate the process."
        #result_msg = "[run] Task completed." if running_result else "[move] Task failed."
        final_msg = success_msg
        self.event_manager.post_event(
            ActionStatusEvent(True, final_msg, "run_simulator")
        )
        self.event_manager.post_event(
            VisualizerEvent("animation", self.simulator.target_map)
        )



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

    def fast_task(self, command: dict) -> None:
        """
        Performs a fast task setup, including setting the avatar, map, brain, and movement task.
        """

        avatar_name = command["avatar_name"]
        map_name = command["map_name"]
        brain_name = command["brain_name"]
        target = command["target"]  # List of 4 integers: x1, y1, x2, y2

        print(f"Fast task setup started: Avatar={avatar_name}, Map={map_name}, Brain={brain_name}, Target={target}")

        # Step 1: Set the avatar
        if not self.simulator.set_avatar(avatar_name):
            error_message = f"[fast_task] Failed: Avatar '{avatar_name}' does not exist."
            self.event_manager.post_event(ActionStatusEvent(False, error_message, "fast_task"))
            return

        # Step 2: Set the map
        if not self.simulator.set_map(map_name):
            error_message = f"[fast_task] Failed: Map '{map_name}' not found."
            self.event_manager.post_event(ActionStatusEvent(False, error_message, "fast_task"))
            return

        # Step 3: Set the brain
        if not self.simulator.set_brain(brain_name):
            error_message = f"[fast_task] Failed: Brain '{brain_name}' not recognized."
            self.event_manager.post_event(ActionStatusEvent(False, error_message, "fast_task"))
            return

        # Step 4: Set the movement task
        if not self.simulator.set_task(target[0], target[1], target[2], target[3]):
            error_message = f"[fast_task] Failed: Invalid movement coordinates ({target[0]}, {target[1]}) → ({target[2]}, {target[3]})."
            self.event_manager.post_event(ActionStatusEvent(False, error_message, "fast_task"))
            return

        # Step 5: Run the simulation
        self.run_simulator()

        success_message = f"[fast_task] Successfully configured and started simulation with Avatar='{avatar_name}', Map='{map_name}', Brain='{brain_name}', Task=({target[0]}, {target[1]}) → ({target[2]}, {target[3]})."
        self.event_manager.post_event(ActionStatusEvent(True, success_message, "fast_task"))




