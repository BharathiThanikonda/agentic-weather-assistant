# Weather Agent

A small full-stack weather assistant built with three layers:

- A plain HTML/CSS/JS frontend for chat input/output
- A FastAPI agent backend powered by Groq and LangChain
- An MCP weather server that wraps OpenWeatherMap tools

The backend sends user messages to an LLM, the LLM can call weather tools exposed by the MCP server, and the MCP server fetches live weather data from OpenWeatherMap.

## Architecture

```text
+-------------------+      POST /chat      +---------------------+      MCP tools      +---------------------+      HTTPS API      +----------------------+
|   Frontend        | -------------------> |   Agent Backend     | ------------------> |   MCP Server         | ------------------> | OpenWeatherMap API   |
|   index.html      |                      |   FastAPI + LangChain|                     |   FastMCP tools      |                     | live weather data    |
+-------------------+                      +---------------------+                     +---------------------+                     +----------------------+
```

## Prerequisites

- Python 3.11 or newer
- A Groq account and API key
- An OpenWeatherMap account and API key
- A modern browser

## Project Setup

### 1. Create and activate a virtual environment

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you are using Command Prompt instead of PowerShell:

```bat
venv\Scripts\activate
```

### 2. Install dependencies

Install the backend and MCP server dependencies:

```powershell
pip install -r backend\requirements.txt
pip install -r mcp-server\requirements.txt
```

## API Keys

You need two API keys:

- **GROQ_API_KEY**: used by the agent backend to talk to Groq
- **OPENWEATHERMAP_API_KEY**: used by the MCP server to fetch weather data

### How to get the Groq API key

1. Create or sign in to a Groq account.
2. Open the Groq console.
3. Generate a new API key.
4. Copy the key into `backend/.env`.

### How to get the OpenWeatherMap API key

1. Create or sign in to an OpenWeatherMap account.
2. Go to the API keys section of your account.
3. Generate or copy your key.
4. Paste it into `mcp-server/.env`.

## Environment Files

Create these files by copying the example files:

- `backend/.env.example` -> `backend/.env`
- `mcp-server/.env.example` -> `mcp-server/.env`

### `backend/.env`

```env
GROQ_API_KEY=your_actual_groq_api_key
```

### `mcp-server/.env`

```env
OPENWEATHERMAP_API_KEY=your_actual_openweathermap_api_key
```

## Running the Backend

The backend runs on `http://localhost:8000`.

In one terminal:

```powershell
cd backend
uvicorn main:app --reload
```

The backend will:

- Load the Groq model `llama-3.3-70b-versatile`
- Connect to the MCP server
- Let the agent call weather tools when needed

## Running the MCP Server

The MCP server is the tool layer that talks to OpenWeatherMap.

In a second terminal:

```powershell
cd mcp-server
python server.py
```

It listens on `http://127.0.0.1:8080/mcp`. Start it **before** the backend so the
agent can load the weather tools at startup.

## Opening the Frontend

The frontend is a single static file at `frontend/index.html`.

### Option 1: Open it directly

Open `frontend/index.html` in your browser.

### Option 2: Serve it locally

If you prefer a local web server:

```powershell
cd frontend
python -m http.server 5500
```

Then open:

```text
http://localhost:5500
```

The chat UI sends messages to `http://localhost:8000/chat`.

## Project Structure

```text
Weather_agent/
├── .gitignore
├── README.md
├── backend/
│   ├── .env.example
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── index.html
├── mcp-server/
│   ├── .env.example
│   ├── server.py
│   └── requirements.txt
└── venv/
```

### Root

- `.gitignore`: ignores local env files, virtual environments, and Python cache files
- `README.md`: project overview and setup instructions

### `backend/`

- `main.py`: FastAPI app, Groq LLM setup, LangChain agent, and `/chat` endpoint
- `requirements.txt`: Python dependencies for the backend
- `.env.example`: example Groq environment file

### `frontend/`

- `index.html`: single-file chat UI with inline CSS and JavaScript

### `mcp-server/`

- `server.py`: MCP server with weather tools for current weather and forecast
- `requirements.txt`: Python dependencies for the MCP server
- `.env.example`: example OpenWeatherMap environment file

### `venv/`

- Local Python virtual environment for the project

## Quick Start Checklist

1. Create and activate `venv`
2. Install dependencies from both `requirements.txt` files
3. Create `backend/.env` with `GROQ_API_KEY`
4. Create `mcp-server/.env` with `OPENWEATHERMAP_API_KEY`
5. Start the MCP server
6. Start the backend
7. Open the frontend and chat

## Notes for the Next Developer

- The frontend is intentionally build-free and static.
- The backend expects the MCP server to be available before or during startup.
- If the agent starts but weather calls fail, verify both `.env` files and that the MCP server is running.
- The current setup is intentionally small and easy to extend.
