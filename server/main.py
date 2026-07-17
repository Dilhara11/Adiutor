import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from google import genai

from employee_logic import (
	delete_employee,
	get_employees_by_department,
	get_employees_by_job,
	insert_employee,
	update_employee,
)
from gemini_tools import run_tool_cycle, tools_config


app = FastAPI(title="HR Employee API")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


class EmployeeIn(BaseModel):
	employee_id: int
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


class ChatRequest(BaseModel):
	prompt: str


class ChatResponse(BaseModel):
	text: str


@app.get("/employees/department/{department_id}")
def employees_by_department(department_id: int):
	return get_employees_by_department(department_id)


@app.get("/employees/job/{job_id}")
def employees_by_job(job_id: str):
	return get_employees_by_job(job_id)


@app.post("/employees")
def create_employee(employee: EmployeeIn):
	try:
		return insert_employee(employee.model_dump())
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/employees/{employee_id}")
def edit_employee(employee_id: int, employee: EmployeeUpdate):
	try:
		updated = update_employee(employee_id, employee.model_dump(exclude_none=True))
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc

	if not updated:
		raise HTTPException(status_code=404, detail="Employee not found")

	return {"message": "Employee updated", "employee_id": employee_id}


@app.delete("/employees/{employee_id}")
def remove_employee(employee_id: int):
	deleted = delete_employee(employee_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="Employee not found")

	return {"message": "Employee deleted", "employee_id": employee_id}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
	prompt = request.prompt.strip()
	if not prompt:
		raise HTTPException(status_code=400, detail="Prompt is required")

	load_dotenv()
	api_key = os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set")

	try:
		client = genai.Client(api_key=api_key)
		chat_session = client.chats.create(
			model="gemini-3.1-flash-lite-preview",
			config=tools_config(),
		)
		response = chat_session.send_message(prompt)
		response = run_tool_cycle(chat_session, response)
		text = response.text or ""
		return ChatResponse(text=text)
	except HTTPException:
		raise
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=False)
