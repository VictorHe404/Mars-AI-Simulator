import sqlite3

DB_NAME = "avatar.db"

def init_db():
    """
    Initialize the database with the required tables: Avatar, Sensor, and AvatarSensor.
    Ensures unique constraints on id and name for both Avatar and Sensor.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS Avatar")

    # Create Avatar table with UNIQUE name
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Avatar (
            id TEXT PRIMARY KEY,  
            name TEXT UNIQUE NOT NULL,  
            weight FLOAT,
            material TEXT,
            description TEXT,
            battery_capacity FLOAT,
            battery_consumption_rate FLOAT,
            driving_force FLOAT,
            speed FLOAT,
            energy_recharge_rate FLOAT
        )
    ''')

    # Create Sensor table with UNIQUE name
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sensor (
            id TEXT PRIMARY KEY,  
            name TEXT UNIQUE NOT NULL,  
            range FLOAT,
            fov INT,
            battery_consumption FLOAT,
            description TEXT,
            direction INT
        )
    ''')

    # Create AvatarSensor relationship table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AvatarSensor (
            avatar_id TEXT,
            sensor_id TEXT,
            FOREIGN KEY (avatar_id) REFERENCES Avatar(id) ON DELETE CASCADE,
            FOREIGN KEY (sensor_id) REFERENCES Sensor(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
