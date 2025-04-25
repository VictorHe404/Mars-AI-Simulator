class Avatar:
    def __init__(self, name="", id_="", weight=0.0, material="", description="", battery_capacity=100.0,
                 battery_efficiency=0.0, battery_consumption_rate=1.0, driving_force=0.0, max_speed=1.0,
                 acceleration=0.0, max_slope=6.0, energy_recharge_rate=10.0, detection_mask=None):
        self.name = name
        self.id = id_
        self.weight = weight
        self.material = material
        self.description = description
        self.battery_capacity = battery_capacity
        self.battery_efficiency = battery_efficiency
        self.battery_consumption_rate = battery_consumption_rate
        self.driving_force = driving_force
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.max_slope = max_slope
        self.energy_recharge_rate = energy_recharge_rate
        self.detection_mask = detection_mask

    def print_avatar(self):
        return f"Avatar: {self.name}, Weight: {self.weight}, Battery: {self.battery_capacity}"

    def get_name(self):
        return self.name

    def get_weight(self):
        return self.weight

    def get_battery_capacity(self):
        return self.battery_capacity

    def get_max_speed(self):
        return self.max_speed

    def get_max_slope(self):
        return self.max_slope

    def get_movable(self, start_elevation, end_elevation):
        return abs(end_elevation - start_elevation) <= self.max_slope

    def get_energy_recharge_rate(self):
        return self.energy_recharge_rate

    def get_detection_mask(self):
        return self.detection_mask