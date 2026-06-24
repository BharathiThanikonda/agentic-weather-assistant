# Prompts Used to Build This Project



## 1. MCP Server (the API wrapper)

**Create the server and the first tool:**

> I want to build a small MCP server in Python using FastMCP (the official `mcp`
> SDK). Create mcp-server/server.py with a single tool get_current_weather(city)
> that returns the current temperature and conditions for a city using the
> OpenWeatherMap API and the requests library. Keep it simple for now.

**Add the second tool:**

> Now add a second tool get_forecast(city, days=3) that returns a short daily
> forecast. Reuse the same API key handling.

**Add error handling and tool docstrings (so the LLM can pick the right tool):**

> Add error handling: if the city isn't found or the API key is missing, return a
> clear friendly message instead of throwing. Also add a good docstring to each
> tool explaining when to use it — I know the LLM reads these to pick a tool.

**Generate the dependency file:**

> Create mcp-server/requirements.txt with the exact libraries this server needs.

---

## 2. Agent Backend (FastAPI + LangChain + Groq)

**Scaffold the API:**

> In the agent-backend folder, create a minimal FastAPI app with a POST /chat
> endpoint that takes {"message": "..."} and just echoes it back as JSON for now.
> Add CORS so a local web page can call it.

**Connect the LLM:**

> Now connect an LLM. Use langchain-groq with the model llama-3.3-70b-versatile,
> reading GROQ_API_KEY from a .env file. Make /chat send the user's message to the
> model and return its reply.

**Load the MCP tools into LangChain:**

> I have an MCP server at ../mcp-server/server.py. Use the langchain-mcp-adapters
> library to load its tools as LangChain tools so the LLM can call them.

**Wrap everything into a tool-calling agent:**

> Wrap this into a LangChain agent that can actually call the weather tools (use
> langgraph create_react_agent or AgentExecutor). The /chat endpoint should run
> the agent and return its final answer.

**Add the system prompt (prompt engineering for contextual answers):**

> Add a system prompt so the assistant acts like a practical weather helper: don't
> just give numbers, give advice (umbrella? jacket? sunscreen?) based on the tool
> results. Keep answers short and friendly.

---

## 3. Frontend (single-file chat UI)

**Build the basic chat page:**

> In the frontend folder, create a single index.html (inline CSS + JS, no build
> tools) with a chat box that POSTs the message to http://localhost:8000/chat and
> shows the reply. Make it work first, keep styling basic.

**Add UX feedback:**

> Add a "thinking..." indicator that shows while waiting for the backend reply,
> and disable the send button until the reply comes back.

**Polish the styling:**

> Now improve the styling: clean modern chat bubbles, readable on mobile, a nice
> header. Still one file, still plain HTML/CSS/JS.

---

## 4. Project Setup & Documentation

**Secrets handling and example env files:**

> Create a root .gitignore that excludes .env, venv/ and __pycache__/. Also create
> .env.example files in mcp-server and agent-backend showing the variable names
> with placeholder values. Tell me what to put in my real .env files.

**Write the README for a new developer:**

> Write a professional README.md for the project root aimed at a new developer
> taking over. Include: project summary, an ASCII architecture diagram
> (Frontend -> Agent Backend -> MCP Server -> OpenWeatherMap), prerequisites,
> setup (venv + install), how to get both API keys, how to create the .env files,
> how to run the backend, how to open the frontend, and a folder-by-folder
> "Project Structure" section.
