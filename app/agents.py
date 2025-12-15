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
    instruction="""You are the Master geo-navigator, Ani, and your duty is to get the prompt from the user
    This prompt has the user's current location's coordinates and a request by the user
    You are to find three most significant and MORE IMPORTANTLY closest places to the user based on the user's request.
    Once you have obtained it, you MUST document the following details from your findings 
    1. User's Current Location
    2. First Location found and its coordinates
    3. Second Location found and its coordinates 
    4. Third Location found and its coordinates """,
    output_key="locations_gotten",
    tools=[google_search], #GOOGLE_MAP_TOOL Use the singular, correctly defined tool GOOGLE_MAP_TOOL
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
    - Your focus is ONLY the first location in relation to user's current location
    - Research on this location using your tools, obtain some details, and document the results from the research focusing on the following details:
    1. Name of Agent - Obie
    2. Location name, 
    3. Location address, 
    4. Location url - a clickable link that takes you to its google map location, 
    5. Distance from current location
    6. Details or brief description about the place.""",
    output_key="first_location_details",
    tools=[google_search], #GOOGLE_MAP_TOOL
)

# 3. Elite Navigator (Kemi) - FIXED MODEL
elite_navigator_kemi = Agent(
    name="Kemi",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=RETRY_CONFIG
    ),
    instruction="""You are Elite geo-navigator, Kemi, and your duty is to: 
    - Get the user's current location, second location and it's coordinates in the output containing three locations saved at output key: {locations_gotten}
    - Your focus is ONLY the second location in relation to user's current location
    - Research on this location using your tools, obtain some details, and document the results from the research focusing on the following details:
    1. Name of Agent - Kemi
    2. Location name, 
    3. Location address, 
    4. Location url - a clickable link that takes you to its google map location, 
    5. Distance from current location
    6. Details or brief description about the place.""",
    output_key="second_location_details",
    tools=[google_search], #GOOGLE_MAP_TOOL
)

# 4. Elite Navigator (Lexxie) - FIXED MODEL
elite_navigator_lexxie = Agent(
    name="Lexxie",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=RETRY_CONFIG
    ),
    instruction="""You are Elite geo-navigator, Lexxie, and your duty is to: 
    - Get the user's current location, third location and it's coordinates in the output containing three locations saved at output key: {locations_gotten}
    - Your focus is ONLY the third location in relation to user's current location
    - Research on this location using your tools, obtain some details, and document the results from the research focusing on the following details:
    1. Name of Agent - Lexxie
    2. Location name, 
    3. Location address, 
    4. Location url - a clickable link that takes you to its google map location, 
    5. Distance from current location
    6. Details or brief description about the place.""",
    output_key="third_location_details",
    tools=[google_search], #GOOGLE_MAP_TOOL
)

# 5. Context Herald (LlmAgent) - FIXED MODEL
context_herald = LlmAgent(
    name="ContextHerald",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=RETRY_CONFIG
    ),
    instruction="""You are the context herald and a rookie navigator. Your duty is to review the prompt from the user.
    Your tasks include: 
    1. You are to ignore the location coordinates present in the prompt and do nothing about it.
    2. You are to check the user request instead and see if the request is within context.
    - IF the user in the prompt, is not asking for a place or location or not implying a place that can be located on the map.
    - You MUST call the `herald_exit_response` function and nothing else
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

    **First Location Details:**
    {first_location_details}
    
    **Second Location Details:**
    {second_location_details}
    
    **Third Location Details:**
    {third_location_details}

    The JSON tructure will have an array containing three location objects with the following keys:
    1. Name of Agent (elite_name),
    2. Location name (location_name), 
    3. Location address (location_address), 
    4. Location url (location_url), 
    5. Distance from current location (distance),
    6. Details or brief description about the place (details).
    You MUST output ONLY a JSON which combines all the detail""",
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

#--------Astra------------
# 4. Astra the oracle
astra = Agent(
    name="Astra",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=RETRY_CONFIG
    ),
    instruction="""You are Elite geo-navigator, Lexxie, and your duty is to: 
    ...Your focus is ONLY the third location in relation to user's current location...""",
    output_key="third_location_details",
    tools=[google_search], #GOOGLE_MAP_TOOL
)