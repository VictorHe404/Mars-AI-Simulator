from .EventManager import *
import argparse
import shlex
from typing import Optional

class CommandController:
    """
    Command Controller: handle and parse the command from the user
    """
    def __init__(self, event_manager: EventManager) -> None:
        self.event_manager = event_manager
        self.event_manager.register(self)

        self.parser = argparse.ArgumentParser(prog="CLI")
        subparsers = self.parser.add_subparsers(dest="command")

        # Move command
        move_parser = subparsers.add_parser("move", help="Move to a destination")
        move_parser.add_argument("-t", "--target", type=int, nargs=4, required=True, help="Target position as four integers (x1, y1, x2, y2)")

        # Cavatar command
        create_avatar_parser = subparsers.add_parser("cavatar", help="Create an avatar")
        create_avatar_parser.add_argument("avatar_name", help="Name of the avatar")

        # Savatar command (Set avatar)
        savatar_parser = subparsers.add_parser("savatar", help="Set the current avatar")
        savatar_parser.add_argument("avatar_name", help="Name of the avatar to set")

        # Smap command (Set map)
        smap_parser = subparsers.add_parser("smap", help="Set the current map")
        smap_parser.add_argument("map_name", help="Name of the map to set")

        # Sbrain command (Set brain for avatar)
        sbrain_parser = subparsers.add_parser("sbrain", help="Set a brain for an avatar")
        sbrain_parser.add_argument("brain_name", help="Name of the brain to set")

        # Sdb command (Set or unset the database)
        sdb_parser = subparsers.add_parser("sdb", help="Enable or disable database usage")
        sdb_parser.add_argument("state", choices=["true", "false"],
                                help="Enable (true) or disable (false) database usage")

        lavatar_parser = subparsers.add_parser("lavatar", help="List existing avatars")
        lmap_parser = subparsers.add_parser("lmap", help="List existing maps")
        lbrain_parser = subparsers.add_parser("lbrain", help="List existing brains")


    def notify(self, event: Event) -> None:
        """
        Notify the listener with the given event
        """
        if isinstance(event, Quit):
            self.event_manager.unregister(self)
        elif isinstance(event, CommandEvent):
            print(f"CommandController received: {event.command}")
            # parse the command
            parsed_command = self.parse(event.command)
            print(f"CommandController parsed: {parsed_command}")
            if parsed_command is not None:
                self.event_manager.post_event(SimulatorEvent(parsed_command))
            else:
                self.event_manager.post_event(
                    ActionStatusEvent(False, "Invalid command", "CommandController"))



    def parse(self, command_str) -> Optional[dict[str, str]]:
        """Parses a command string and provides user-friendly error messages."""
        try:
            args = self.parser.parse_args(shlex.split(command_str))
            return vars(args)
        except SystemExit:
            print("Error: Invalid command. Type 'help' for usage.")
            return None

    def __str__(self):
        return "Keyboard Controller"
