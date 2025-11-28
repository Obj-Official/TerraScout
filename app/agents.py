from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from .config import RETRY_CONFIG, APP_NAME
from .tools import GOOGLE_MAP_TOOL, HERALD_EXIT_TOOL, auto_save_to_memory

# --- Services ---
SESSION_SERVICE = InMemorySessionService()
MEMORY_SERVICE = InMemoryMemoryService() # Use InMemory for development; swap for VertexAiMemoryBankService for production

# --- Agent Definitions ---

# 1. Master Navigator (Ani) - FIXED MODEL
master_navigator_ani = Agent(
    name="Ani",
    model=Gemini(
        # MUST use a model that supports Function Calling
        model="gemini-2.5-flash", 
        retry_options=RETRY_CONFIG
    ),
    instruction="""You are the Master geo-navigator, Ani, and your duty is to get the prompt from the user...
    ...4. Third Location found and its coordinates """,
    output_key="locations_gotten",
    tools=[google_search, GOOGLE_MAP_TOOL], # Use the singular, correctly defined tool GOOGLE_MAP_TOOL
)

# 2. Elite Navigator (Obie) - FIXED MODEL
elite_navigator_obie = Agent(
    name="Obie",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=RETRY_CONFIG
    ),
    instruction="""You are Elite geo-navigator, Obie, and your duty is to: 
    - Get the user's current location, first location and it's coordinates in the output containing three locations saved at output key: {locations_gotten}
    ...
    6. Details or brief description about the place.""",
    output_key="first_location_details",
    tools=[google_search, GOOGLE_MAP_TOOL], 
)

# 3. Elite Navigator (Kemi) - FIXED MODEL
elite_navigator_kemi = Agent(
    name="Kemi",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=RETRY_CONFIG
    ),
    instruction="""You are Elite geo-navigator, Kemi, and your duty is to: 
    ...Your focus is ONLY the second location in relation to user's current location...""",
    output_key="second_location_details",
    tools=[google_search, GOOGLE_MAP_TOOL],
)

# 4. Elite Navigator (Lexxie) - FIXED MODEL
elite_navigator_lexxie = Agent(
    name="Lexxie",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=RETRY_CONFIG
    ),
    instruction="""You are Elite geo-navigator, Lexxie, and your duty is to: 
    ...Your focus is ONLY the third location in relation to user's current location...""",
    output_key="third_location_details",
    tools=[google_search, GOOGLE_MAP_TOOL], 
)

# 5. Context Herald (LlmAgent) - FIXED MODEL
context_herald = LlmAgent(
    name="ContextHerald",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=RETRY_CONFIG
    ),
    instruction="""You are the context herald and a rookie navigator. Your duty is to review the prompt from the user...
    ...You MUST call the `herald_exit_response` function and nothing else
    - OTHERWISE, (which means it is within context), document the prompt as it is (with the coordinates)""",
    output_key="conveyed_message",
    tools=[HERALD_EXIT_TOOL],
)

# 6. Aggregator Agent - FIXED MODEL
aggregator = Agent(
    name="Aggregator",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=RETRY_CONFIG
    ),
    instruction="""Combine the results of these three findings into a single JSON structure:
    ...You MUST output ONLY a JSON which combines all the detail""",
    output_key="all_location_response",
)

# --- Composite Agents ---

# ParallelAgent runs Obie, Kemi, and Lexxie simultaneously
parallel_elite_search = ParallelAgent(
    name="ParallelEliteSearch",
    sub_agents=[elite_navigator_obie, elite_navigator_kemi, elite_navigator_lexxie],
)

# SequentialAgent defines the full workflow
ROOT_AGENT = SequentialAgent(
    name="TerraScout",
    # Note: `aggregator_agent` in your code was a typo; it should be `aggregator`
    # The workflow is: Context -> Master Ani -> Parallel Search -> Aggregator
    sub_agents=[context_herald, master_navigator_ani, parallel_elite_search, aggregator],
    after_agent_callback=auto_save_to_memory,
)