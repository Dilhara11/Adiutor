# Adiutor

Adiutor is an AI-powered HR workspace with a modern web client and a FastAPI backend.

- **Frontend:** Next.js app in [`client`](client) for chatting with the assistant and viewing responses.
- **Backend:** FastAPI service in [`server`](server) for employee operations and Gemini-backed chat orchestration.

By default, the frontend calls the backend at `http://localhost:5000`.

## ✨ Highlights

- AI assistant chat powered by Google Gemini, with streaming answers and conversation memory
- HR dashboard: workforce overview, headcount by department, recent hires, quick actions
- Employee management endpoints for common HR flows
- TypeScript-based frontend with modern React + Next.js
- Python FastAPI backend with SQLite persistence

## 🧱 Architecture

```text
client (Next.js)  --->  server (FastAPI)  --->  Gemini API
                       └---> SQLite
```

## 🛠️ Tech Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Uvicorn, Python, SQLite, managed with uv
- **AI:** Google Gemini (`google-genai`)

## 📁 Project Structure

- [`client`](client) — UI, routing, and chat experience
- [`server`](server) — API, business logic, and AI/tool integration

## ✅ Prerequisites

- Node.js 18+
- Python 3.11+ and [uv](https://docs.astral.sh/uv/) (uv can install Python for you)
- Gemini API key

## 🚀 Quick Start

### 1) Start the backend

```bash
cd server
uv sync                  # creates .venv and installs exact versions from uv.lock
uv run db.py --demo      # optional: adds 10 sample employees
uv run main.py
```

Create `server/.env`:

```env
GEMINI_API_KEY=your_key_here
# optional: GEMINI_MODEL, SEED_DEMO_DATA, HR_DB_PATH, CORS_ORIGINS, PORT
```

The database (`server/human_resources.db`) is created automatically on start-up with default departments and jobs.

Backend URL: `http://localhost:5000`

### 2) Start the frontend

```bash
cd client
npm install
npm run dev
```

Optional `client/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

Frontend URL: `http://localhost:3000`

## 🔌 API at a glance

- `POST /chat/stream` — streamed AI answer (newline-delimited JSON events)
- `POST /chat` — full AI answer in one response (`{prompt, history}` → `{text, tools}`)
- `GET /summary`, `GET /departments`, `GET /jobs`, `GET /health`
- `GET /employees?q=`, `GET /employees/{employee_id}`
- `GET /employees/department/{department_id}`, `GET /employees/job/{job_id}`
- `POST /employees`, `PUT /employees/{employee_id}`, `DELETE /employees/{employee_id}`

## 📝 What's new

See [docs/CHANGES.md](docs/CHANGES.md) for a plain-English guide to the latest performance, safety and UI improvements.

## 🧪 Frontend Scripts

From `client/`:

- `npm run dev` — start development server
- `npm run lint` — run ESLint
- `npm run build` — create production build

## 📝 Notes

- Backend CORS is configured for `http://localhost:3000` by default.
- The AI asks for confirmation before adding, editing or removing employees. There is no login yet, so don't expose the app publicly.