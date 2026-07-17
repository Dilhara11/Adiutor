# Adiutor

Adiutor is an AI-powered HR workspace with a modern web client and a FastAPI backend.

- **Frontend:** Next.js app in [`client`](client) for chatting with the assistant and viewing responses.
- **Backend:** FastAPI service in [`server`](server) for employee operations and Gemini-backed chat orchestration.

By default, the frontend calls the backend at `http://localhost:5000`.

## ✨ Highlights

- AI assistant chat powered by Google Gemini
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
- **Backend:** FastAPI, Uvicorn, Python, SQLite
- **AI:** Google Gemini (`google-genai`)

## 📁 Project Structure

- [`client`](client) — UI, routing, and chat experience
- [`server`](server) — API, business logic, and AI/tool integration

## ✅ Prerequisites

- Node.js 18+
- Python 3.11+
- Gemini API key

## 🚀 Quick Start

### 1) Start the backend

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirments.txt
python main.py
```

Create `server/.env`:

```env
GEMINI_API_KEY=your_key_here
```

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

- `GET /employees/department/{department_id}`
- `GET /employees/job/{job_id}`
- `POST /employees`
- `PUT /employees/{employee_id}`
- `DELETE /employees/{employee_id}`
- `POST /chat`

## 🧪 Frontend Scripts

From `client/`:

- `npm run dev` — start development server
- `npm run lint` — run ESLint
- `npm run build` — create production build

## 📝 Notes

- Backend CORS is configured for `http://localhost:3000` by default.
- The backend dependency file is intentionally named `requirments.txt`.