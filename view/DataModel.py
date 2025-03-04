from PyQt6.QtCore import QObject, pyqtSignal


class DataModel(QObject):
    activity_log_updated = pyqtSignal(str)
    path_result_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.cache = ""

    def write_to_cache(self, data: str):
        """
        Writes data to the cache storage.

        The method writes the provided data to the cache attribute
        of the class. The data must be a string, and it replaces
        any previously stored value in the cache.

        Parameters:
            data: str
                The data to be stored in the cache.
        """
        self.cache = data

    def log_activity(self, log: str):
        """
        Logs a new activity and emits a signal with the provided log message.
        This method is used to record activity logs and notify connected
        listeners via the `activity_log_updated` signal. The signal is emitted
        with the given log message.

        Parameters
        ----------
        log : str
            The log message to be added and emitted via the signal.
        """
        self.activity_log_updated.emit(log)

    def update_path_result(self, result: str):
        """
        Updates the path result and emits a signal for the updated value.

        Parameters:
        result (str): The updated result value for the path.

        Raises:
        None

        Returns:
        None
        """
        self.path_result_updated.emit(result)