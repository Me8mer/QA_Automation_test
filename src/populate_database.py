#!/usr/bin/env python3

import os
import sqlite3
import random
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(ROOT_DIR, "db", "ships.db")

def random_values(n):
    return [random.randint(1, 20) for _ in range(n)]

def populate_database(db_path=DB_PATH):
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' does not exist. Run create_database.py first.")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    # Populate weapons
    for i in range(1, 21):
        name = f"Weapon-{i}"
        values = random_values(5)
        c.execute('''
            INSERT INTO weapons (weapon, reload_speed, rotation_speed, diameter, power_volley, count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, *values))

    # Populate hulls
    for i in range(1, 6):
        name = f"Hull-{i}"
        values = random_values(3)
        c.execute('''
            INSERT INTO hulls (hull, armor, type, capacity)
            VALUES (?, ?, ?, ?)
        ''', (name, *values))

    # Populate engines
    for i in range(1, 7):
        name = f"Engine-{i}"
        values = random_values(2)
        c.execute('''
            INSERT INTO engines (engine, power, type)
            VALUES (?, ?, ?)
        ''', (name, *values))

    # Get existing foreign key values
    c.execute("SELECT weapon FROM weapons")
    weapons = [row[0] for row in c.fetchall()]

    c.execute("SELECT hull FROM hulls")
    hulls = [row[0] for row in c.fetchall()]

    c.execute("SELECT engine FROM engines")
    engines = [row[0] for row in c.fetchall()]

    # Populate ships
    for i in range(1, 201):
        name = f"Ship-{i}"
        weapon = random.choice(weapons)
        hull = random.choice(hulls)
        engine = random.choice(engines)
        c.execute('''
            INSERT INTO ships (ship, weapon, hull, engine)
            VALUES (?, ?, ?, ?)
        ''', (name, weapon, hull, engine))

    conn.commit()
    conn.close()
    print(f"Database '{db_path}' populated with test data.")

if __name__ == "__main__":
    populate_database()
