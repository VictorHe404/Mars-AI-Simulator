import sqlite3
import numpy as np
from model.avatar.database import DB_NAME
from model.avatar.sensor import Sensor

class DetectionMask:
    def __init__(self, avatar_id, database_available=True):
        """
        Initialize DetectionMask for a specific Avatar.
        :param avatar_id: The ID of the Avatar for which the detection mask is calculated.
        """
        self.avatar_id = avatar_id
        self.detectable_positions = set()
        self.database_available = database_available

        if self.database_available:
            self.sensors = self.get_sensors()
            self.generate_mask()

    def get_sensors(self):
        """
        Query the database to get all sensors bound to this Avatar.
        :return: List of Sensor objects.
        """
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, range, fov, battery_consumption, description, direction
                    FROM Sensor
                    JOIN AvatarSensor ON Sensor.id = AvatarSensor.sensor_id
                    WHERE AvatarSensor.avatar_id = ?
                ''', (self.avatar_id,))
                rows = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching sensors for Avatar ID = {self.avatar_id}: {e}")
            return []

        return [
            Sensor(
                name=row[1],
                range_=row[2],
                fov=row[3],
                battery_consumption=row[4],
                description=row[5],
                direction=row[6],
                sensor_id=row[0]
            ) for row in rows
        ]

    def generate_mask(self):
        """
        Generate the detection mask based on sensors' range, field of view, and direction.
        All detectable positions (dx, dy) are stored in self.detectable_positions.
        """
        self.detectable_positions.clear()
        for sensor in self.sensors:
            detection_range = int(sensor.get_range())
            fov = sensor.get_fov()
            direction = sensor.get_direction()

            for dx in range(-detection_range, detection_range + 1):
                for dy in range(-detection_range, detection_range + 1):
                    distance = np.sqrt(dx ** 2 + dy ** 2)
                    if distance <= detection_range:
                        angle = np.degrees(np.arctan2(dy, dx)) % 360

                        min_angle = (direction - fov / 2) % 360
                        max_angle = (direction + fov / 2) % 360

                        if min_angle < max_angle:
                            in_fov = min_angle <= angle <= max_angle
                        else:
                            in_fov = angle >= min_angle or angle <= max_angle

                        if in_fov:
                            self.detectable_positions.add((dx, dy))

    def apply_mask(self, detect_map, full_map, x, y):
        """
        Apply the detection mask to the full map, updating detect_map.
        :param detect_map: 2D array to store detection results.
        :param full_map: The full 2D map array.
        :param x: The Avatar's current X coordinate.
        :param y: The Avatar's current Y coordinate.
        :return: The updated detect_map.
        """
        rows, cols = len(full_map), len(full_map[0])

        for dx, dy in self.detectable_positions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < rows and 0 <= new_y < cols:
                if full_map[new_x][new_y] is not None:
                    detect_map[new_x][new_y] = full_map[new_x][new_y]

        return detect_map

    def refresh_sensors(self):
        """
        Refresh the sensor list by re-querying the database and regenerating the mask.
        This should be called when sensors are bound or unbound.
        """
        if self.database_available:
            self.sensors = self.get_sensors()
            self.generate_mask()

    def refresh_sensors_without_database(self, sensor_list):
        """
        Refresh sensors manually without using the database.
        :param sensor_list: List of Sensor objects.
        """
        self.sensors = sensor_list
        self.generate_mask()
