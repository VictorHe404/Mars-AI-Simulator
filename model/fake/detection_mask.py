class DetectionMask:
    def __init__(self):
        self.detectable_positions = set()
        self.generate_mask()

    def generate_mask(self):
        self.detectable_positions.clear()
        detection_range = 1
        for dx in range(-detection_range, detection_range + 1):
            for dy in range(-detection_range, detection_range + 1):
                self.detectable_positions.add((dx, dy))

    def apply_mask(self, detect_map, full_map, x, y):
        rows, cols = len(full_map), len(full_map[0])
        for dx, dy in self.detectable_positions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < rows and 0 <= new_y < cols:
                detect_map[new_x][new_y] = full_map[new_x][new_y]
        return detect_map