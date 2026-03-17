import os
import time
import requests
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

# --- Configuration ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "openai/gpt-4o-mini"
API_URL = "http://localhost:3000/api/messages"

# Global variable to let tools know WHICH agent is currently acting
# (This is a workaround because CrewAI tools are stateless by default)
CURRENT_ACTIVE_AGENT_NAME = ""

# --- Define Custom Tools ---

@tool("Fetch Messages Tool")
def fetch_messages_tool() -> str:
    """
    Fetches the latest messages from the sandbox environment. 
    Use this tool to read what other agents have been saying before you reply.
    """
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        messages = response.json()
        
        if not messages:
            return "The sandbox is currently empty. There are no messages."
        
        # Format the messages so the LLM can easily read them (last 5 for context)
        formatted_history = "\n".join([f"[{msg['timestamp']}] {msg['agentName']}: {msg['content']}" for msg in messages[-5:]])
        return f"Recent messages in the sandbox:\n{formatted_history}"
    except Exception as e:
        return f"Error connecting to the sandbox API: {e}"

@tool("Post Message Tool")
def post_message_tool(message_content: str) -> str:
    """
    Posts a new message to the sandbox environment.
    Use this tool to communicate with other agents. 
    Provide the exact string you want to say as the argument.
    """
    payload = {
        "agentName": CURRENT_ACTIVE_AGENT_NAME, # Dynamically uses the active agent's name
        "content": message_content
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        response.raise_for_status()
        return "Message successfully posted to the sandbox."
    except Exception as e:
        return f"Failed to post message: {e}"

# --- Agent Factory ---

def create_sandbox_agent(name: str, role: str, backstory: str) -> Agent:
    """Factory function to dynamically create agents."""
    return Agent(
        role=role,
        goal=f"Participate naturally in the sandbox chat as {name}. Read the room, and reply maintaining your persona.",
        backstory=backstory,
        verbose=True, # Set to False if you don't want to see their internal thoughts in the terminal
        allow_delegation=False,
        llm=MODEL,
        tools=[fetch_messages_tool, post_message_tool]
    )

def create_interaction_task(agent: Agent) -> Task:
    """Creates a task prompting the agent to interact once."""
    return Task(
        description=(
            "1. First, use the 'Fetch Messages Tool' to read recent activity in the sandbox.\n"
            f"2. Analyze the conversation. If the sandbox is empty, introduce yourself as {agent.role}.\n"
            "3. If there are messages, decide on a short, relevant message to contribute to the discussion. "
            "Do NOT repeat what others have just said. Add your own unique perspective based on your backstory.\n"
            "4. Use the 'Post Message Tool' to send your final message."
        ),
        expected_output="A successful confirmation that a thoughtful message has been posted.",
        agent=agent
    )

# --- Define Your Agents ---

agent_alpha = create_sandbox_agent(
    name="Agent Alpha",
    role="The Optimistic Visionary",
    backstory="You are an AI that focuses on the positive potential of technology. You are enthusiastic, collaborative, and you always try to steer conversations toward creative solutions."
)

agent_beta = create_sandbox_agent(
    name="Agent Beta",
    role="The Skeptical Analyst",
    backstory="You are a highly logical AI. You question assumptions and look for potential flaws or ethical concerns. You are polite but very direct and analytical."
)

# You can easily add more agents here:
# agent_gamma = create_sandbox_agent("Agent Gamma", "The Joker", "You make sarcastic but helpful tech jokes.")

# Load them into a list for easy iteration
simulation_participants = [
    {"name": "Agent Alpha", "instance": agent_alpha},
    {"name": "Agent Beta",  "instance": agent_beta}
]

# --- Main Simulation Loop ---

def run_simulation(turns: int = 4, delay_seconds: int = 15):
    """
    Runs a continuous loop where agents take turns interacting.
    - turns: How many total messages will be sent.
    - delay_seconds: Time to wait between agents (the human reflection window).
    """
    global CURRENT_ACTIVE_AGENT_NAME
    
    print("=========================================")
    print("🚀 Starting Continuous Multi-Agent Sandbox")
    print("=========================================\n")
    
    for cycle in range(turns):
        # Pick the next agent in the list (Round Robin)
        participant = simulation_participants[cycle % len(simulation_participants)]
        current_agent_name = participant["name"]
        current_agent = participant["instance"]
        
        # Set the global variable so the Post Message Tool knows who is sending
        CURRENT_ACTIVE_AGENT_NAME = current_agent_name
        
        print(f"\n[{cycle + 1}/{turns}] 🔄 It is now {current_agent_name}'s turn to think...")
        
        # Create a fresh task for this specific turn
        task = create_interaction_task(current_agent)
        crew = Crew(
            agents=[current_agent],
            tasks=[task],
            process=Process.sequential,
        )
        
        # Execute the agent's turn
        crew.kickoff()
        
        print(f"✅ {current_agent_name} finished their turn.")
        
        # Wait before the next agent's turn unless it's the very last turn
        if cycle < turns - 1:
            print(f"⏳ Waiting {delay_seconds} seconds before the next interaction...\n")
            time.sleep(delay_seconds)

if __name__ == "__main__":
    # Clear the terminal for a clean start
    os.system('cls' if os.name == 'nt' else 'clear') 
    
    # Run the simulation for 6 turns, and wait 10 seconds between them
    run_simulation(turns=6, delay_seconds=10)
