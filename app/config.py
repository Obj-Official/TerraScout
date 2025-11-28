import os
from google.genai import types

# --- ADK Configuration ---
APP_NAME = "TerraScout"
USER_ID = "demo_user"
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:5000/mcp")

# --- Model Configuration ---
# Set up model retry options (uses a better structure for production)
RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# --- Environment Variable Setup ---
# The logic from your first cell, ensuring keys are set from the environment.
# Note: Do NOT hardcode secrets. Use environment variables.
os.environ["GOOGLE_API_KEY"] = "AIzaSyCB4hgvolu8fsOTpCXSsqWk_Y7P9hzotmU" #os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_MAPS_API_KEY"] = "AIzaSyD9GnFBnvyydRNQcyYU-DIRLI-NHqoKxyI"#os.getenv("GOOGLE_MAPS_API_KEY")

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GEMINI_API_KEY not found. Please set it in your environment.")
if not os.getenv("GOOGLE_MAPS_API_KEY"):
    print("⚠️ WARNING: MAPS_API_KEY not found. MCP tool may fail if not set on the server side.")