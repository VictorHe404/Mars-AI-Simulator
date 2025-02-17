import sqlite3

DB_NAME = "avatar.db"

def init_db():
    """初始化数据库，创建 Avatar、Sensor、Avatar-Sensor 关系表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1️⃣ Avatar 表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Avatar (
        id TEXT PRIMARY KEY,  
        name TEXT NOT NULL,
        weight FLOAT,
        material TEXT,
        description TEXT,
        battery_capacity FLOAT,
        battery_efficiency FLOAT,
        battery_consumption_rate FLOAT,
        driving_force FLOAT,
        max_speed FLOAT,
        acceleration FLOAT,
        max_slope FLOAT,
        energy_recharge_rate FLOAT
    )''')

    # 2️⃣ Sensor 表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sensor (
        id TEXT PRIMARY KEY,  
        name TEXT NOT NULL,
        range FLOAT,
        fov INT,
        battery_consumption FLOAT,
        description TEXT,
        direction INT,
        direction_description TEXT  -- 方向描述（如 "Front", "Left", "Right"）
    )''')

    # 3️⃣ Avatar-Sensor 关系表（一个 Avatar 可以有多个 Sensor）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AvatarSensor (
        avatar_id TEXT,
        sensor_id TEXT,
        FOREIGN KEY (avatar_id) REFERENCES Avatar(id),
        FOREIGN KEY (sensor_id) REFERENCES Sensor(id)
    )''')

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# 运行初始化
if __name__ == "__main__":
    init_db()
