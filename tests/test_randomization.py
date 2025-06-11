import pytest
import sqlite3

DB_PATH = "../db/ships.db"  # Adjust if needed

def get_ship_data(conn):
    c = conn.cursor()
    c.execute("SELECT ship, weapon, hull, engine FROM ships ORDER BY ship")
    return {row[0]: {"weapon": row[1], "hull": row[2], "engine": row[3]} for row in c.fetchall()}

def get_component_data(conn, table, key_name):
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table}")
    cols = [desc[0] for desc in c.description]
    return {row[0]: dict(zip(cols, row)) for row in c.fetchall()}

def pytest_generate_tests(metafunc):
    if "ship_name" in metafunc.fixturenames and "component" in metafunc.fixturenames:
        # Generate (ship_name, component) for all 200*3
        conn = sqlite3.connect(DB_PATH)
        ships = get_ship_data(conn)
        conn.close()
        argvalues = []
        for ship in ships.keys():
            for component in ["weapon", "hull", "engine"]:
                argvalues.append((ship, component))
        metafunc.parametrize(("ship_name", "component"), argvalues)

@pytest.fixture(scope="session")
def original_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()

@pytest.fixture(scope="session")
def randomized_conn(randomized_db_path):
    conn = sqlite3.connect(randomized_db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()

@pytest.fixture(scope="session")
def mode(pytestconfig):
    return pytestconfig.getoption("mode")

def component_table_and_key(component):
    if component == "weapon":
        return "weapons", "weapon"
    elif component == "hull":
        return "hulls", "hull"
    elif component == "engine":
        return "engines", "engine"
    else:
        raise ValueError(component)

def component_info(conn, component, key):
    table, key_col = component_table_and_key(component)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table} WHERE {key_col}=?", (key,))
    row = c.fetchone()
    if not row:
        return None
    cols = [desc[0] for desc in c.description]
    return dict(zip(cols, row))

def test_ship_component(ship_name, component, original_conn, randomized_conn, mode):
    orig_ships = get_ship_data(original_conn)
    rand_ships = get_ship_data(randomized_conn)

    orig_ship = orig_ships[ship_name]
    rand_ship = rand_ships[ship_name]

    if mode == "a":
        # Check if the component reference changed
        orig_component = orig_ship[component]
        rand_component = rand_ship[component]
        assert orig_component == rand_component, (
            f"\n[Ship: {ship_name}]\n"
            f"{component} changed!\n"
            f"Before: {orig_component}\n"
            f"After:  {rand_component}\n"
            f"Full ship before: {orig_ship}\n"
            f"Full ship after:  {rand_ship}\n"
        )
    elif mode == "b":
        # Check if any parameter of the component changed
        orig_component_name = orig_ship[component]
        rand_component_name = rand_ship[component]
        assert orig_component_name == rand_component_name, (
            f"\n[Ship: {ship_name}]\n"
            f"{component} reference changed (should not in mode b)!\n"
            f"Before: {orig_component_name}\n"
            f"After:  {rand_component_name}\n"
            f"Full ship before: {orig_ship}\n"
            f"Full ship after:  {rand_ship}\n"
        )
        # Now check parameters
        orig_comp_info = component_info(original_conn, component, orig_component_name)
        rand_comp_info = component_info(randomized_conn, component, rand_component_name)
        for key in orig_comp_info:
            if key == component:
                continue  # skip primary key
            if orig_comp_info[key] != rand_comp_info[key]:
                assert False, (
                    f"\n[Ship: {ship_name}] {component} ({orig_component_name})\n"
                    f"Parameter '{key}' changed!\n"
                    f"Before: {orig_comp_info}\n"
                    f"After:  {rand_comp_info}\n"
                )
