import math
import os
import sqlite3
import uuid

from plotly.validators.layout.slider.transition import DurationValidator

from model.avatar.database import DB_NAME
from model.avatar.sensor import Sensor
from model.avatar.detection_mask import DetectionMask


class Avatar:
    def __init__(self, name, weight, material, description,
                 battery_capacity, battery_consumption_rate,
                 driving_force, speed, energy_recharge_rate,
                 sensors=None, avatar_id=None, database_available=True):
        """
        Initialize Avatar without checking for duplicates.
        Relies on database UNIQUE constraint to enforce unique id and name.
        """
        # Generate unique ID if not provided
        self.id = avatar_id if avatar_id else str(uuid.uuid4())
        self.name = name
        self.weight = weight
        self.material = material
        self.description = description
        self.battery_capacity = battery_capacity
        self.battery_consumption_rate = battery_consumption_rate
        self.driving_force = driving_force
        self.speed = speed
        self.max_slope = -1
        self.energy_recharge_rate = energy_recharge_rate
        self.sensors = sensors if sensors else []
        self.database_available = database_available

        if self.database_available:
            if avatar_id is None:
                try:
                    self.save_to_db()
                except sqlite3.IntegrityError as e:
                    print(f"Failed to save Avatar: {e}")
                    raise

        # Initialize detection mask
        self.detection_mask = DetectionMask(self.id, database_available)

        # Bind provided sensors to this Avatar
        if self.database_available:
            for sensor in self.sensors:
                self.bind_sensor(sensor)

    def save_to_db(self):
        """
        Save this Avatar to the database as a new record.
        """
        print(DB_NAME)
        if os.path.exists(DB_NAME):
            print(f"Database found: {DB_NAME}")
        if self.database_available:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Avatar'")
                result = cursor.fetchone()
                print("Table exists:", result)

            print("11")
            query = '''
                INSERT INTO Avatar (id, name, weight, material, description,
                                    battery_capacity, battery_consumption_rate,
                                    driving_force, speed, energy_recharge_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                str(self.id),  # Ensure ID is a string
                str(self.name),  # Ensure Name is a string
                float(self.weight) if self.weight is not None else None,  # Ensure float or None
                str(self.material),  # Ensure Material is a string
                str(self.description),  # Ensure Description is a string
                float(self.battery_capacity) if self.battery_capacity is not None else None,
                float(self.battery_consumption_rate) if self.battery_consumption_rate is not None else None,
                float(self.driving_force) if self.driving_force is not None else None,
                float(self.speed) if self.speed is not None else None,
                float(self.energy_recharge_rate) if self.energy_recharge_rate is not None else None
            )
            print(query)

            # Labels for each attribute
            attributes = [
                "ID", "Name", "Weight", "Material", "Description",
                "Battery Capacity", "Battery Consumption Rate",
                "Driving Force", "Speed", "Energy Recharge Rate"
            ]

            # Print in a formatted way
            print("Avatar Characteristics:")
            for attr, value in zip(attributes, params):
                print(f"{attr}: {value}")

            with sqlite3.connect(DB_NAME) as conn:
                print("22")
                cursor = conn.cursor()
                print("44")
                cursor.execute(query, params)
                print("55")
                conn.commit()
                print("33")

    @staticmethod
    def get_all_avatar_names():
        """
        Retrieve a list of all Avatar names stored in the database.
        """
        query = "SELECT name FROM Avatar"
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        return [row[0] for row in rows]

    @staticmethod
    def delete_avatar(name):
        """
        Delete an Avatar from the database by name and remove all its sensor bindings.
        """
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM Avatar WHERE name = ?", (name,))
            row = cursor.fetchone()

            if not row:
                print(f"Avatar '{name}' not found in database.")
                return False

            avatar_id = row[0]

            cursor.execute("DELETE FROM AvatarSensor WHERE avatar_id = ?", (avatar_id,))

            cursor.execute("DELETE FROM Avatar WHERE id = ?", (avatar_id,))
            conn.commit()

        print(f"Avatar '{name}' and its sensor bindings deleted.")
        return True

    @staticmethod
    def get_avatar_by_name(name):
        print(DB_NAME)
        """
        Retrieve an Avatar instance from the database by name.
        :param name: The unique name of the Avatar.
        :return: Avatar instance if found, else None.
        """
        query = "SELECT * FROM Avatar WHERE name = ?"
        print("1")
        if os.path.exists(DB_NAME):
            print(f"Database found: {DB_NAME}")
        with sqlite3.connect(DB_NAME) as conn:
            print("3")
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            row = cursor.fetchone()
        print("2")
        if row:
            return Avatar(
                name=row[1], weight=row[2], material=row[3], description=row[4],
                battery_capacity=row[5], battery_consumption_rate=row[6],
                driving_force=row[7], speed=row[8], energy_recharge_rate=row[9],
                avatar_id=row[0]
            )
        return None

    @staticmethod
    def get_avatar_by_id(avatar_id):
        """
        Retrieve an Avatar by its ID.
        """
        query = "SELECT * FROM Avatar WHERE id = ?"
        params = (avatar_id,)

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()

        if row:
            return Avatar(
                name=row[1],
                weight=row[2],
                material=row[3],
                description=row[4],
                battery_capacity=row[5],
                battery_consumption_rate=row[6],
                driving_force=row[7],
                speed=row[8],
                energy_recharge_rate=row[9],
                avatar_id=row[0]
            )
        return None



    def bind_sensor(self, sensor):
        """
        Bind a sensor to this Avatar (avoid duplicate binding in AvatarSensor table).
        Automatically refresh the detection mask after binding.
        """
        if self.database_available:
            query = 'SELECT COUNT(*) FROM AvatarSensor WHERE avatar_id=? AND sensor_id=?'
            params = (self.id, sensor.id)

            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                exists = cursor.fetchone()[0] > 0  # Check if it already exists

                if not exists:
                    cursor.execute('''
                        INSERT INTO AvatarSensor (avatar_id, sensor_id) VALUES (?,?)
                    ''', (self.id, sensor.id))
                    conn.commit()
                    print(f"Sensor '{sensor.name}' bound to Avatar '{self.name}'.")
                else:
                    print(f"Sensor '{sensor.name}' already bound to Avatar '{self.name}'. Skipping.")

            # Auto-refresh detection mask after binding
            if self.detection_mask:
                self.detection_mask.refresh_sensors()
        else:
            if not any(s.id == sensor.id for s in self.sensors):
                self.sensors.append(sensor)
                print(f"Sensor '{sensor.name}' added to Avatar '{self.name}'.")
            else:
                print(f"Sensor '{sensor.name}' is already assigned to Avatar '{self.name}'.")

            if self.detection_mask:
                self.detection_mask.refresh_sensors_without_database(self.sensors)

    def unbind_sensor(self, sensor):
        """
        Unbind a sensor from this Avatar.
        Automatically refresh the detection mask after unbinding.
        """
        if self.database_available:
            query = '''
                DELETE FROM AvatarSensor WHERE avatar_id=? AND sensor_id=?
            '''
            params = (self.id, sensor.id)

            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()

            self.sensors = [s for s in self.sensors if s.id != sensor.id]
            print(f"Sensor '{sensor.name}' unbound from Avatar '{self.name}'.")

            if self.detection_mask:
                self.detection_mask.refresh_sensors()
                if hasattr(self, '_sensor_cache'):
                    del self._sensor_cache
        else:
            self.sensors = [s for s in self.sensors if s.id != sensor.id]
            print(f"Sensor '{sensor.name}' unbound from Avatar '{self.name}'.")
            if self.detection_mask:
                self.detection_mask.refresh_sensors_without_database(self.sensors)



    def calculate_max_slope_difference(self, friction, gravity, distance):
        if self.driving_force <= 0 or self.weight <= 0:
            return 0

        normal_force = self.weight * gravity

        max_slope_radians = math.atan((self.driving_force - friction * normal_force) / normal_force)

        max_slope_degrees = math.degrees(max_slope_radians)

        max_elevation_difference = distance * math.tan(max_slope_radians)

        self.max_slope = max_elevation_difference
    def get_movable(self, start_elevation, end_elevation):
        """
        Check if this Avatar can move from start to end elevation.
        """
        elevation_difference = abs(end_elevation - start_elevation)
        return elevation_difference <= self.max_slope

    def calculate_time_per_grid(self):
        return math.ceil(10/self.speed)

    def get_sensors(self):

        """
        Retrieve sensors bound to this Avatar from the DB to ensure consistency.
        Cached to prevent redundant DB queries.
        """

        if self.database_available:
            # Use cache if available
            if hasattr(self, '_sensor_cache'):
                return self._sensor_cache

            query = '''
                SELECT id, name, range, fov, battery_consumption, description, direction
                FROM Sensor
                JOIN AvatarSensor ON Sensor.id = AvatarSensor.sensor_id
                WHERE AvatarSensor.avatar_id = ?
            '''
            params = (self.id,)

            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Failed to retrieve sensors for Avatar ID = {self.id}: {e}")
                return []

            self._sensor_cache = [Sensor(
                name=row[1],
                range_=row[2],
                fov=row[3],
                battery_consumption=row[4],
                description=row[5],
                direction=row[6],
                sensor_id=row[0]
            ) for row in rows]

            return self._sensor_cache
        else:
            return []

    def get_detection_mask(self):
        """
        Refresh and return the detection mask for this Avatar.
        """
        if self.database_available:
            self.detection_mask = DetectionMask(self.id)
        return self.detection_mask

    def print_avatar(self):
        """
        Print the avatar's basic information.
        """
        print(f"Avatar ID: {self.id}")
        print(f"Name: {self.name}")
        print(f"Weight: {self.weight} kg")
        print(f"Material: {self.material}")
        print(f"Description: {self.description}")
        print(f"Battery Capacity: {self.battery_capacity} mAh")
        print(f"Battery Consumption Rate: {self.battery_consumption_rate} mAh/m")
        print(f"Driving Force: {self.driving_force} N")
        print(f"Max Speed: {self.speed} m/s")
        print(f"Max Slope: {self.max_slope} degrees")
        print(f"Energy Recharge Rate: {self.energy_recharge_rate} mAh/s")

    @classmethod
    def get_default_avatar(cls, avatar_name):
        """
        Returns a default Avatar instance with a unique sensor name based on the avatar name.
        This prevents name collisions for sensors when multiple avatars are created.
        """
        radar_sensor = Sensor(
            name=f"{avatar_name}_Radar-360",
            range_=5,
            fov=360,
            battery_consumption=2,
            description=f"Radar sensor for {avatar_name}, providing 360-degree vision.",
            direction=0,
            database_available=False
        )

        return cls(
            name=avatar_name,
            weight=80,
            material="Titanium Alloy",
            description=f"A high-endurance avatar named {avatar_name} for Mars exploration.",
            battery_capacity=200,
            battery_consumption_rate=5,
            driving_force=280,
            speed=1,
            energy_recharge_rate=20,
            sensors=[radar_sensor],
            database_available=False
        )

    def get_name(self):
        return self.name
    def get_weight(self):
        return self.weight
    def get_battery_capacity(self):
        return self.battery_capacity
    def get_battery_consumption_rate(self):
        return self.battery_consumption_rate
    def get_driving_force(self):
        return self.driving_force
    def get_max_speed(self):
        return self.speed
    def get_max_slope(self):
        return self.max_slope
    def get_energy_recharge_rate(self):
        return self.energy_recharge_rate

