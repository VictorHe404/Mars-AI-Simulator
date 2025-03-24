class Log:
    def __init__(self, index_x=0, index_y=0, detect_map=None, time=0,  energy=0):
        self.index_x = index_x
        self.index_y = index_y
        self.detect_map = detect_map if detect_map is not None else []
        self.time = time
        self.energy = energy
        self.local_grid = self.get_local_grid_str()

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

    def get_local_grid_str(self, size=3):
        if self.detect_map is None or not self.detect_map:
            return "[Empty detection map]"

        half = size // 2
        rows = len(self.detect_map)
        cols = len(self.detect_map[0]) if rows > 0 else 0

        lines = []
        for i in range(self.index_x - half, self.index_x + half + 1):
            line = ""
            for j in range(self.index_y - half, self.index_y + half + 1):
                if i == self.index_x and j == self.index_y:
                    cell = f"{'x':^5}"
                elif 0 <= i < rows and 0 <= j < cols:
                    val = self.detect_map[i][j]
                    if val == 114514:
                        cell = f"{'?':^5}"
                    else:
                        cell = f"{int(val):^5}"
                else:
                    cell = " " * 5
                line += cell
            lines.append(line)
        return "\n".join(lines)

    def print_log(self):
        print(self.__str__())