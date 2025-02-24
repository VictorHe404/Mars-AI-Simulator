import unittest
import numpy as np
import sqlite3
from model.avatar.database import DB_NAME
from model.avatar.sensor import Sensor
from model.avatar.detection_mask import DetectionMask


class TestAvatarSystem(unittest.TestCase):

    def setUp(self):
        """
        Initialize the database and add test data
        """
        # Connect to the database and create tables
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sensor (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                range FLOAT,
                fov INT,
                battery_consumption FLOAT,
                description TEXT,
                direction INT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS AvatarSensor (
                avatar_id TEXT,
                sensor_id TEXT,
                FOREIGN KEY (sensor_id) REFERENCES Sensor(id)
            )
        ''')
        # Insert test sensor
        cursor.execute('''
            INSERT INTO Sensor (id, name, range, fov, battery_consumption, description, direction)
            VALUES ('test-sensor-id', 'Test Sensor', 3.0, 90, 0.5, 'Test Description', 0)
        ''')
        # Link sensor to an avatar
        cursor.execute('''
            INSERT INTO AvatarSensor (avatar_id, sensor_id)
            VALUES ('test-avatar-id', 'test-sensor-id')
        ''')
        conn.commit()
        conn.close()

    def test_sensor_creation_and_save(self):
        """
        Test the creation and saving of a Sensor object
        """
        # Create a Sensor object
        sensor = Sensor(
            name="New Test Sensor",
            range_=10.0,
            fov=120,
            battery_consumption=0.8,
            description="A sensor for testing",
            direction=45
        )
        # Save to database
        sensor.save_to_db()

        # Check if the sensor is saved in the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Sensor WHERE name = ?', (sensor.name,))
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)
        self.assertEqual(result[1], "New Test Sensor")
        self.assertEqual(result[2], 10.0)
        self.assertEqual(result[3], 120)
        self.assertEqual(result[4], 0.8)
        self.assertEqual(result[5], "A sensor for testing")
        self.assertEqual(result[6], 45)

    def test_detection_mask_generate(self):
        """
        Test the generation of detection mask
        """
        detection_mask = DetectionMask('test-avatar-id')
        # Check if the detection mask has been generated
        self.assertTrue(len(detection_mask.detectable_positions) > 0)

    def test_detection_mask_apply(self):
        """
        Test the application of detection mask on a map
        """
        # Create a full map and an empty detection map
        full_map = np.random.randint(0, 10, (10, 10))
        detect_map = np.zeros_like(full_map)
        x, y = 5, 5  # Avatar's current position

        detection_mask = DetectionMask('test-avatar-id')
        detected_map = detection_mask.apply_mask(detect_map, full_map, x, y)

        # Check if at least one position is detected
        self.assertTrue(np.any(detected_map))

    def test_database_connection(self):
        """
        Test the database connection and integrity
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        conn.close()

        # Check if the required tables exist
        required_tables = {'Sensor', 'AvatarSensor'}
        existing_tables = {table[0] for table in tables}
        self.assertTrue(required_tables.issubset(existing_tables))

    def tearDown(self):
        """
        Clean up the database after testing
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS Sensor')
        cursor.execute('DROP TABLE IF EXISTS AvatarSensor')
        conn.commit()
        conn.close()


if __name__ == '__main__':
    unittest.main()
