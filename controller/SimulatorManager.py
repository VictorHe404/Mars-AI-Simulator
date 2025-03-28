from xmlrpc.client import boolean

from model.simulator import *
from .EventManager import *
import threading
import os

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
            status, msg = False, "This is a default message"
            if command["command"] == "cavatar":
                print("SimulatorManager received create_avatar command")
                status, msg = self.create_avatar(command["avatar_name"])
            elif command["command"] == "savatar":
                print("SimulatorManager received set_avatar command")
                status, msg = self.set_avatar(command["avatar_name"])
            elif command["command"] == "smap":
                print("SimulatorManager received set_map command")
                status, msg = self.set_map(command["map_name"])
            elif command["command"] == "sbrain":
                print("SimulatorManager received set_brain command")
                status, msg = self.set_brain(command["brain_name"])


            elif command["command"] == "move":
                print("SimulatorManager received move command")
                self.set_task(command["target"][0], command["target"][1],
                              command["target"][2], command["target"][3])
                status, msg = self.run_simulator()

            elif command["command"] == "stask":
                print("SimulatorManager received stask command")
                status, msg = self.set_task(command["x1"], command["y1"], command["x2"], command["y2"])
            elif command["command"] == "run":
                print("SimulatorManager received run command")
                status, msg = self.run_simulator()


            elif command["command"] == "sdb":
                print("SimulatorManager received sdb command")
                status, msg = self.set_database(command["state"] == "true")



            elif command["command"] == "lavatar":
                print("SimulatorManager received lavatar command")
                status, msg = self.list_avatars()
            elif command["command"] == "lmap":
                print("SimulatorManager received lmap command")
                status, msg = self.list_maps()
            elif command["command"] == "lbrain":
                print("SimulatorManager received lbrain command")
                status, msg = self.list_brains()



            #fast_task a1 Louth_Crater_Sharp greedy -t 20 20 35 45
            elif command["command"] == "fast_task":
                print("SimulatorManager received fast_task command")
                status, msg = self.fast_task(command)

            elif command["command"] == "iavatar":
                print("SimulatorManager received iavatar command")
                avatar_name = command.get("avatar_name")

                if avatar_name:
                    found, info = self.simulator.get_avatar_characteristics(avatar_name)
                    if found:
                        status, msg = True, f"[iavatar] Info for avatar '{avatar_name}':\n{info}"
                    else:
                        status, msg = False, f"[iavatar] Avatar '{avatar_name}' not found."
                else:
                    found, info = self.simulator.get_target_avatar_characteristics()
                    if found:
                        status, msg = True, f"[iavatar] Info for currently selected avatar:\n{info}"
                    else:
                        status, msg = False, "[iavatar] No avatar is currently selected."

            if not event.task_bar:
                self.event_manager.post_event(
                    ActionStatusEvent(status, msg, command["command"]))
            else:
                self.event_manager.post_event(
                    ActionStatusEvent(status, msg, command["command"], task_bar=True))


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

    def create_avatar(self, avatar_name: str) -> (bool, str):
        is_created = self.simulator.add_avatar(avatar_name)
        if not is_created:
            message = f"[cavatar] Avatar creation failed due to duplicated avatar name: {avatar_name}."
        else:
            message = f"[cavatar] Avatar '{avatar_name}' created successfully."
        return is_created, message

    def set_avatar(self, avatar_name: str) -> (bool, str):
        is_set = self.simulator.set_avatar(avatar_name)
        if not is_set:
            message = f"[savatar] Avatar '{avatar_name}' set failed because it does not exist."
        else:
            message = f"[savatar] Avatar '{avatar_name}' set successfully."
        return is_set, message

    def set_map(self, map_name: str) -> (bool, str):
        is_set = self.simulator.set_map(map_name)
        if not is_set:
            message = f"[smap] Map '{map_name}' set failed because the map was not found."
        else:
            message = f"[smap] Map '{map_name}' set successfully."
            self.event_manager.post_event(VisualizerEvent("minimap", map_name))
            cache_path = os.path.join(os.getcwd(), 'cache_directory_2')
            pic_path = os.path.join(cache_path, f'set_map.png')
            self.event_manager.post_event(VisualizerEvent("main_map", pic_path))
        return is_set, message

    def set_task(self, start_row, start_col, destination_row, destination_col) -> (bool, str):
        is_set = self.simulator.set_task(start_row, start_col,
                                         destination_row, destination_col)
        if not is_set:
            message = f"[stask] Task set failed due to invalid coordinates: ({start_row}, {start_col}) → ({destination_row}, {destination_col})."
        else:
            message = f"[stask] Task set successfully from ({start_row}, {start_col}) to ({destination_row}, {destination_col})."
            cache_path = os.path.join(os.getcwd(), 'cache_directory_2')
            pic_path = os.path.join(cache_path, f'set_task_map.png')
            self.event_manager.post_event(VisualizerEvent("task", pic_path))
        return is_set, message

    def set_brain(self, brain_name: str) -> (bool, str):
        is_set = self.simulator.set_brain(brain_name)
        if not is_set:
            message = f"[sbrain] Brain set failed due to invalid brain name: {brain_name}."
        else:
            message = f"[sbrain] Brain set successfully to {brain_name}."
        return is_set, message

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

    def run_simulator(self) -> (bool, str):
        is_running, running_result, estimated_time, virtual_time = self.simulator.run_simulation()

        if not is_running:
            error_message = "[run] Simulator failed to start due to unset elements (missing map, avatar, or task)."
            return False , error_message
        pre_animation_msg = f"[run] The task took {virtual_time} seconds of simulate time to finish.\n"
        pre_animation_msg += f"[run] Task {'completed' if running_result else 'failed'}, starting processing animation...\n"
        pre_animation_msg += f"[run] Estimated duration: ~{estimated_time} seconds."
        self.event_manager.post_event(ActionStatusEvent(is_running,pre_animation_msg, "run_simulator"))
        self.simulator.process_simulation_output()
        success_msg = "[run] Simulator finished successfully, start to animate the process."
        #result_msg = "[run] Task completed." if running_result else "[move] Task failed."
        self.event_manager.post_event(
            VisualizerEvent("animation", self.simulator.target_map)
        )
        return True, success_msg



    def set_database(self, database_available: bool) -> (bool, str):
        self.simulator.database_available = database_available
        success_message = f"[sdb] Database connection set to {database_available}."
        return True, success_message

    def list_avatars(self) -> (bool, str):
        avatar_names = self.simulator.get_avatar_names()

        if not avatar_names:
            message = "[lavatar] No avatars found."
        else:
            message = "[lavatar] List of existing avatars:\n"
            message += "\n".join([f"  - {name}" for name in avatar_names])
        return True, message

    def list_brains(self) -> (bool, str):
        brain_names = self.simulator.get_brain_names()

        if not brain_names:
            message = "[lbrain] No brains found."
        else:
            message = "[lbrain] List of available brains:\n"
            message += "\n".join([f"  - {name}" for name in brain_names])

        return True, message

    def list_maps(self) -> (bool, str):
        map_names = self.simulator.get_map_names()

        if not map_names:
            message = "[lmap] No maps found."
        else:
            message = "[lmap] List of available maps:\n"
            message += "\n".join([f"  - {name}" for name in map_names])
        return True, message

    def fast_task(self, command: dict) -> (bool, str):
        """
        Performs a fast task setup, including setting the avatar, map, brain, and movement task.
        """

        avatar_name = command["avatar_name"]
        map_name = command["map_name"]
        brain_name = command["brain_name"]
        target = command["target"]

        print(f"Fast task setup started: Avatar={avatar_name}, Map={map_name}, Brain={brain_name}, Target={target}")

        if not self.simulator.set_avatar(avatar_name):
            error_message = f"[fast_task] Failed: Avatar '{avatar_name}' does not exist."
            return False, error_message

        if not self.simulator.set_map(map_name):
            error_message = f"[fast_task] Failed: Map '{map_name}' not found."
            return False, error_message

        if not self.simulator.set_brain(brain_name):
            error_message = f"[fast_task] Failed: Brain '{brain_name}' not recognized."
            return False, error_message

        if not self.simulator.set_task(target[0], target[1], target[2], target[3]):
            error_message = f"[fast_task] Failed: Invalid movement coordinates ({target[0]}, {target[1]}) → ({target[2]}, {target[3]})."
            return False, error_message

        status, msg = self.run_simulator()
        self.event_manager.post_event(ActionStatusEvent(status, msg, "run_simulator"))

        success_message = f"[fast_task] Successfully configured and started simulation with Avatar='{avatar_name}', Map='{map_name}', Brain='{brain_name}', Task=({target[0]}, {target[1]}) → ({target[2]}, {target[3]})."
        return True, success_message




