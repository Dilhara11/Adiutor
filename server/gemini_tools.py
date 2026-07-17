import os

from google.genai import types
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")


def _request(method: str, path: str, payload: dict | None = None):
    url = f"{API_BASE_URL}{path}"
    response = requests.request(method, url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def get_employees_by_department(department_id: int):
    return _request("GET", f"/employees/department/{department_id}")


def get_employees_by_job(job_id: str):
    return _request("GET", f"/employees/job/{job_id}")


def create_employee(
    employee_id: int,
    job_id: str,
    department_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    phone_number: str | None = None,
    hire_date: str | None = None,
    salary: float | None = None,
):
    payload = {
        "employee_id": employee_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone_number": phone_number,
        "hire_date": hire_date,
        "salary": salary,
        "job_id": job_id,
        "department_id": department_id,
    }
    return _request("POST", "/employees", payload)


def edit_employee(
    employee_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    phone_number: str | None = None,
    hire_date: str | None = None,
    salary: float | None = None,
    job_id: str | None = None,
    department_id: int | None = None,
):
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone_number": phone_number,
        "hire_date": hire_date,
        "salary": salary,
        "job_id": job_id,
        "department_id": department_id,
    }
    payload = {key: value for key, value in payload.items() if value is not None}
    return _request("PUT", f"/employees/{employee_id}", payload)


def remove_employee(employee_id: int):
    return _request("DELETE", f"/employees/{employee_id}")


TOOL_FUNCTIONS = {
    "get_employees_by_department": get_employees_by_department,
    "get_employees_by_job": get_employees_by_job,
    "create_employee": create_employee,
    "edit_employee": edit_employee,
    "remove_employee": remove_employee,
}


def function_calls_from_response(response) -> list[types.FunctionCall]:
    calls: list[types.FunctionCall] = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            call = getattr(part, "function_call", None)
            if call:
                calls.append(call)
    return calls


def tools_config() -> types.GenerateContentConfig:
    declarations = [
        types.FunctionDeclaration(
            name="get_employees_by_department",
            description="Fetch employees for a department.",
            parameters={
                "type": "object",
                "properties": {"department_id": {"type": "integer"}},
                "required": ["department_id"],
            },
        ),
        types.FunctionDeclaration(
            name="get_employees_by_job",
            description="Fetch employees for a job ID.",
            parameters={
                "type": "object",
                "properties": {"job_id": {"type": "string"}},
                "required": ["job_id"],
            },
        ),
        types.FunctionDeclaration(
            name="create_employee",
            description="Create a new employee record.",
            parameters={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "hire_date": {"type": "string"},
                    "salary": {"type": "number"},
                    "job_id": {"type": "string"},
                    "department_id": {"type": "integer"},
                },
                "required": ["employee_id", "job_id", "department_id"],
            },
        ),
        types.FunctionDeclaration(
            name="edit_employee",
            description="Update an existing employee.",
            parameters={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "hire_date": {"type": "string"},
                    "salary": {"type": "number"},
                    "job_id": {"type": "string"},
                    "department_id": {"type": "integer"},
                },
                "required": ["employee_id"],
            },
        ),
        types.FunctionDeclaration(
            name="remove_employee",
            description="Delete an employee by ID.",
            parameters={
                "type": "object",
                "properties": {"employee_id": {"type": "integer"}},
                "required": ["employee_id"],
            },
        ),
    ]

    return types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=declarations)]
    )


def run_tool_cycle(chat, response):
    while True:
        calls = function_calls_from_response(response)
        if not calls:
            return response

        for call in calls:
            handler = TOOL_FUNCTIONS.get(call.name)
            if not handler:
                result = {"error": f"Unknown tool: {call.name}"}
            else:
                try:
                    result = handler(**(call.args or {}))
                except Exception as exc:
                    result = {"error": str(exc)}

            if isinstance(result, list):
                result = {"items": result}

            tool_response = types.FunctionResponse(
                name=call.name,
                response=result,
            )
            response = chat.send_message(
                [types.Part(function_response=tool_response)]
            )
