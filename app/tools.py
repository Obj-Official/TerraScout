import os
import asyncio
from google.adk.tools import FunctionTool, google_search
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.sessions import Session
# from google.adk.runners import AgentInvocationContext
from .config import MCP_SERVER_URL

# --- Tool 1: Google Maps MCP Toolset (HTTP Streaming) ---
# This is the stable solution for production deployment and local Windows use.

GOOGLE_MAP_TOOL = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        # Uses the URL from config.py (defaults to http://localhost:5000/mcp)
        url=MCP_SERVER_URL,
        # API key is passed here as the remote server needs it
        headers={
            "X-Google-Maps-API-Key": os.environ.get("GOOGLE_MAPS_API_KEY") or ""
        },
    ),
)

# --- Tool 2: Herald Exit Function ---

def herald_exit_response():
    """Call this function when the user's prompt is out of context."""
    return {"status": "400", "message": "Sorry! The prompt you entered is not a Location Based request."}

HERALD_EXIT_TOOL = FunctionTool(herald_exit_response)


# --- Tool 3: Auto-Save Callback Function (Corrected Signature) ---

async def auto_save_to_memory(callback_context):
    """Automatically save session to memory after each agent turn."""
    # Ensure memory service and session are available before saving
    """Automatically save session to memory after each agent turn."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )
    # if invocation_context.memory_service and invocation_context.session:
    #     # Note: The ADK callback arguments were adjusted slightly from your notebook
    #     await invocation_context.memory_service.add_session_to_memory(
    #         invocation_context.session
    #     )
    # else:
    #     print("⚠️ WARNING: Memory Service or Session not available for auto-save.")