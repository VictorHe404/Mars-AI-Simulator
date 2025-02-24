import sqlite3
import uuid
from model.avatar.database import DB_NAME

class Sensor:
    def __init__(self, name, range_, fov, battery_consumption, description, direction, sensor_id=None):
        """
        Initialize Sensor
        :param name: Name of the sensor
        :param range_: Detection range of the sensor (float)
        :param fov: Field of view (FOV) of the sensor (int)
        :param battery_consumption: Battery consumption per usage (float)
        :param description: Description of the sensor
        :param direction: Direction of the sensor (int, 0-360 degrees)
        :param sensor_id: Unique ID of the sensor (optional, UUID generated if not provided)
        """
        # Generate a unique ID if not provided
        self.id = sensor_id if sensor_id else str(uuid.uuid4())
        self.name = name
        self.range = range_
        self.fov = fov
        self.battery_consumption = battery_consumption
        self.description = description
        self.direction = direction

    def save_to_db(self):
        """ Save the sensor to the database """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Sensor (id, name, range, fov, battery_consumption, description, direction)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.id, self.name, self.range, self.fov, self.battery_consumption, self.description, self.direction))
        conn.commit()
        conn.close()

    @staticmethod
    def get_sensor_by_id(sensor_id):
        """ Get a sensor by its ID """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Sensor WHERE id = ?", (sensor_id,))
        sensor_data = cursor.fetchone()
        conn.close()
        if sensor_data:
            return Sensor(*sensor_data[1:], sensor_id=sensor_data[0])
        return None

    @staticmethod
    def get_all_sensors():
        """ Get all sensors from the database """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Sensor")
        sensors = cursor.fetchall()
        conn.close()
        return [Sensor(*sensor[1:], sensor_id=sensor[0]) for sensor in sensors]

    def get_range(self):
        """ Return the range of the sensor """
        return self.range

    def get_fov(self):
        """ Return the field of view (FOV) of the sensor """
        return self.fov

    def get_battery_consumption(self):
        """ Return the battery consumption of the sensor """
        return self.battery_consumption

    def get_direction(self):
        """ Return the direction of the sensor """
        return self.direction


