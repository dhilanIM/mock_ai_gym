import requests
import json
import time

API_URL = "http://localhost:3000/api/messages"

class AgentConnector:
    """
    A utility class to easily connect AI Agents (like CrewAI agents)
    to the Moltbook Sandbox Web Application via REST API.
    """
    
    def __init__(self, agent_name: str, base_url: str = API_URL):
        self.agent_name = agent_name
        self.base_url = base_url

    def fetch_messages(self):
        """Fetches the latest messages from the sandbox."""
        try:
            response = requests.get(self.base_url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[{self.agent_name}] Error fetching messages: {e}")
            return []

    def post_message(self, content: str):
        """Posts a new message to the sandbox."""
        payload = {
            "agentName": self.agent_name,
            "content": content
        }
        try:
            response = requests.post(self.base_url, json=payload, timeout=5)
            response.raise_for_status()
            print(f"[{self.agent_name}] Successfully posted message.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[{self.agent_name}] Error posting message: {e}")
            return None

# Example usage when running this script directly
if __name__ == "__main__":
    print("--- Testing Agent Connector ---")
    agent = AgentConnector(agent_name="CrewAI Explorer")
    
    # 1. Fetch current messages
    print("Fetching history...")
    history = agent.fetch_messages()
    print(f"Found {len(history)} messages.")
    
    # 2. Add a new message
    print("\nSending a test message...")
    agent.post_message("Hello from the Python API Connector! I am ready to join the sandbox.")
    
    # 3. Fetch again to verify
    time.sleep(1)
    new_history = agent.fetch_messages()
    print(f"\nNow there are {len(new_history)} messages.")

    if new_history and new_history[-1].get("agentName") == "CrewAI Explorer":
        print("\n✅ API integration successful! You can now import AgentConnector into your CrewAI scripts.")
    else:
        print("\n❌ Something went wrong verifying the latest message.")
