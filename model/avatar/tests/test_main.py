import unittest
import sqlite3
from model.avatar.database import init_db, DB_NAME
from model.avatar.avatar import Avatar
from model.avatar.sensor import Sensor
from model.avatar.detection_mask import DetectionMask


# tests/test_main.py
class TestAvatarSys(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Wipe database completely before test suite
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DROP TABLE IF EXISTS AvatarSensor")
        conn.execute("DROP TABLE IF EXISTS Avatar")
        conn.execute("DROP TABLE IF EXISTS Sensor")
        conn.commit()
        init_db()

    def setUp(self):
        # Start each test with empty tables
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DELETE FROM AvatarSensor")
        conn.execute("DELETE FROM Avatar")
        conn.execute("DELETE FROM Sensor")
        conn.commit()



    def tearDown(self):
        """
        Ensure no residual data after each test.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Avatar')
        cursor.execute('DELETE FROM Sensor')
        cursor.execute('DELETE FROM AvatarSensor')
        conn.commit()
        conn.close()

    def test_database_connection(self):
        """
        Test if database connection is working and tables are correctly initialized.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        self.assertIn("Avatar", tables)
        self.assertIn("Sensor", tables)
        self.assertIn("AvatarSensor", tables)

    def test_avatar_creation(self):
        """
        Test creation of an Avatar with unique name and ID.
        """
        avatar = Avatar(name="UniqueAvatar", weight=50, material="Metal",
                        description="A test avatar", battery_capacity=1000,
                        battery_efficiency=0.8, battery_consumption_rate=10,
                        driving_force=100, max_speed=10, acceleration=2,
                        max_slope=30, energy_recharge_rate=5)
        self.assertIsNotNone(avatar.id)
        self.assertEqual(avatar.name, "UniqueAvatar")

    def test_duplicate_avatar_name(self):
        avatar1 = Avatar(
            name="DuplicateAvatar", weight=50, material="Metal",
            description="First instance", battery_capacity=1000,
            battery_efficiency=0.8, battery_consumption_rate=10,
            driving_force=100, max_speed=10, acceleration=2,
            max_slope=30, energy_recharge_rate=5
        )

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Avatar WHERE name=?", ("DuplicateAvatar",))
        result = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(result, "第一个 Avatar 未正确插入数据库")

        with self.assertRaises(sqlite3.IntegrityError):
            Avatar(
                name="DuplicateAvatar", weight=60, material="Plastic",
                description="Second instance", battery_capacity=1200,
                battery_efficiency=0.85, battery_consumption_rate=12,
                driving_force=110, max_speed=12, acceleration=3,
                max_slope=35, energy_recharge_rate=6
            )

    def test_sensor_creation(self):
        """
        Test creation of a Sensor with unique name and ID.
        """
        sensor = Sensor(name="UniqueSensor", range_=10, fov=90, battery_consumption=5,
                        description="A test sensor", direction=0)
        self.assertIsNotNone(sensor.id)
        self.assertEqual(sensor.name, "UniqueSensor")

    def test_duplicate_sensor_name(self):
        """
        Test creation of two Sensors with the same name, should raise IntegrityError.
        """
        Sensor(name="DuplicateSensor", range_=15, fov=120, battery_consumption=8,
               description="First sensor", direction=90)

        with self.assertRaises(sqlite3.IntegrityError):
            Sensor(name="DuplicateSensor", range_=20, fov=180, battery_consumption=10,
                   description="Second sensor", direction=180)

    def test_bind_and_unbind_sensor(self):
        """
        Test binding and unbinding of Sensors to Avatar.
        """
        avatar = Avatar(name="BindTestBot", weight=70, material="Metal",
                        description="Bot for binding test", battery_capacity=2000,
                        battery_efficiency=0.9, battery_consumption_rate=15,
                        driving_force=150, max_speed=15, acceleration=3,
                        max_slope=35, energy_recharge_rate=10)
        sensor = Sensor(name="BoundSensor", range_=15, fov=120, battery_consumption=8,
                        description="Sensor to bind", direction=90)
        avatar.bind_sensor(sensor)
        sensors = avatar.get_sensors()
        self.assertIn(sensor.id, [s.id for s in sensors])

        avatar.unbind_sensor(sensor)
        sensors_after_unbind = avatar.get_sensors()
        self.assertNotIn(sensor.id, [s.id for s in sensors_after_unbind])

    def test_detection_mask(self):
        """
        Test DetectionMask generation and accuracy.
        """
        avatar = Avatar(name="DetectionBot", weight=60, material="Plastic",
                        description="Bot for detection test", battery_capacity=1500,
                        battery_efficiency=0.85, battery_consumption_rate=12,
                        driving_force=120, max_speed=12, acceleration=2.5,
                        max_slope=25, energy_recharge_rate=8)
        sensor = Sensor(name="DetectionSensor", range_=10, fov=180, battery_consumption=6,
                        description="Wide angle sensor", direction=0)
        avatar.bind_sensor(sensor)
        detection_mask = avatar.get_detection_mask()
        self.assertGreater(len(detection_mask.detectable_positions), 0)

    def test_detection_mask_refresh(self):
        """
        Test auto-refresh of DetectionMask when binding new sensors.
        """
        avatar = Avatar(name="RefreshBot", weight=65, material="Carbon",
                        description="Bot for refresh test", battery_capacity=1800,
                        battery_efficiency=0.88, battery_consumption_rate=14,
                        driving_force=130, max_speed=14, acceleration=2.8,
                        max_slope=28, energy_recharge_rate=9)
        initial_positions = len(avatar.get_detection_mask().detectable_positions)

        new_sensor = Sensor(name="New Range Sensor", range_=20, fov=180, battery_consumption=10,
                            description="New sensor to increase range", direction=0)
        avatar.bind_sensor(new_sensor)

        after_bind_positions = len(avatar.get_detection_mask().detectable_positions)
        self.assertTrue(after_bind_positions > initial_positions,
                        "After binding a sensor, detection positions should increase.")


if __name__ == '__main__':
    unittest.main()
