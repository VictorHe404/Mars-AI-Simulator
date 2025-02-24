import EventManager

class Visualizer:
    """
    Visualizer: visualize the event
    """
    def __init__(self, event_manager: EventManager) -> None:
        self.event_manager = event_manager
        self.event_manager.register(self)

    def notify(self, event: EventManager.Event) -> None:
        """
        Notify the listener with the given event
        #### Message to Victor He: your visualizer should receive the CommandEvent
        and them visualize the command
        """
        print(f"Visualizer received: {event}")
        raise NotImplementedError

    def run(self) -> None:
        """
        Run the Visualizer
        ### you can design the run loop for the visualizer as you see fit
        """
        print("Visualizer is running")
        # while True:
        #     pass
        raise NotImplementedError

    def __str__(self):
        return "Visualizer"
