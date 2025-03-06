class Environment:
    """
    Mars Terrain Friction Coefficients (μ)

    The friction coefficient (μ) is the ratio of frictional force to normal force,
    which determines how much grip an object (like a rover or astronaut) has on Mars' surface.

    Terrain Type            | Friction Coefficient (μ) | Description
    ------------------------|-------------------------|----------------------------
    Loose sand/dust         | ~0.3 - 0.4              | Slippery, similar to dry sand on Earth
    Compact soil            | ~0.5 - 0.6              | Firmer, more traction
    Rocky terrain           | ~0.6 - 0.8              | Good grip, like gravel
    Ice-covered regions     | ~0.1 - 0.3              | Very slippery, low traction

    """

    def __init__(self, friction=0.5, gravity=3.73, light_intensity=1.0):
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