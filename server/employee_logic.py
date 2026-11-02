"""All reads and writes to the HR database live here.

Both the REST API (main.py) and the AI tools (gemini_tools.py) call these
functions directly.
"""

import sqlite3
from contextlib import closing

from db import get_connection

# Columns returned for an employee. Job title and department name are joined
# in so answers read naturally ("Sarah - Software Engineer, Engineering").
EMPLOYEE_SELECT = """
    SELECT e.employee_id, e.first_name, e.last_name, e.email, e.phone_number,
           e.hire_date, e.salary, e.job_id, j.job_title,
           e.department_id, d.department_name
    FROM employees e
    LEFT JOIN jobs j ON j.job_id = e.job_id
    LEFT JOIN departments d ON d.department_id = e.department_id
"""

# Only these fields may be changed through an update.
UPDATABLE_FIELDS = {
    "first_name",
    "last_name",
    "email",
    "phone_number",
    "hire_date",
    "salary",
    "job_id",
    "department_id",
}

DEFAULT_LIMIT = 200


def _rows_to_dicts(rows):
    return [dict(row) for row in rows]


def _query(sql: str, params: tuple = ()) -> list[dict]:
    with closing(get_connection()) as conn:
        return _rows_to_dicts(conn.execute(sql, params).fetchall())


def _write(sql: str, params: tuple) -> sqlite3.Cursor:
    with closing(get_connection()) as conn:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor


# ---------- Reads ----------

def get_employees_by_department(department_id: int, limit: int = DEFAULT_LIMIT):
    return _query(
        EMPLOYEE_SELECT + " WHERE e.department_id = ? ORDER BY e.last_name, e.first_name LIMIT ?",
        (department_id, limit),
    )


def get_employees_by_job(job_id: str, limit: int = DEFAULT_LIMIT):
    return _query(
        EMPLOYEE_SELECT + " WHERE e.job_id = ? ORDER BY e.last_name, e.first_name LIMIT ?",
        (job_id, limit),
    )


def get_employee(employee_id: int):
    rows = _query(EMPLOYEE_SELECT + " WHERE e.employee_id = ?", (employee_id,))
    return rows[0] if rows else None


def search_employees(query: str = "", limit: int = DEFAULT_LIMIT):
    """Find employees by part of their first name, last name, full name or email."""
    like = f"%{query.strip()}%"
    return _query(
        EMPLOYEE_SELECT
        + """ WHERE e.first_name LIKE ? OR e.last_name LIKE ? OR e.email LIKE ?
                 OR (e.first_name || ' ' || e.last_name) LIKE ?
              ORDER BY e.last_name, e.first_name LIMIT ?""",
        (like, like, like, like, limit),
    )


def get_employees_hired_between(start_date: str, end_date: str, limit: int = DEFAULT_LIMIT):
    """Dates are YYYY-MM-DD and both ends are included."""
    return _query(
        EMPLOYEE_SELECT + " WHERE e.hire_date BETWEEN ? AND ? ORDER BY e.hire_date DESC LIMIT ?",
        (start_date, end_date, limit),
    )


def list_departments():
    return _query(
        """SELECT d.department_id, d.department_name, COUNT(e.employee_id) AS headcount,
                  ROUND(AVG(e.salary), 2) AS average_salary
           FROM departments d
           LEFT JOIN employees e ON e.department_id = d.department_id
           GROUP BY d.department_id
           ORDER BY d.department_name"""
    )


def list_jobs():
    return _query(
        """SELECT j.job_id, j.job_title, j.min_salary, j.max_salary,
                  COUNT(e.employee_id) AS headcount
           FROM jobs j
           LEFT JOIN employees e ON e.job_id = j.job_id
           GROUP BY j.job_id
           ORDER BY j.job_title"""
    )


def workforce_summary():
    """Numbers for the dashboard sidebar."""
    totals = _query(
        "SELECT COUNT(*) AS total_employees, ROUND(AVG(salary), 2) AS average_salary, "
        "ROUND(SUM(salary), 2) AS total_payroll FROM employees"
    )[0]
    departments = list_departments()
    recent_hires = _query(EMPLOYEE_SELECT + " ORDER BY e.hire_date DESC LIMIT 5")
    return {
        **totals,
        "department_count": len(departments),
        "departments": departments,
        "recent_hires": recent_hires,
    }


# ---------- Writes ----------

def insert_employee(employee_data: dict):
    """Add an employee. If ``employee_id`` is missing, the next free ID is used."""
    columns = [
        "employee_id", "first_name", "last_name", "email", "phone_number",
        "hire_date", "salary", "job_id", "department_id",
    ]
    if employee_data.get("employee_id") is None:
        columns.remove("employee_id")

    values = tuple(employee_data.get(column) for column in columns)
    placeholders = ", ".join("?" for _ in columns)
    query = f"INSERT INTO employees ({', '.join(columns)}) VALUES ({placeholders})"

    try:
        cursor = _write(query, values)
    except sqlite3.IntegrityError as exc:
        raise ValueError(_friendly_integrity_error(exc, "add")) from exc

    return {"message": "Employee added", "employee_id": cursor.lastrowid}


def update_employee(employee_id: int, update_data: dict):
    update_data = {k: v for k, v in update_data.items() if k in UPDATABLE_FIELDS}
    if not update_data:
        raise ValueError("No fields provided to update")

    fields = ", ".join(f"{key} = ?" for key in update_data)
    values = (*update_data.values(), employee_id)

    try:
        cursor = _write(f"UPDATE employees SET {fields} WHERE employee_id = ?", values)
    except sqlite3.IntegrityError as exc:
        raise ValueError(_friendly_integrity_error(exc, "update")) from exc
    return cursor.rowcount > 0


def delete_employee(employee_id: int):
    cursor = _write("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
    return cursor.rowcount > 0


def _friendly_integrity_error(exc: sqlite3.IntegrityError, action: str) -> str:
    text = str(exc)
    if "FOREIGN KEY" in text:
        return (
            f"Unable to {action} employee: the job ID or department ID does not exist. "
            "Check the list of jobs and departments."
        )
    if "UNIQUE" in text:
        return f"Unable to {action} employee: that employee ID is already taken."
    return f"Unable to {action} employee: {text}"
