import sqlite3
import uuid
from model.avatar.database import DB_NAME

class Sensor:
    def __init__(self, name, range_, fov, battery_consumption, description, direction, sensor_id=None, database_available = True):
        self.id = sensor_id if sensor_id else str(uuid.uuid4())
        self.name = name
        self.range = range_
        self.fov = fov
        self.battery_consumption = battery_consumption
        self.description = description
        self.direction = direction
        self.database_available = database_available

        if self.database_available:
            if sensor_id is None:
                try:
                    self.save_to_db()
                except sqlite3.IntegrityError as e:
                    print(f"Failed to save Sensor: {e}")
                    raise


    def save_to_db(self):

        if self.database_available:
            """
            Save this Sensor to the database as a new record.
            Relies on database UNIQUE constraint to ensure unique name and id.
            """
            query = '''
                INSERT INTO Sensor (id, name, range, fov, battery_consumption, description, direction)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                self.id, self.name, self.range, self.fov,
                self.battery_consumption, self.description, self.direction
            )

            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()

    @staticmethod
    def get_sensor_by_id(sensor_id):
        """
        Retrieve a Sensor by its ID.
        """
        query = "SELECT * FROM Sensor WHERE id = ?"
        params = (sensor_id,)

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()

        if row:
            return Sensor(
                name=row[1],
                range_=row[2],
                fov=row[3],
                battery_consumption=row[4],
                description=row[5],
                direction=row[6],
                sensor_id=row[0]
            )
        return None

    @staticmethod
    def get_all_sensors():
        """
        Retrieve all Sensors from the database.
        """
        query = "SELECT * FROM Sensor"

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        return [Sensor(
            name=row[1],
            range_=row[2],
            fov=row[3],
            battery_consumption=row[4],
            description=row[5],
            direction=row[6],
            sensor_id=row[0]
        ) for row in rows]

    def __repr__(self):
        return f"<Sensor(name={self.name}, range={self.range}, fov={self.fov})>"

    def get_range(self):
        return self.range

    def get_fov(self):
        return self.fov

    def get_battery_consumption(self):
        return self.battery_consumption

    def get_direction(self):
        return self.direction
