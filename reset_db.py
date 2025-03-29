import os
import sqlite3
from model.avatar.database import DB_NAME, init_db

def reset_database():
    """
    Delete the existing database file and reinitialize the database.
    """
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Deleted existing database: {DB_NAME}")

    init_db()
    print("Database has been reset.")

if __name__ == "__main__":
    reset_database()
