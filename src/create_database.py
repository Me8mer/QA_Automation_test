#!/usr/bin/env python3

import os
import sqlite3

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(ROOT_DIR, "db", "ships.db")

def create_database(db_path=DB_PATH):
    # Ensure the db directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create weapons table
    c.execute('''
        CREATE TABLE IF NOT EXISTS weapons (
            weapon TEXT PRIMARY KEY,
            reload_speed INTEGER,
            rotation_speed INTEGER,
            diameter INTEGER,
            power_volley INTEGER,
            count INTEGER
        )
    ''')

    # Create hulls table
    c.execute('''
        CREATE TABLE IF NOT EXISTS hulls (
            hull TEXT PRIMARY KEY,
            armor INTEGER,
            type INTEGER,
            capacity INTEGER
        )
    ''')

    # Create engines table
    c.execute('''
        CREATE TABLE IF NOT EXISTS engines (
            engine TEXT PRIMARY KEY,
            power INTEGER,
            type INTEGER
        )
    ''')

    # Create ships table
    c.execute('''
        CREATE TABLE IF NOT EXISTS ships (
            ship TEXT PRIMARY KEY,
            weapon TEXT,
            hull TEXT,
            engine TEXT,
            FOREIGN KEY (weapon) REFERENCES weapons(weapon),
            FOREIGN KEY (hull) REFERENCES hulls(hull),
            FOREIGN KEY (engine) REFERENCES engines(engine)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database '{db_path}' created with required tables.")

if __name__ == "__main__":
    create_database()
