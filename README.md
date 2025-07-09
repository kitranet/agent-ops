# 🧠 AgentOps: Local Dev Setup

This is a complete setup for managing AI agents (LangGraph, Swarm, etc.) using a backend built in **FastAPI + SQLite** and a frontend in **React**.

---

## 📁 Project Structure

```
agentops-backend/       ← FastAPI backend
agentops-frontend/          ← React frontend
```

---

## ✅ Prerequisites

Install these on your system:

- [Python 3.11](https://www.python.org/downloads/)
- [Node.js (LTS)](https://nodejs.org)
- [Git (optional)](https://git-scm.com)

---

## ⚙️ Backend Setup (FastAPI)

### Step 1: Create virtual environment & activate

```bash
cd agentops-backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the backend

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000

or

uvicorn main:app --reload
```

This starts the FastAPI server at:  
📍 `http://127.0.0.1:8000`

---

## 🌐 Frontend Setup (React + Vite)

### Step 1: Install Node modules

```bash
curl http://127.0.0.1:8000/agents/list/all
curl http://127.0.0.1:8000/agents/status/agent-001
npm install
```

### Step 2: Run the frontend app

```bash
npm run dev
npm start
```

This starts the UI at:  
📍 `http://localhost:5173`

---

## 🔁 Connect Frontend to Backend

### Option A: Edit fetch URLs in React

Change API calls in `AgentDashboard.jsx` from `/agents/...` to `http://127.0.0.1:8000/agents/...`

### Option B: Use Proxy (preferred)

Edit `vite.config.js`:

```js
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/agents': 'http://127.0.0.1:8000'
    }
  }
});
```

---

## 🚀 Features Supported

✅ Agent Registration  
✅ Agent Retirement  
✅ Agent Status Monitoring  
✅ Feedback Submission  
✅ MCP (Model Context Protocol) Upload  
✅ Telemetry & Anomaly Detection  
✅ Deployment Auditing

---

## 📦 Extras

- Feedback saved in `/feedback/`
- MCP saved in `/mcp/`
- Logs written to `/logs/agent_activity.log`

---

## 🧠 Credits

Created by [M.R.Vijay Krishnan] – Built for managing LLM agents 


