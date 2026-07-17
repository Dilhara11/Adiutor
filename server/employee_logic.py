import sqlite3

DB_PATH = "human_resources.db"


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _rows_to_dicts(rows):
    return [dict(row) for row in rows]


def get_employees_by_department(department_id: int):
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM employees WHERE department_id = ?",
            (department_id,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_employees_by_job(job_id: str):
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM employees WHERE job_id = ?",
            (job_id,),
        ).fetchall()
    return _rows_to_dicts(rows)


def insert_employee(employee_data: dict):
    query = """
        INSERT INTO employees (
            employee_id, first_name, last_name, email, phone_number,
            hire_date, salary, job_id, department_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = (
        employee_data.get("employee_id"),
        employee_data.get("first_name"),
        employee_data.get("last_name"),
        employee_data.get("email"),
        employee_data.get("phone_number"),
        employee_data.get("hire_date"),
        employee_data.get("salary"),
        employee_data.get("job_id"),
        employee_data.get("department_id"),
    )

    try:
        with _get_connection() as conn:
            conn.execute(query, values)
            conn.commit()
    except sqlite3.IntegrityError as exc:
        raise ValueError(f"Unable to insert employee: {exc}") from exc

    return {"message": "Employee inserted", "employee_id": employee_data["employee_id"]}


def update_employee(employee_id: int, update_data: dict):
    if not update_data:
        raise ValueError("No fields provided to update")

    fields = []
    values = []
    for key, value in update_data.items():
        fields.append(f"{key} = ?")
        values.append(value)

    values.append(employee_id)
    query = f"UPDATE employees SET {', '.join(fields)} WHERE employee_id = ?"

    try:
        with _get_connection() as conn:
            cursor = conn.execute(query, tuple(values))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.IntegrityError as exc:
        raise ValueError(f"Unable to update employee: {exc}") from exc


def delete_employee(employee_id: int):
    with _get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM employees WHERE employee_id = ?",
            (employee_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
