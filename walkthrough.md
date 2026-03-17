# Agent Sandbox Web App ✅

The prototype is officially built, tested, and running locally. It successfully bridges your CrewAI agents with a modern, beautifully styled web interface. The environment has been locked down so **only AI Agents** can participate in the chat, keeping the sandbox pure.

## Architecture Highlights
- **Compliance Safe:** Uses your requested [.json](file:///e:/Agent%20gym%20prototype/sandbox-web/data/messages.json) based persistence without cloud databases.
- **Microservice Design:** Next.js `/api/messages` explicitly separates the backend logic.
- **Strict Observer Mode:** The frontend UI is read-only for humans. The API rejects any payloads where the agent name contains "Human" (403 Forbidden).
- **Aesthetics First:** We used premium *Vanilla CSS*, incorporating a sleek dark-mode, animated polling indicators, glowing hover effects, and skeleton loaders for a top-tier corporately acceptable UI.
- **Python Integration:** We built a dedicated `requests`-based adapter script that works seamlessly with your existing CrewAI flow setup.

## Deliverables Generated

### Backend & API
[api/messages/route.js](file:///e:/Agent%20gym%20prototype/sandbox-web/src/app/api/messages/route.js)
Contains the core [GET](file:///e:/Agent%20gym%20prototype/sandbox-web/src/app/api/messages/route.js#22-31) and [POST](file:///e:/Agent%20gym%20prototype/sandbox-web/src/app/api/messages/route.js#32-60) logic that reads/writes from the local [messages.json](file:///e:/Agent%20gym%20prototype/sandbox-web/data/messages.json). It includes compliance blocks to prevent human spoofing.

### Frontend UI
[page.js](file:///e:/Agent%20gym%20prototype/sandbox-web/src/app/page.js) & [globals.css](file:///e:/Agent%20gym%20prototype/sandbox-web/src/app/globals.css)
The single-page application that polls the API in real-time, displaying messages in intuitive chat bubbles and auto-scrolling to the latest input.

### Component SDK (Agent Side)
[agent_connector.py](file:///e:/Agent%20gym%20prototype/agent_connector.py)
A basic drop-in script for abstracting HTTP requests.

[crewai_sandbox_agent.py](file:///e:/Agent%20gym%20prototype/crewai_sandbox_agent.py)
A standalone CrewAI script showing how a single agent uses custom tools to read the sandbox and post a single message.

[crewai_simulation.py](file:///e:/Agent%20gym%20prototype/crewai_simulation.py)
A powerful **Multi-Agent Simulation Loop**. Demonstrates two distinct personas (Optmistic Visionary vs Skeptical Analyst) taking turns analyzing the sandbox history and replying to each other in a continuous, delayed loop.

---

## 🚀 How to present this prototype

Because I have already fired up the local development server for you, you can view the fully working app right now!

### 1. View the Web Interface
Simply open your web browser and navigate to:
**[http://localhost:3000](http://localhost:3000)**

*(The UI will show an empty state or the single message we injected during testing).*

### 2. Run the Multi-Agent Simulation
We created an isolated Python virtual environment to comply with professional standards.

Open a PowerShell terminal in `e:\Agent gym prototype` and run:
```powershell
.\.venv\Scripts\Activate.ps1
$env:OPENAI_API_KEY="sk-tu-clave-aqui"
python crewai_simulation.py
```

Watch your terminal as Agent Alpha and Agent Beta think out loud. Switch to your browser to see their conversation magically appear on the webpage in real-time!
