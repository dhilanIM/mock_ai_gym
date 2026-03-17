import os
import time
import random
import argparse
import requests
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

# --- Configuration ---
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
MODEL = "openai/gpt-4o-mini"
API_URL = "http://localhost:3000/api/messages"

AGENT_NAME = "" # Will be set dynamically

# --- Custom Tools ---
@tool("Fetch Messages Tool")
def fetch_messages_tool() -> str:
    """Fetches the latest messages from the sandbox."""
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        messages = response.json()
        if not messages: return "The sandbox is currently empty."
        formatted_history = "\n".join([f"[{msg['timestamp']}] {msg['agentName']}: {msg['content']}" for msg in messages[-5:]])
        return f"Recent messages:\n{formatted_history}"
    except Exception as e:
        return f"Error connecting to api: {e}"

@tool("Post Message Tool")
def post_message_tool(message_content: str) -> str:
    """Posts a new message to the sandbox."""
    payload = {"agentName": AGENT_NAME, "content": message_content}
    try:
        requests.post(API_URL, json=payload, timeout=5)
        return "Message successfully posted."
    except Exception as e:
        return f"Failed to post: {e}"

# --- Direct API Fetcher (For the Loop Logic) ---
def get_latest_message_raw():
    """Reads the API directly without invoking the LLM, to check for state changes."""
    try:
        res = requests.get(API_URL, timeout=5)
        msgs = res.json()
        return msgs[-1] if msgs else None
    except:
        return None

# --- Main Node Loop ---
def run_autonomous_node(name, role, backstory, min_delay, max_delay):
    global AGENT_NAME
    AGENT_NAME = name
    
    print(f"\n=======================================================")
    print(f"🤖 Initializing Node: {AGENT_NAME}")
    print(f"🎭 Role: {role}")
    print(f"⏱️  Desync Delay: {min_delay}s to {max_delay}s")
    print(f"=======================================================\n")
    
    agent = Agent(
        role=role,
        goal=f"Participate in the sandbox chat as {name}. Read the conversation and reply naturally.",
        backstory=backstory,
        verbose=True,
        allow_delegation=False,
        llm=MODEL,
        tools=[fetch_messages_tool, post_message_tool]
    )

    while True:
        try:
            latest_msg = get_latest_message_raw()
            
            # Rule 1: Do not talk to yourself back-to-back
            if latest_msg and latest_msg.get("agentName") == AGENT_NAME:
                print(f"💤 [{time.strftime('%X')}] I was the last one to speak. Waiting for others...")
                time.sleep(10)
                continue
                
            # Rule 2: Wait a random amount of time (Jitter) to prevent collisions with other agents
            delay = random.randint(min_delay, max_delay)
            print(f"⏳ [{time.strftime('%X')}] Sandbox updated. Waiting {delay} seconds before deciding to act to avoid collisions...")
            time.sleep(delay)
            
            # Rule 3: Check if someone else spoke while we were waiting!
            current_latest = get_latest_message_raw()
            
            # If the messages don't match, it means another agent posted while we were asleep.
            if latest_msg != current_latest:
                print(f"⚠️ [{time.strftime('%X')}] Another agent spoke while I was waiting! Aborting my turn to read the new context.")
                continue # Restart the loop to read the new message
                
            # If we survived the wait and nobody else spoke, it is our turn!
            print(f"✅ [{time.strftime('%X')}] Coast is clear. {AGENT_NAME} is thinking...")
            
            task = Task(
                description=(
                    "1. Use 'Fetch Messages Tool' to read recent activity.\n"
                    f"2. Analyze context. If sandbox is empty, introduce yourself as {role}.\n"
                    "3. If there are messages, contribute briefly. Do NOT repeat what others said.\n"
                    "4. Use 'Post Message Tool' to send your output."
                ),
                expected_output="Confirmation of posted message.",
                agent=agent
            )
            
            Crew(agents=[agent], tasks=[task], process=Process.sequential).kickoff()
            
            print(f"🎉 [{time.strftime('%X')}] Turn completed!")
            
            # Wait a bit after talking to let the system breathe
            time.sleep(5)
            
        except KeyboardInterrupt:
            print(f"\n🛑 Node {AGENT_NAME} manually shut down.")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a single autonomous Agent Node.")
    parser.add_argument("--name", type=str, required=True, help="Name of the Agent (e.g., 'Agent Charlie')")
    parser.add_argument("--role", type=str, required=True, help="Role of the Agent (e.g., 'The Tech Guru')")
    parser.add_argument("--backstory", type=str, default="You are a helpful and polite AI.", help="The agent's personality.")
    parser.add_argument("--min", type=int, default=10, help="Minimum wait time in seconds to avoid collision")
    parser.add_argument("--max", type=int, default=25, help="Maximum wait time in seconds to avoid collision")
    
    args = parser.parse_args()
    run_autonomous_node(args.name, args.role, args.backstory, args.min, args.max)
