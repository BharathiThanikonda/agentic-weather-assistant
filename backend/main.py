from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, SecretStr
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from dotenv import load_dotenv
import os
from typing import cast

from langchain_mcp_adapters.sessions import Connection, create_session
from langchain_mcp_adapters.tools import (
    _list_all_tools,
    convert_mcp_tool_to_langchain_tool,
)


load_dotenv()

# --- LLM and Agent Setup ---
llm = None
agent_graph = None
tools = []

# --- FastAPI App Setup ---
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    Asynchronously load tools and initialize the agent when the app starts.
    """
    global llm, agent_graph, tools

    if tools:
        return

    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("FATAL: GROQ_API_KEY is not set. Please add it to backend/.env.")
        return

    # Initialize the LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=SecretStr(groq_api_key)
    )

    # --- Tool Loading Logic ---
    mcp_server_url = "http://localhost:8080/mcp"
    print(f"Attempting to load tools from MCP server at {mcp_server_url}...")
    
    try:
        connection = cast(Connection, {"transport": "streamable_http", "url": mcp_server_url})
        async with create_session(connection) as session:
            await session.initialize()
            mcp_tools = await _list_all_tools(session)

        if not mcp_tools:
            print("Warning: No tools found on the MCP server.")
        else:
            print(f"Found {len(mcp_tools)} tools on MCP server.")

        
        for tool in mcp_tools:
            converted_tool = convert_mcp_tool_to_langchain_tool(
                session=None, tool=tool, connection=connection
            )
            tools.append(converted_tool)

    except Exception as e:
        print(f"FATAL: Could not connect to or load tools from MCP server: {e}")
        print("Please ensure the MCP server is running at the specified URL.")
        return

    system_prompt = (
        "You are a practical weather helper. "
        "Use the weather tools when helpful, then answer briefly and naturally. "
        "Do not just repeat numbers. Include simple advice like umbrella, jacket, or sunscreen when it fits the conditions. "
        "Keep replies short and friendly."
    )

    agent_graph = create_agent(model=llm, tools=tools, system_prompt=system_prompt)
    print("Agent initialized successfully with tools.")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ChatMessage(BaseModel):
    message: str


def _extract_agent_response(response: object) -> str | None:
    """Return the best available text answer from the agent state."""
    if not isinstance(response, dict):
        return None

    structured_response = response.get("structured_response")
    if structured_response is not None:
        return str(structured_response)

    messages = response.get("messages", [])
    for message in reversed(messages):
        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content")

        if content:
            return str(content)

    return None

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    """
    Receives a message, sends it to the agent, and returns the final answer.
    """
    if not agent_graph:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized. Check server startup logs for errors.",
        )
    
    try:
        response = await agent_graph.ainvoke({"messages": [{"role": "user", "content": chat_message.message}]})
        reply_text = _extract_agent_response(response)
        if not reply_text:
            raise HTTPException(status_code=502, detail="Agent returned no response.")
        return {"response": reply_text}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during agent execution: {type(e).__name__}: {e}",
        )

@app.get("/")
def read_root():
    return {"message": "FastAPI server with LangChain agent is running"}

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    print("Ensure the MCP server is running on http://localhost:8080/mcp")
    print("Ensure the GROQ_API_KEY is set in your .env file")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
