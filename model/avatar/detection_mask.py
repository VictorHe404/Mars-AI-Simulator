import sqlite3
import numpy as np
from model.avatar.database import DB_NAME
from model.avatar.sensor import Sensor


class DetectionMask:
    def __init__(self, avatar_id):
        """
        Initialize DetectionMask for a specific Avatar
        :param avatar_id: ID of the Avatar for which the detection mask is calculated
        """
        self.avatar_id = avatar_id

        # Stores all detectable positions as (dx, dy) relative to the Avatar's current position
        # Using a set to avoid duplicate positions
        self.detectable_positions = set()

        # Get all sensors bound to this Avatar
        self.sensors = self.get_sensors()

        # Generate the detection mask based on sensors
        self.generate_mask()

    def get_sensors(self):
        """
        Get all sensors bound to this Avatar
        :return: List of Sensor objects
        """
        # Connect to the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Query all sensors associated with this Avatar
        cursor.execute('''
            SELECT Sensor.id, Sensor.name, Sensor.range, Sensor.fov, Sensor.battery_consumption, 
                   Sensor.description, Sensor.direction
            FROM Sensor
            JOIN AvatarSensor ON Sensor.id = AvatarSensor.sensor_id
            WHERE AvatarSensor.avatar_id = ?
        ''', (self.avatar_id,))

        # Fetch all the results
        sensors_data = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert fetched data to a list of Sensor objects
        # Using list comprehension for clean and readable code
        return [Sensor(*sensor[1:], sensor_id=sensor[0]) for sensor in sensors_data]

    def generate_mask(self):
        """
        Generate the detection mask based on sensors' range, fov, and direction
        Stores all detectable positions as (dx, dy) in self.detectable_positions
        """
        # Clear any existing detectable positions
        self.detectable_positions.clear()

        # Loop through all sensors attached to this Avatar
        for sensor in self.sensors:
            # Get the detection range, fov, and direction of the sensor
            detection_range = int(sensor.get_range())
            fov = sensor.get_fov()  # Field of View
            direction = sensor.get_direction()  # Direction the sensor is facing

            # Loop through all positions within the detection range
            for dx in range(-detection_range, detection_range + 1):
                for dy in range(-detection_range, detection_range + 1):
                    # Calculate the distance from the center (0, 0)
                    distance = np.sqrt(dx ** 2 + dy ** 2)

                    # If within range, calculate the angle
                    if distance <= detection_range:
                        # Calculate the angle from the center (0, 0) to (dx, dy)
                        angle = np.degrees(np.arctan2(dy, dx))

                        # Make sure the angle is between 0 and 360
                        if angle < 0:
                            angle += 360

                        # Calculate the visible angle range for this sensor
                        min_angle = (direction - fov / 2) % 360
                        max_angle = (direction + fov / 2) % 360

                        # Check if the angle is within the fov
                        # Handle the circular nature of angles
                        if min_angle < max_angle:
                            if min_angle <= angle <= max_angle:
                                self.detectable_positions.add((dx, dy))
                        else:  # The angle range wraps around 0 degrees
                            if angle >= min_angle or angle <= max_angle:
                                self.detectable_positions.add((dx, dy))

    def apply_mask(self, detect_map, full_map, x, y):
        """
        Apply the detection mask to the full map
        :param detect_map: The map to store detected positions (2D array)
        :param full_map: The full map (2D array)
        :param x: Current X coordinate of Avatar
        :param y: Current Y coordinate of Avatar
        :return: A 2D array representing the detected map
        """
        # Get the size of the full map
        rows, cols = len(full_map), len(full_map[0])

        # Loop through all detectable positions
        for dx, dy in self.detectable_positions:
            # Calculate the absolute position on the full map
            new_x, new_y = x + dx, y + dy

            # Check if the new position is within the map boundaries
            if 0 <= new_x < rows and 0 <= new_y < cols:
                # Copy the value from the full map to the detected map
                detect_map[new_x][new_y] = full_map[new_x][new_y]

        # Return the updated detected map
        return detect_map


