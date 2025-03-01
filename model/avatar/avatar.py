import sqlite3
import uuid
from model.avatar.database import DB_NAME
from model.avatar.sensor import Sensor
from model.avatar.detection_mask import DetectionMask

class Avatar:
    def __init__(self, name, weight, material, description,
                 battery_capacity, battery_efficiency, battery_consumption_rate,
                 driving_force, max_speed, acceleration, max_slope, energy_recharge_rate,
                 sensors=None, avatar_id=None):
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
        self.battery_efficiency = battery_efficiency
        self.battery_consumption_rate = battery_consumption_rate
        self.driving_force = driving_force
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.max_slope = max_slope
        self.energy_recharge_rate = energy_recharge_rate
        self.sensors = sensors if sensors else []

        if avatar_id is None:
            try:
                self.save_to_db()
            except sqlite3.IntegrityError as e:
                print(f"Failed to save Avatar: {e}")
                raise

            # Initialize detection mask
        self.detection_mask = DetectionMask(self.id)

        # Bind provided sensors to this Avatar
        for sensor in self.sensors:
            self.bind_sensor(sensor)

    def save_to_db(self):
        """
        Save this Avatar to the database as a new record.
        Relies on database UNIQUE constraint to ensure unique name and id.
        """
        query = '''
            INSERT INTO Avatar (id, name, weight, material, description,
                                battery_capacity, battery_efficiency, battery_consumption_rate,
                                driving_force, max_speed, acceleration, max_slope, energy_recharge_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            self.id, self.name, self.weight, self.material, self.description,
            self.battery_capacity, self.battery_efficiency, self.battery_consumption_rate,
            self.driving_force, self.max_speed, self.acceleration, self.max_slope,
            self.energy_recharge_rate
        )

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def bind_sensor(self, sensor):
        """
        Bind a sensor to this Avatar (avoid duplicate binding in AvatarSensor table)
        Automatically refresh the detection mask after binding.
        """
        query = 'SELECT * FROM AvatarSensor WHERE avatar_id=? AND sensor_id=?'
        params = (self.id, sensor.id)

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            existing = cursor.fetchone()

            if not existing:
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
                battery_efficiency=row[6],
                battery_consumption_rate=row[7],
                driving_force=row[8],
                max_speed=row[9],
                acceleration=row[10],
                max_slope=row[11],
                energy_recharge_rate=row[12],
                avatar_id=row[0]
            )
        return None

    def unbind_sensor(self, sensor):
        """
        Unbind a sensor from this Avatar.
        Automatically refresh the detection mask after unbinding.
        """
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

        # Auto-refresh detection mask after unbinding
        if self.detection_mask:
            self.detection_mask.refresh_sensors()
            if hasattr(self, '_sensor_cache'):
                del self._sensor_cache

    def get_sensors(self):
        """
        Retrieve sensors bound to this Avatar from the DB to ensure consistency.
        Cached to prevent redundant DB queries.
        """
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

        # Cache the result
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

    def get_detection_mask(self):
        """
        Refresh and return the detection mask for this Avatar.
        """
        self.detection_mask = DetectionMask(self.id)
        return self.detection_mask

    def get_movable(self, start_elevation, end_elevation):
        """
        Check if this Avatar can move from start to end elevation.
        """
        slope = abs(end_elevation - start_elevation)
        return slope <= self.max_slope

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
        print(f"Battery Efficiency: {self.battery_efficiency}")
        print(f"Battery Consumption Rate: {self.battery_consumption_rate} mAh/km")
        print(f"Driving Force: {self.driving_force} N")
        print(f"Max Speed: {self.max_speed} m/s")
        print(f"Acceleration: {self.acceleration} m/s²")
        print(f"Max Slope: {self.max_slope} degrees")
        print(f"Energy Recharge Rate: {self.energy_recharge_rate} mAh/s")



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
        return self.max_speed
    def get_max_slope(self):
        return self.max_slope
    def get_energy_recharge_rate(self):
        return self.energy_recharge_rate
