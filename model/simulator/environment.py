class Environment:
    def __init__(self, friction=0.0, gravity=9.8, light_intensity=1.0):
        self.friction = friction
        self.gravity = gravity
        self.light_intensity = light_intensity

    def get_friction(self):
        return self.friction

    def get_gravity(self):
        return self.gravity

    def get_light_intensity(self):
        return self.light_intensity

    def set_friction(self, friction):
        self.friction = friction

    def set_gravity(self, gravity):
        self.gravity = gravity

    def set_light_intensity(self, light_intensity):
        self.light_intensity = light_intensity