from EventManager import EventManager, Event, Quit, CommandEvent

class KeyboardController:
    """
    Keyboard Controller: handle the keyboard input
    """
    def __init__(self, event_manager: EventManager) -> None:
        self.event_manager = event_manager
        self.event_manager.register(self)

    def notify(self, event: Event) -> None:
        """
        Notify the listener with the given event
        """
        if isinstance(event, Quit):
            self.event_manager.unregister(self)
            self.event_manager.post_event(Quit("Keyboard Controller is shutting down"))

    def run(self) -> None:
        """
        Run the Keyboard Controller
        """
        print("Keyboard Controller is running")
        while True:
            command = input("Enter a command: ")
            self.event_manager.post_event(CommandEvent(command))

    def __str__(self):
        return "Keyboard Controller"
