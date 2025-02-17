class Log:
    def __init__(self, index_x=0, index_y=0, detect_map=None, time=0,  energy=0):
        self.index_x = index_x
        self.index_y = index_y
        self.detect_map = detect_map if detect_map is not None else []
        self.time = time
        self.energy = energy

    def get_index_x(self):
        return self.index_x

    def get_index_y(self):
        return self.index_y

    def get_detect_map(self):
        return self.detect_map

    def get_time(self):
        return self.time

    def get_energy(self):
        return self.energy

    def __str__(self):
        return (f"Log Point - X: {self.index_x}, Y: {self.index_y}, Time: {self.time}, "
                f"Energy: {self.energy}, Detect Map: {self.detect_map}")

    def print_log(self):
        print(self.__str__())