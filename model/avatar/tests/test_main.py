import unittest
import sqlite3
from model.avatar.database import init_db, DB_NAME
from model.avatar.avatar import Avatar
from model.avatar.sensor import Sensor
from model.avatar.detection_mask import DetectionMask


class TestAvatarSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize a clean database before running tests"""
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DROP TABLE IF EXISTS AvatarSensor")
        conn.execute("DROP TABLE IF EXISTS Avatar")
        conn.execute("DROP TABLE IF EXISTS Sensor")
        conn.commit()
        init_db()

    def setUp(self):
        """Start each test with empty tables"""
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DELETE FROM AvatarSensor")
        conn.execute("DELETE FROM Avatar")
        conn.execute("DELETE FROM Sensor")
        conn.commit()

    def tearDown(self):
        """Ensure no residual data after each test"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Avatar")
        cursor.execute("DELETE FROM Sensor")
        cursor.execute("DELETE FROM AvatarSensor")
        conn.commit()
        conn.close()

    # 📌 **测试数据库连接**
    def test_database_connection(self):
        """Test if database connection is working and tables are correctly initialized"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()

        self.assertIn("Avatar", tables)
        self.assertIn("Sensor", tables)
        self.assertIn("AvatarSensor", tables)

    # 📌 **测试 Avatar 创建**
    def test_avatar_creation(self):
        """Test creation of an Avatar with unique name and ID"""
        avatar = Avatar(name="TestAvatar", weight=50, material="Metal",
                        description="Test Avatar", battery_capacity=1000,
                        battery_consumption_rate=10, driving_force=100,
                        speed=10, energy_recharge_rate=5)

        self.assertIsNotNone(avatar.id)
        self.assertEqual(avatar.name, "TestAvatar")

    # 📌 **测试 Avatar 名称唯一性**
    def test_duplicate_avatar_name(self):
        """Test creating two Avatars with the same name should raise IntegrityError"""
        Avatar(name="DuplicateAvatar", weight=50, material="Metal",
               description="First Avatar", battery_capacity=1000,
               battery_consumption_rate=10, driving_force=100, speed=10,
               energy_recharge_rate=5)

        with self.assertRaises(sqlite3.IntegrityError):
            Avatar(name="DuplicateAvatar", weight=60, material="Plastic",
                   description="Second Avatar", battery_capacity=1200,
                   battery_consumption_rate=12, driving_force=110, speed=12,
                   energy_recharge_rate=6)

    # 📌 **测试 Avatar 删除**
    def test_avatar_deletion(self):
        """Test deleting an Avatar from the database"""
        avatar = Avatar(name="DeleteAvatar", weight=50, material="Metal",
                        description="To be deleted", battery_capacity=1000,
                        battery_consumption_rate=10, driving_force=100,
                        speed=10, energy_recharge_rate=5)

        deleted = Avatar.delete_avatar("DeleteAvatar")
        self.assertTrue(deleted, "Avatar should be deleted successfully")

    # 📌 **测试 Sensor 创建**
    def test_sensor_creation(self):
        """Test creation of a Sensor with unique name and ID"""
        sensor = Sensor(name="TestSensor", range_=10, fov=90, battery_consumption=5,
                        description="Test Sensor", direction=0)

        self.assertIsNotNone(sensor.id)
        self.assertEqual(sensor.name, "TestSensor")

    # 📌 **测试 Sensor 名称唯一性**
    def test_duplicate_sensor_name(self):
        """Test creating two Sensors with the same name should raise IntegrityError"""
        Sensor(name="DuplicateSensor", range_=15, fov=120, battery_consumption=8,
               description="First Sensor", direction=90)

        with self.assertRaises(sqlite3.IntegrityError):
            Sensor(name="DuplicateSensor", range_=20, fov=180, battery_consumption=10,
                   description="Second Sensor", direction=180)

    # 📌 **测试 Avatar 绑定和解绑 Sensor**
    def test_bind_and_unbind_sensor(self):
        """Test binding and unbinding of Sensors to Avatar"""
        avatar = Avatar(name="BindTestAvatar", weight=70, material="Metal",
                        description="Bot for binding test", battery_capacity=2000,
                        battery_consumption_rate=15, driving_force=150,
                        speed=15, energy_recharge_rate=10)

        sensor = Sensor(name="TestBoundSensor", range_=15, fov=120, battery_consumption=8,
                        description="Sensor to bind", direction=90)

        avatar.bind_sensor(sensor)
        sensors = avatar.get_sensors()
        self.assertIn(sensor.id, [s.id for s in sensors])

        avatar.unbind_sensor(sensor)
        sensors_after_unbind = avatar.get_sensors()
        self.assertNotIn(sensor.id, [s.id for s in sensors_after_unbind])

    # 📌 **测试 DetectionMask 生成**
    def test_detection_mask_generation(self):
        """Test DetectionMask generation and accuracy"""
        avatar = Avatar(name="DetectionBot", weight=60, material="Plastic",
                        description="Bot for detection test", battery_capacity=1500,
                        battery_consumption_rate=12, driving_force=120,
                        speed=12, energy_recharge_rate=8)

        sensor = Sensor(name="DetectionSensor", range_=10, fov=180, battery_consumption=6,
                        description="Wide angle sensor", direction=0)
        avatar.bind_sensor(sensor)

        detection_mask = avatar.get_detection_mask()
        self.assertGreater(len(detection_mask.detectable_positions), 0)

    # 📌 **测试 DetectionMask 自动刷新**
    def test_detection_mask_refresh(self):
        """Test auto-refresh of DetectionMask when binding new sensors"""
        avatar = Avatar(name="RefreshBot", weight=65, material="Carbon",
                        description="Bot for refresh test", battery_capacity=1800,
                        battery_consumption_rate=14, driving_force=130,
                        speed=14, energy_recharge_rate=9)

        initial_positions = len(avatar.get_detection_mask().detectable_positions)

        new_sensor = Sensor(name="NewRangeSensor", range_=20, fov=180, battery_consumption=10,
                            description="New sensor to increase range", direction=0)

        avatar.bind_sensor(new_sensor)
        after_bind_positions = len(avatar.get_detection_mask().detectable_positions)

        self.assertTrue(after_bind_positions > initial_positions,
                        "Detection mask should increase after binding a new sensor.")

if __name__ == '__main__':
    unittest.main()
