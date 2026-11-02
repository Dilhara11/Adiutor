"""Database setup for Adiutor.

The app calls ``init_db()`` automatically when it starts, so you no longer
have to run this file by hand. You can still run it directly:

    python db.py          # create tables + default departments and jobs
    python db.py --demo   # ...and also add a few sample employees
"""

import os
import sqlite3
import sys
from contextlib import closing

# Always keep the database next to this file, no matter which folder the
# server is started from.
DB_PATH = os.getenv(
    "HR_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "human_resources.db"),
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    job_title TEXT NOT NULL,
    min_salary REAL,
    max_salary REAL
);

CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL
);

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

-- Indexes make "employees in department X / with job Y" lookups fast
-- instead of scanning every row.
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees (department_id);
CREATE INDEX IF NOT EXISTS idx_employees_job ON employees (job_id);
CREATE INDEX IF NOT EXISTS idx_employees_hire_date ON employees (hire_date);
"""

DEFAULT_DEPARTMENTS = [
    (10, "Administration"),
    (20, "Marketing"),
    (30, "Sales"),
    (40, "Human Resources"),
    (50, "Engineering"),
    (60, "Finance"),
    (70, "Customer Support"),
]

DEFAULT_JOBS = [
    ("AD_ASST", "Administrative Assistant", 30000, 50000),
    ("MK_MGR", "Marketing Manager", 60000, 110000),
    ("MK_REP", "Marketing Specialist", 40000, 70000),
    ("SA_MAN", "Sales Manager", 65000, 120000),
    ("SA_REP", "Sales Representative", 35000, 75000),
    ("HR_REP", "HR Specialist", 40000, 75000),
    ("HR_MGR", "HR Manager", 65000, 115000),
    ("IT_PROG", "Software Engineer", 60000, 140000),
    ("IT_MGR", "Engineering Manager", 100000, 180000),
    ("FI_ACCOUNT", "Accountant", 45000, 85000),
    ("FI_MGR", "Finance Manager", 80000, 140000),
    ("CS_REP", "Support Agent", 30000, 55000),
]

DEMO_EMPLOYEES = [
    ("Amara", "Perera", "amara.perera@example.com", "+94 77 123 4567", "2022-03-14", 98000, "HR_MGR", 40),
    ("Nimal", "Silva", "nimal.silva@example.com", "+94 71 234 5678", "2023-07-01", 52000, "HR_REP", 40),
    ("Sarah", "Johnson", "sarah.johnson@example.com", "+1 555 0101", "2021-11-08", 125000, "IT_PROG", 50),
    ("David", "Kim", "david.kim@example.com", "+1 555 0102", "2024-02-19", 88000, "IT_PROG", 50),
    ("Priya", "Nair", "priya.nair@example.com", "+91 98 1234 5678", "2020-05-25", 160000, "IT_MGR", 50),
    ("Lucas", "Martin", "lucas.martin@example.com", "+33 6 12 34 56 78", "2023-09-11", 61000, "SA_REP", 30),
    ("Emma", "Brown", "emma.brown@example.com", "+44 7700 900123", "2019-01-07", 104000, "SA_MAN", 30),
    ("Kasun", "Fernando", "kasun.fernando@example.com", "+94 76 345 6789", "2025-06-02", 47000, "MK_REP", 20),
    ("Olivia", "Garcia", "olivia.garcia@example.com", "+1 555 0103", "2022-10-17", 72000, "FI_ACCOUNT", 60),
    ("Ahmed", "Hassan", "ahmed.hassan@example.com", "+971 50 123 4567", "2025-09-15", 41000, "CS_REP", 70),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(with_demo_data: bool = False) -> None:
    """Create tables/indexes and add default departments and jobs if empty."""
    with closing(get_connection()) as conn:
        # WAL mode lets people read while someone else is writing.
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.executescript(SCHEMA)

        if conn.execute("SELECT COUNT(*) FROM departments").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO departments (department_id, department_name) VALUES (?, ?)",
                DEFAULT_DEPARTMENTS,
            )
        if conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES (?, ?, ?, ?)",
                DEFAULT_JOBS,
            )
        if with_demo_data and conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0:
            conn.executemany(
                """INSERT INTO employees (first_name, last_name, email, phone_number,
                                          hire_date, salary, job_id, department_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                DEMO_EMPLOYEES,
            )
        conn.commit()


if __name__ == "__main__":
    demo = "--demo" in sys.argv
    init_db(with_demo_data=demo)
    print(f"Database ready at {DB_PATH}" + (" (with demo employees)" if demo else ""))
