# Adiutor

Adiutor is a two-part AI-assisted HR workspace:

- A Next.js frontend in [client](client) for chatting with the assistant and viewing responses.
- A FastAPI backend in [server](server) for employee data actions and Gemini-powered chat orchestration.

The frontend talks to the backend over HTTP. By default, the client expects the API at `http://localhost:5000`.

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Uvicorn, Python, SQLite
- AI: Google Gemini via the `google-genai` SDK

## Project Structure

- [client](client): Next.js app and UI components
- [server](server): FastAPI API, employee logic, and Gemini integration

## Prerequisites

- Node.js 18+ for the client
- Python 3.11+ for the server
- A Gemini API key for the chat endpoint

## Setup

### 1. Backend

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirments.txt
```

Create a `.env` file in [server](server) with your Gemini key:

```env
GEMINI_API_KEY=your_key_here
```

Start the API server:

```bash
python main.py
```

The backend runs on `http://localhost:5000`.

### 2. Frontend

```bash
cd client
npm install
```

If you want to point the frontend at a different backend URL, create a `.env.local` file in [client](client):

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

Start the app:

```bash
npm run dev
```

The frontend runs on `http://localhost:3000`.

## How It Works

- The client sends prompts to `POST /chat`.
- The server forwards the prompt to Gemini with tool support.
- The server also exposes employee CRUD-style endpoints for department/job lookups and record management.

## API Endpoints

- `GET /employees/department/{department_id}`
- `GET /employees/job/{job_id}`
- `POST /employees`
- `PUT /employees/{employee_id}`
- `DELETE /employees/{employee_id}`
- `POST /chat`

## Notes

- Local SQLite data files and Python virtual environments are ignored by git.
- The backend enables CORS for `http://localhost:3000` by default.
- The repository contains a legacy file named `requirments.txt`; keep that filename as-is unless you plan to rename it everywhere it is referenced.

## Development Tips

- Run the backend first, then start the frontend.
- If chat requests fail, confirm `GEMINI_API_KEY` is set and the backend is reachable on port `5000`.
- If the frontend cannot reach the API, verify `NEXT_PUBLIC_API_BASE_URL` matches your backend URL.