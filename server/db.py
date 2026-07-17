import sqlite3

# 1. Connect to database
conn = sqlite3.connect('human_resources.db')
cursor = conn.cursor()

# 2. Enable Foreign Key support (disabled by default in SQLite)
cursor.execute('PRAGMA foreign_keys = ON;')

# 3. Create Tables
cursor.executescript('''
    -- Table 1: Jobs
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        job_title TEXT NOT NULL,
        min_salary REAL,
        max_salary REAL
    );

    -- Table 2: Departments
    CREATE TABLE IF NOT EXISTS departments (
        department_id INTEGER PRIMARY KEY,
        department_name TEXT NOT NULL
    );

    -- Table 3: Employees (The Bridge Table)
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone_number TEXT,
        hire_date TEXT,
        salary REAL,
        job_id TEXT,
        department_id INTEGER,
        FOREIGN KEY (job_id) REFERENCES jobs (job_id),
        FOREIGN KEY (department_id) REFERENCES departments (department_id)
    );
''')

# 4. Save and Close
conn.commit()
conn.close()