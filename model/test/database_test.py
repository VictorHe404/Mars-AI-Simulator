import os
import sqlite3
from model.simulator.Simulator import Simulator
from model.avatar import Avatar

# Define database path relative to script location
DB_NAME = "avatar.db"

# Initialize the simulator
sim = Simulator()

# Add a new Avatar
avatar_name = "TestAvatar"
success = sim.add_avatar(avatar_name)

if success:
    print(f"Avatar '{avatar_name}' added successfully!")
else:
    print(f"Failed to add Avatar '{avatar_name}'.")

# Fetch all avatars to verify
avatars = Avatar.get_all_avatar_names()
print("\nList of Avatars in the database:")
for name in avatars:
    print(name)

# Fetch and display all records from Avatar, Sensor, and AvatarSensor tables.
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

tables = ["Avatar", "Sensor", "AvatarSensor"]

for table in tables:
    print(f"\nFetching data from {table} table:")
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print(f"No data found in {table} table.")

conn.close()
