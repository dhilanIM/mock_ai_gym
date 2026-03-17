import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
import requests
import time

# --- Configuration ---
load_dotenv() # Loads variables from .env file explicitly
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "openai/gpt-4o-mini"

API_URL = "http://localhost:3000/api/messages"
AGENT_NAME = "CrewAI Agent"

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
        
        # Format the messages so the LLM can easily read them
        formatted_history = "\n".join([f"[{msg['timestamp']}] {msg['agentName']}: {msg['content']}" for msg in messages[-5:]]) # Get last 5 for context
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
        "agentName": AGENT_NAME,
        "content": message_content
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        response.raise_for_status()
        return "Message successfully posted to the sandbox."
    except Exception as e:
        return f"Failed to post message: {e}"

# --- Create the Agent ---

sandbox_agent = Agent(
    role="Friendly AI Observer",
    goal="Enter the sandbox, read the current conversation, and introduce yourself or reply to an existing interesting topic.",
    backstory=(
         "You are an AI assistant designed to participate in a multi-agent sandbox simulation. "
         "You are polite, observant, and concise. You like analyzing what others say and adding valuable insights."
    ),
    verbose=True,
    allow_delegation=False,
    llm=MODEL, # Direct LiteLLM model definition using variable
    tools=[fetch_messages_tool, post_message_tool]
)

# --- Define the Task ---

interact_task = Task(
    description=(
        "1. First, use the 'Fetch Messages Tool' to read recent activity in the sandbox.\n"
        "2. Analyze the conversation. If the sandbox is empty (no messages), introduce yourself as the first agent to join the sandbox.\n"
        "3. If there are already messages, decide on a short, polite, and relevant message to contribute to the ongoing discussion.\n"
        "4. Use the 'Post Message Tool' to send your message."
    ),
    expected_output="A successful confirmation that a thoughtful message has been posted to the sandbox.",
    agent=sandbox_agent
)

# --- Assemble the Crew ---

crew = Crew(
    agents=[sandbox_agent],
    tasks=[interact_task],
    process=Process.sequential,
)

# --- Run the Execution ---
if __name__ == "__main__":
    print(f"Starting CrewAI simulation. Agent: {AGENT_NAME}")
    print("WARNING: Make sure your Next.js server is running on localhost:3000")
    print("WARNING: Make sure OPENAI_API_KEY is set in your environment variables.\n")
    
    # Adding a small delay to simulate human-like pacing if desired
    time.sleep(2) 
    
    result = crew.kickoff()
    
    print("\n######################")
    print("CREW EXECUTION RESULT:")
    print("######################")
    print(result)
