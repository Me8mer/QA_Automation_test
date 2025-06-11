import pytest
import shutil
import sqlite3
import random
import os

# Add --mode option to pytest
def pytest_addoption(parser):
    parser.addoption(
        "--mode",
        action="store",
        default="a",
        choices=["a", "b"],
        help="Randomization mode: a (change one component per ship) or b (change one parameter per component)"
    )

# Session-scoped fixture for randomized DB
@pytest.fixture(scope="session")
def randomized_db_path(pytestconfig, tmp_path_factory):
    # Path to the original DB
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    original_db = os.path.join(ROOT_DIR, "db", "ships.db")

    if not os.path.exists(original_db):
        raise FileNotFoundError(f"Original DB not found at: {original_db}")

    # Create a temp DB file
    temp_dir = tmp_path_factory.mktemp("db")
    temp_db = temp_dir / "randomized.db"
    shutil.copy2(original_db, temp_db)

    # Randomize the temp DB according to the mode
    mode = pytestconfig.getoption("mode")

    conn = sqlite3.connect(temp_db)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    if mode == "a":
        # For each ship, change one component to a random other one (hull, weapon, or engine)
        # Gather all possible components
        c.execute("SELECT weapon FROM weapons")
        weapons = [row[0] for row in c.fetchall()]
        c.execute("SELECT hull FROM hulls")
        hulls = [row[0] for row in c.fetchall()]
        c.execute("SELECT engine FROM engines")
        engines = [row[0] for row in c.fetchall()]

        c.execute("SELECT ship, weapon, hull, engine FROM ships")
        ships = c.fetchall()
        for ship, weapon, hull, engine in ships:
            component_to_change = random.choice(["weapon", "hull", "engine"])
            if component_to_change == "weapon":
                new_value = random.choice([w for w in weapons if w != weapon])
                c.execute("UPDATE ships SET weapon=? WHERE ship=?", (new_value, ship))
            elif component_to_change == "hull":
                new_value = random.choice([h for h in hulls if h != hull])
                c.execute("UPDATE ships SET hull=? WHERE ship=?", (new_value, ship))
            elif component_to_change == "engine":
                new_value = random.choice([e for e in engines if e != engine])
                c.execute("UPDATE ships SET engine=? WHERE ship=?", (new_value, ship))
        conn.commit()

    elif mode == "b":
        # For each ship, change one random parameter of each component to a random value
        # First get all ships and their linked components
        c.execute("SELECT ship, weapon, hull, engine FROM ships")
        ships = c.fetchall()
        for ship, weapon, hull, engine in ships:
            # Weapons
            c.execute("PRAGMA table_info(weapons)")
            weapon_cols = [row[1] for row in c.fetchall() if row[1] != "weapon"]
            param = random.choice(weapon_cols)
            new_value = random.randint(1, 20)
            c.execute(f"UPDATE weapons SET {param}=? WHERE weapon=?", (new_value, weapon))
            # Hulls
            c.execute("PRAGMA table_info(hulls)")
            hull_cols = [row[1] for row in c.fetchall() if row[1] != "hull"]
            param = random.choice(hull_cols)
            new_value = random.randint(1, 20)
            c.execute(f"UPDATE hulls SET {param}=? WHERE hull=?", (new_value, hull))
            # Engines
            c.execute("PRAGMA table_info(engines)")
            engine_cols = [row[1] for row in c.fetchall() if row[1] != "engine"]
            param = random.choice(engine_cols)
            new_value = random.randint(1, 20)
            c.execute(f"UPDATE engines SET {param}=? WHERE engine=?", (new_value, engine))
        conn.commit()

    conn.close()
    return str(temp_db)
