"""The AI side of Adiutor: the tools Gemini can use and the loop that runs them.

How a chat works:
1. We send the HR manager's message (plus earlier messages) to Gemini.
2. Gemini either answers in text, or asks us to run one or more tools,
   e.g. ``get_employees_by_department(department_id=50)``.
3. We run the tools *directly against the database* (no extra HTTP call),
   send all results back in one message, and repeat until Gemini answers.
"""

import asyncio
import os
from collections.abc import AsyncIterator
from datetime import date

from google import genai
from google.genai import types

import employee_logic as db

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")

# Safety net: stop if the model keeps asking for tools without answering.
MAX_TOOL_ROUNDS = 6

# Keep only this many earlier messages to limit cost and latency.
MAX_HISTORY_MESSAGES = 20

WRITE_TOOLS = {"create_employee", "edit_employee", "remove_employee"}


# ---------- Tool implementations ----------

def _create_employee(**fields):
    return db.insert_employee(fields)


def _edit_employee(employee_id: int, **fields):
    fields = {k: v for k, v in fields.items() if v is not None}
    if not db.update_employee(employee_id, fields):
        return {"error": f"No employee with ID {employee_id}"}
    return {"message": "Employee updated", "employee": db.get_employee(employee_id)}


def _remove_employee(employee_id: int):
    employee = db.get_employee(employee_id)
    if not employee or not db.delete_employee(employee_id):
        return {"error": f"No employee with ID {employee_id}"}
    return {"message": "Employee removed", "removed": employee}


def _get_employee(employee_id: int):
    return db.get_employee(employee_id) or {"error": f"No employee with ID {employee_id}"}


TOOL_FUNCTIONS = {
    "get_workforce_summary": db.workforce_summary,
    "list_departments": db.list_departments,
    "list_jobs": db.list_jobs,
    "get_employee": _get_employee,
    "search_employees": db.search_employees,
    "get_employees_by_department": db.get_employees_by_department,
    "get_employees_by_job": db.get_employees_by_job,
    "get_employees_hired_between": db.get_employees_hired_between,
    "create_employee": _create_employee,
    "edit_employee": _edit_employee,
    "remove_employee": _remove_employee,
}


def tool_label(name: str, args: dict) -> str:
    """A short, human-friendly description shown in the UI while a tool runs."""
    a = args or {}
    labels = {
        "get_workforce_summary": "Checked the workforce overview",
        "list_departments": "Looked up departments",
        "list_jobs": "Looked up job roles",
        "get_employee": f"Opened employee #{a.get('employee_id')}",
        "search_employees": f"Searched for “{a.get('query', '')}”",
        "get_employees_by_department": f"Listed department {a.get('department_id')}",
        "get_employees_by_job": f"Listed job {a.get('job_id')}",
        "get_employees_hired_between": f"Checked hires {a.get('start_date')} → {a.get('end_date')}",
        "create_employee": "Added a new employee",
        "edit_employee": f"Updated employee #{a.get('employee_id')}",
        "remove_employee": f"Removed employee #{a.get('employee_id')}",
    }
    return labels.get(name, name)


# ---------- Tool declarations (what Gemini sees) ----------

_EMPLOYEE_FIELDS = {
    "first_name": {"type": "string"},
    "last_name": {"type": "string"},
    "email": {"type": "string"},
    "phone_number": {"type": "string"},
    "hire_date": {"type": "string", "description": "YYYY-MM-DD"},
    "salary": {"type": "number", "description": "Yearly salary"},
    "job_id": {"type": "string", "description": "e.g. IT_PROG. Use list_jobs to find it."},
    "department_id": {"type": "integer", "description": "Use list_departments to find it."},
}


def _decl(name: str, description: str, properties: dict | None = None, required=None):
    params = None
    if properties:
        params = {"type": "object", "properties": properties, "required": required or []}
    return types.FunctionDeclaration(name=name, description=description, parameters=params)


DECLARATIONS = [
    _decl("get_workforce_summary", "Totals: headcount, average salary, payroll, headcount per department, latest hires."),
    _decl("list_departments", "All departments with ID, name, headcount and average salary."),
    _decl("list_jobs", "All job roles with job ID, title, salary range and headcount."),
    _decl("get_employee", "Full details for one employee.", {"employee_id": {"type": "integer"}}, ["employee_id"]),
    _decl(
        "search_employees",
        "Find employees by part of their first name, last name, full name or email.",
        {"query": {"type": "string"}},
        ["query"],
    ),
    _decl(
        "get_employees_by_department",
        "Employees in a department.",
        {"department_id": {"type": "integer"}},
        ["department_id"],
    ),
    _decl("get_employees_by_job", "Employees with a job ID.", {"job_id": {"type": "string"}}, ["job_id"]),
    _decl(
        "get_employees_hired_between",
        "Employees hired between two dates (inclusive).",
        {
            "start_date": {"type": "string", "description": "YYYY-MM-DD"},
            "end_date": {"type": "string", "description": "YYYY-MM-DD"},
        },
        ["start_date", "end_date"],
    ),
    _decl(
        "create_employee",
        "Add a new employee. Employee ID is assigned automatically if not given.",
        {"employee_id": {"type": "integer"}, **_EMPLOYEE_FIELDS},
        ["first_name", "last_name", "job_id", "department_id"],
    ),
    _decl(
        "edit_employee",
        "Change one or more fields of an existing employee.",
        {"employee_id": {"type": "integer"}, **_EMPLOYEE_FIELDS},
        ["employee_id"],
    ),
    _decl("remove_employee", "Permanently delete an employee.", {"employee_id": {"type": "integer"}}, ["employee_id"]),
]


def system_instruction() -> str:
    return f"""You are Adiutor, an assistant for an HR manager. Today is {date.today().isoformat()}.
You manage employee records using the provided tools. Never invent data; always look it up.

Data model: employees belong to one department (numeric department_id) and one job (text job_id like IT_PROG).
When the user names a department or job in words (e.g. "Engineering", "software engineers"), call
list_departments or list_jobs first to find the ID. When they name a person, use search_employees.

Before create_employee, edit_employee or remove_employee:
- Show a short summary of exactly what will change (for edits show old -> new values).
- Ask the user to confirm, and only call the tool after they clearly say yes.
- If a salary is outside the job's min/max range, mention it.

Formatting (Markdown):
- Use a table when listing more than two employees (columns: ID, Name, Job, Department, Hire date, Salary).
- Format salaries like $85,000. Keep answers short and friendly, written for a non-technical manager.
- If something fails, explain why in plain words and suggest what to do next."""


def tools_config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=system_instruction(),
        tools=[types.Tool(function_declarations=DECLARATIONS)],
        # We run tools ourselves so we can report progress to the UI.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )


# ---------- Running tools ----------

def run_tool(name: str, args: dict) -> dict:
    handler = TOOL_FUNCTIONS.get(name)
    if not handler:
        return {"error": f"Unknown tool: {name}"}
    try:
        result = handler(**(args or {}))
    except Exception as exc:  # report the problem to the model instead of crashing
        return {"error": str(exc)}
    if isinstance(result, list):
        return {"items": result, "count": len(result)}
    return result if isinstance(result, dict) else {"result": result}


async def _run_calls(calls: list[types.FunctionCall]) -> list[types.Part]:
    """Run every requested tool (in parallel) and return all results as one batch."""
    results = await asyncio.gather(
        *(asyncio.to_thread(run_tool, call.name, dict(call.args or {})) for call in calls)
    )
    return [
        types.Part(function_response=types.FunctionResponse(id=call.id, name=call.name, response=result))
        for call, result in zip(calls, results)
    ]


def history_to_contents(history: list[dict]) -> list[types.Content]:
    contents = []
    for turn in history[-MAX_HISTORY_MESSAGES:]:
        text = (turn.get("text") or "").strip()
        if not text:
            continue
        role = "user" if turn.get("role") == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=text)]))
    return contents


async def stream_chat(
    client: genai.Client, prompt: str, history: list[dict] | None = None
) -> AsyncIterator[dict]:
    """Yield events while answering:

    {"type": "text", "delta": "..."}            piece of the answer
    {"type": "tool", "name": ..., "label": ...} a tool is being used
    {"type": "data_changed"}                    a record was added/edited/removed
    """
    chat = client.aio.chats.create(
        model=MODEL,
        config=tools_config(),
        history=history_to_contents(history or []),
    )

    message: str | list[types.Part] = prompt
    for _ in range(MAX_TOOL_ROUNDS):
        calls: list[types.FunctionCall] = []
        async for chunk in await chat.send_message_stream(message):
            for candidate in chunk.candidates or []:
                for part in (candidate.content.parts if candidate.content else None) or []:
                    if part.function_call:
                        calls.append(part.function_call)
                    elif part.text and not part.thought:
                        yield {"type": "text", "delta": part.text}

        if not calls:
            return

        for call in calls:
            yield {"type": "tool", "name": call.name, "label": tool_label(call.name, dict(call.args or {}))}
        message = await _run_calls(calls)
        if any(call.name in WRITE_TOOLS for call in calls):
            yield {"type": "data_changed"}

    yield {"type": "text", "delta": "\n\n_I stopped because this request needed too many steps. Please try a simpler question._"}


async def run_chat(client: genai.Client, prompt: str, history: list[dict] | None = None) -> dict:
    """Non-streaming version: wait for the whole answer."""
    text, tools = [], []
    async for event in stream_chat(client, prompt, history):
        if event["type"] == "text":
            text.append(event["delta"])
        elif event["type"] == "tool":
            tools.append(event["label"])
    return {"text": "".join(text), "tools": tools}
