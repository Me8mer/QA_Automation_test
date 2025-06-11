# QA Automation Test 

##  Setup

1. **Create the database**
   ```bash
   ./src/create_database.py
   ```

2. **Populate it with data**
   ```bash
   ./src/populate_database.py
   ```

---

##  Running the Tests

Tests are located in the `tests/` directory and compare randomized data with the original DB.

### Test Modes:

- `--mode=a`: one component (weapon/hull/engine) is changed per ship
- `--mode=b`: one parameter of each component is changed

### Run tests in mode a:

```bash
pytest tests --mode=a
```

Expected: 200 fails, 400 passes (each ship has one changed component)

---

### Run tests in mode b:

```bash
pytest tests --mode=b
```

Expected: 600 fails (each component's parameter is changed)


##  Notes

- The randomized database is created as a temporary file during the test session.
- Foreign key constraints are enforced.
- Test output includes both original and changed values for clarity.


