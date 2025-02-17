# model/brain.py
from abc import ABC, abstractmethod
from model.fake import Log, Task, Environment, Avatar

# The abstract class for Brain
class Brain(ABC):
    def __init__(self):
        self.task_trail = []
        self.detect_map = []
        self.original_map = []
        self.current_task = None
        self.current_avatar = None
        self.current_environment = None
        self.time = 0

    def set_original_map(self, original_map):
        self.original_map = original_map

    def set_task(self, task: Task):
        self.current_task = task

    def set_avatar(self, avatar: Avatar):
        self.current_avatar = avatar

    def set_environment(self, environment: Environment):
        self.current_environment = environment

    def get_trail(self):
        return self.task_trail

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def reset(self):
        pass
