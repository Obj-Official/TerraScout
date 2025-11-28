import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # NEW IMPORT
from pydantic import BaseModel
from google.adk.runners import Runner
from google.genai import types
from .agents import ROOT_AGENT, SESSION_SERVICE, MEMORY_SERVICE
from .config import APP_NAME, USER_ID, MCP_SERVER_URL

# --- FastAPI Setup ---
app = FastAPI(title=APP_NAME, description="Multi-Agent System for Geo-Navigation.")

origins = [
    "http://localhost",
    "http://localhost:3000", # Common Next.js dev port
    "http://localhost:8080", # Common Cloud Run/Vertex AI port
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"], # Allow all headers
)
# --- FastAPI Setup ---
app = FastAPI(title=APP_NAME, description="Multi-Agent System for Geo-Navigation.")

# --- ADK Runner Setup ---
# The Runner needs to be initialized with the full root agent and services
runner = Runner(
    agent=ROOT_AGENT,
    app_name=APP_NAME,
    session_service=SESSION_SERVICE,
    memory_service=MEMORY_SERVICE,
)

# --- Pydantic Schemas for API ---
class UserPrompt(BaseModel):
    prompt: str
    session_id: str = "default_session"

class AgentResponse(BaseModel):
    message: str
    session_id: str

# --- API Endpoint ---
@app.post("/api/v1/run_agent", response_model=AgentResponse)
async def run_agent_session(data: UserPrompt):
    """
    Runs the multi-agent system workflow with a user prompt and returns the final response.
    """
    
    # 1. Prepare Session
    # In a real app, session_id would be tied to the user/frontend session
    session_id = data.session_id
    
    try:
        #Check if session exist
        session = await SESSION_SERVICE.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    except:
        # If session doesn't exist, create a new one
        session = await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)

    new_message = types.UserContent(parts=[types.Part(text=data.prompt)])

    # 2. Run Agent Workflow
    final_response_text = ""
    
    # Run the agent synchronously (using run_async wrapper) and aggregate the final response
    async for event in runner.run_async(
        user_id=USER_ID, 
        session_id=session_id, 
        new_message=new_message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            # We assume the final output is the JSON from the Aggregator
            final_response_text = event.content.parts[0].text
    
    if not final_response_text:
        # Handle cases where the agent returns an empty response (e.g., if ContextHerald calls the exit function)
        # Note: You'd need more complex logic to extract the JSON from the ContextHerald exit tool if that happens.
        # For simplicity, we assume the successful path here.
        return AgentResponse(
            message="Agent workflow finished, but no final response was generated (ContextHerald might have blocked it).",
            session_id=session_id
        )

    return AgentResponse(
        message=final_response_text,
        session_id=session_id
    )

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "agent_name": ROOT_AGENT.name, "mcp_url": MCP_SERVER_URL}
