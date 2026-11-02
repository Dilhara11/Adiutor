import json
import os
from contextlib import asynccontextmanager
from typing import Literal

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google import genai
from pydantic import BaseModel, Field

import employee_logic as db
from db import init_db
from gemini_tools import MODEL, run_chat, stream_chat

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts (not on every request).
    init_db(with_demo_data=os.getenv("SEED_DEMO_DATA", "").lower() in {"1", "true", "yes"})
    api_key = os.getenv("GEMINI_API_KEY")
    app.state.genai = genai.Client(api_key=api_key) if api_key else None
    yield


app = FastAPI(title="Adiutor HR API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Models ----------

class EmployeeIn(BaseModel):
    employee_id: int | None = None  # assigned automatically when left out
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    hire_date: str | None = None
    salary: float | None = None
    job_id: str
    department_id: int


class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    hire_date: str | None = None
    salary: float | None = None
    job_id: str | None = None
    department_id: int | None = None


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    text: str


class ChatRequest(BaseModel):
    prompt: str
    history: list[ChatTurn] = Field(default_factory=list)


class ChatResponse(BaseModel):
    text: str
    tools: list[str] = Field(default_factory=list)


# ---------- Dashboard / lookup endpoints ----------

@app.get("/health")
def health(request: Request):
    return {"status": "ok", "ai_configured": request.app.state.genai is not None, "model": MODEL}


@app.get("/summary")
def summary():
    return db.workforce_summary()


@app.get("/departments")
def departments():
    return db.list_departments()


@app.get("/jobs")
def jobs():
    return db.list_jobs()


# ---------- Employee endpoints ----------

@app.get("/employees")
def search_employees(q: str = ""):
    return db.search_employees(q)


@app.get("/employees/department/{department_id}")
def employees_by_department(department_id: int):
    return db.get_employees_by_department(department_id)


@app.get("/employees/job/{job_id}")
def employees_by_job(job_id: str):
    return db.get_employees_by_job(job_id)


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    employee = db.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.post("/employees")
def create_employee(employee: EmployeeIn):
    try:
        return db.insert_employee(employee.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/employees/{employee_id}")
def edit_employee(employee_id: int, employee: EmployeeUpdate):
    try:
        updated = db.update_employee(employee_id, employee.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not updated:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee updated", "employee_id": employee_id}


@app.delete("/employees/{employee_id}")
def remove_employee(employee_id: int):
    if not db.delete_employee(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted", "employee_id": employee_id}


# ---------- Chat endpoints ----------

def _client_or_error(request: Request) -> genai.Client:
    client = request.app.state.genai
    if client is None:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set on the server")
    return client


def _validated(chat_request: ChatRequest) -> tuple[str, list[dict]]:
    prompt = chat_request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    return prompt, [turn.model_dump() for turn in chat_request.history]


@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, request: Request):
    """Wait for the full answer, then return it in one piece."""
    client = _client_or_error(request)
    prompt, history = _validated(chat_request)
    try:
        return ChatResponse(**await run_chat(client, prompt, history))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/chat/stream")
async def chat_stream(chat_request: ChatRequest, request: Request):
    """Send the answer piece by piece as newline-delimited JSON events."""
    client = _client_or_error(request)
    prompt, history = _validated(chat_request)

    async def events():
        try:
            async for event in stream_chat(client, prompt, history):
                yield json.dumps(event) + "\n"
        except Exception as exc:
            yield json.dumps({"type": "error", "message": str(exc)}) + "\n"
        yield json.dumps({"type": "done"}) + "\n"

    return StreamingResponse(
        events(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "5000")), reload=False)
